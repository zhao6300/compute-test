# compute-test

本仓库用于做算子/内核层面的性能与结构验证，重点覆盖：

- Marlin 与 DeepGEMM MXFP4 的 kernel 基准对比；
- DeepSeek V4 / V4.1 Flash MoE expert 的结构与计算量估算；
- 128K token 输入下的 MoE 层整体算量估算；
- NCCL 通信基线（all2all 与 allreduce）；
- FlashInfer attention demo 与 KV cache 指标采集；
- CUDA `vector_add` 小样例编译与执行。

这里放的是轻量测试脚本，不包含完整模型推理、训练或端到端评测。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `compare_marlin_deepgemm_mxfp4.py` | 对比 vLLM Marlin（W4A16 MXFP4）与 DeepGEMM（W4A8 MXFP4）在给定 `M/N/K` 下的时间、算子和可选精度 |
| `simulate_moe_expert.py` | 通用 MoE expert 形状分解，输出 `gate_up` + `down` 的 MAC/FLOPs |
| `simulate_deepseek_v4_flash_expert.py` | 按 DeepSeek V4 Flash 近似结构模拟一个 routed expert |
| `simulate_deepseek_v41_flash_expert.py` | 按 DeepSeek V4.1 Flash 实际配置模拟一个 routed expert（`hidden=5120`、`moe_intermediate=2304`） |
| `simulate_deepseek_v41_flash_moe_128k.py` | 按 V4.1 Flash 配置模拟 128K token 输入下整个 MoE 层的算量 |
| `allreduce_and_all_to_all.py` | 本地 4 卡 NCCL 通信基线，用于模拟 EP all-to-all 与 TP all-reduce |
| `flashinfer_attention_demo.py` | FlashInfer attention 的小型演示/benchmark |
| `kv_cache_metrics.py` | 从 vLLM `/metrics` 读取 KV cache 与 prefix cache 指标 |
| `Makefile` / `vector_add.cu` | CUDA `vector_add` 小样例，`make` 可构建 |

## 环境

脚本默认使用 `/opt/venv`。当前环境已包含：

- CUDA 13.2 / torch 2.15.0a0
- vLLM 0.0.0+cu132
- DeepGEMM 2.6.1+local
- Transformers 5.16.1

也可以用 `/opt/venv/bin/python <script>` 显式启动任意脚本。

## 示例

### 1. 对比 Marlin 与 DeepGEMM MXFP4

```bash
./compare_marlin_deepgemm_mxfp4.py --shapes 4608,5120,1 5120,2304,1 --ms 131072 --mode kernel
```

该脚本会输出两组形状下 Marlin 和 DeepGEMM 的平均耗时、吞吐和可选精度指标。

### 2. 模拟 V4.1 Flash 单个 routed expert

```bash
./simulate_deepseek_v41_flash_expert.py --tokens 8 --json /tmp/v41_expert.json
```

### 3. 估算 128K token 下整个 MoE 层

```bash
./simulate_deepseek_v41_flash_moe_128k.py --tokens 131072 --json /tmp/v41_moe_128k.json
```

这里的 128K 按 `131072 tokens` 计算，并假设路由在 384 个 expert 上近似均匀。

按 `TP=2 × EP=2` 拆分时：

```bash
./simulate_deepseek_v41_flash_moe_128k.py \
  --tokens 131072 --tp-size 2 --ep-size 2 \
  --json /tmp/v41_moe_128k_tp_ep.json
```

### 4. 用 NCCL 测 EP all-to-all / TP all-reduce

```bash
timeout 120 env NCCL_COMM_ID=127.0.0.1:19810 \
  /opt/venv/bin/torchrun --nproc_per_node=4 \
  ./allreduce_and_all_to_all.py \
  --mode both --tokens 131072 --product 5120 \
  --iterations 1 --warmup 1 --timeout 60 \
  --json /tmp/comm_128k_5120.json
```

脚本会先绑定本地 GPU，再初始化 NCCL，并把本机通信约束固定到 `lo`、关闭 IB、开启阻塞等待和超时信号，避免误连远端网卡后长期挂起。

在 4 张本地卡、BF16、`131072 tokens × 5120 product` 下，`all2all` 约 `10ms`，`allreduce` 约 `5ms`。

同时交叉 `TP=2 × EP=2` 时可以运行：

```bash
timeout 120 env NCCL_COMM_ID=127.0.0.1:19810 \
  /opt/venv/bin/torchrun --nproc_per_node=4 \
  ./allreduce_and_all_to_all.py \
  --mode tp_ep --ep-size 2 --tp-size 2 \
  --tokens 8192 --product 5120 \
  --iterations 2 --warmup 1 --timeout 30
```

该模式会把 `tokens` 维度切给 EP、`features` 维度切给 TP。在 4 张本地卡、BF16、`8192 tokens × 5120 features` 下，`all2all` 约 `2.6ms`，`allreduce` 约 `1.2ms`。

### 5. 构建 CUDA `vector_add`

```bash
make
```

## 多尺寸 NCCL 基线

当前 `nccl_results.json` 记录了 4 张本地卡、BF16 下分别按 `8192/32768/131072 tokens × 2304/5120 features` 测出的 `all2all` 与 `allreduce` 时间。`all2all` 在测量范围内大致稳定在约 `1.0 GB/s` 的等效带宽，`allreduce` 约 `2.2 GB/s` 的等效带宽。

## 说明

仓库中的“模拟”主要用于估算形状、MAC/FLOPs 与 kernel 实现，不是完整 MoE 推理路径：

- 不执行真正的 top-k routing dispatch/combine；
- 不考虑动态路由导致的负载不均衡；
- `simulate_*_flash_expert*.py` 默认只实例化一个 expert，不是完整 MoE stack。
