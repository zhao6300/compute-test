#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

#include <cuda_runtime.h>

#define CUDA_CHECK(call)                                                  \
    do {                                                                  \
        cudaError_t err__ = (call);                                       \
        if (err__ != cudaSuccess) {                                       \
            std::fprintf(stderr, "CUDA Error: %s at %s:%d\n",             \
                         cudaGetErrorString(err__), __FILE__, __LINE__);  \
            std::exit(EXIT_FAILURE);                                      \
        }                                                                 \
    } while (0)

enum class KernelKind {
    kFloat4,
    kFloat4Lb256,
    kFloat4Lb1024,
    kFloat4X4,
    kFloat4Mul,
    kFloat4X4Mul,
    kFloat4X4Streaming,
    kFloat4X4StreamingMul,
    kFloat4Streaming,
    kFloat4CacheBypass,
    kFloat4GridStrideMul,
    kFloat4GridStride,
};

__global__ void Float4Kernel(__restrict__ const float4* a,
                             __restrict__ const float4* b,
                             __restrict__ float4* c, int count) {
    const int index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index < count) {
        const float4 va = a[index];
        const float4 vb = b[index];
        c[index] = make_float4(va.x + vb.x, va.y + vb.y,
                               va.z + vb.z, va.w + vb.w);
    }
}

__global__ void __launch_bounds__(256)
Float4Lb256Kernel(__restrict__ const float4* a,
                  __restrict__ const float4* b,
                  __restrict__ float4* c, int count) {
    const int index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index < count) {
        const float4 va = __ldg(a + index);
        const float4 vb = __ldg(b + index);
        c[index] = make_float4(va.x + vb.x, va.y + vb.y,
                               va.z + vb.z, va.w + vb.w);
    }
}

__global__ void __launch_bounds__(1024)
Float4Lb1024Kernel(__restrict__ const float4* a,
                   __restrict__ const float4* b,
                   __restrict__ float4* c, int count) {
    const int index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index < count) {
        const float4 va = __ldg(a + index);
        const float4 vb = __ldg(b + index);
        c[index] = make_float4(va.x + vb.x, va.y + vb.y,
                               va.z + vb.z, va.w + vb.w);
    }
}

__global__ void Float4X4Kernel(__restrict__ const float4* a,
                               __restrict__ const float4* b,
                               __restrict__ float4* c, int count) {
    const int first = blockIdx.x * blockDim.x * 4 + threadIdx.x;
#pragma unroll
    for (int step = 0; step < 4; ++step) {
        const int index = first + step * blockDim.x;
        if (index < count) {
            const float4 va = __ldg(a + index);
            const float4 vb = __ldg(b + index);
            c[index] = make_float4(va.x + vb.x, va.y + vb.y,
                                   va.z + vb.z, va.w + vb.w);
        }
    }
}

__global__ void Float4MulKernel(__restrict__ const float4* a,
                                __restrict__ const float4* b,
                                __restrict__ float4* c, int count) {
    const int index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index < count) {
        const float4 va = a[index];
        const float4 vb = b[index];
        c[index] = make_float4(va.x * vb.x, va.y * vb.y,
                               va.z * vb.z, va.w * vb.w);
    }
}

__global__ void Float4X4MulKernel(__restrict__ const float4* a,
                                  __restrict__ const float4* b,
                                  __restrict__ float4* c, int count) {
    const int first = blockIdx.x * blockDim.x * 4 + threadIdx.x;
#pragma unroll
    for (int step = 0; step < 4; ++step) {
        const int index = first + step * blockDim.x;
        if (index < count) {
            const float4 va = __ldg(a + index);
            const float4 vb = __ldg(b + index);
            c[index] = make_float4(va.x * vb.x, va.y * vb.y,
                                   va.z * vb.z, va.w * vb.w);
        }
    }
}

__global__ void Float4X4StreamingKernel(__restrict__ const float4* a,
                                        __restrict__ const float4* b,
                                        __restrict__ float4* c,
                                        int count) {
    const int first = blockIdx.x * blockDim.x * 4 + threadIdx.x;
#pragma unroll
    for (int step = 0; step < 4; ++step) {
        const int index = first + step * blockDim.x;
        if (index < count) {
            const float4 va = __ldcs(a + index);
            const float4 vb = __ldcs(b + index);
            __stcs(c + index, make_float4(va.x + vb.x, va.y + vb.y,
                                          va.z + vb.z, va.w + vb.w));
        }
    }
}

__global__ void Float4X4StreamingMulKernel(__restrict__ const float4* a,
                                           __restrict__ const float4* b,
                                           __restrict__ float4* c,
                                           int count) {
    const int first = blockIdx.x * blockDim.x * 4 + threadIdx.x;
#pragma unroll
    for (int step = 0; step < 4; ++step) {
        const int index = first + step * blockDim.x;
        if (index < count) {
            const float4 va = __ldcs(a + index);
            const float4 vb = __ldcs(b + index);
            __stcs(c + index, make_float4(va.x * vb.x, va.y * vb.y,
                                          va.z * vb.z, va.w * vb.w));
        }
    }
}

__global__ void Float4StreamingKernel(__restrict__ const float4* a,
                                      __restrict__ const float4* b,
                                      __restrict__ float4* c, int count) {
    const int index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index < count) {
        const float4 va = __ldcs(a + index);
        const float4 vb = __ldcs(b + index);
        __stcs(c + index, make_float4(va.x + vb.x, va.y + vb.y,
                                      va.z + vb.z, va.w + vb.w));
    }
}

__global__ void Float4CacheBypassKernel(__restrict__ const float4* a,
                                        __restrict__ const float4* b,
                                        __restrict__ float4* c, int count) {
    const int index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index < count) {
        const float4 va = __ldcg(a + index);
        const float4 vb = __ldcg(b + index);
        __stcg(c + index, make_float4(va.x + vb.x, va.y + vb.y,
                                      va.z + vb.z, va.w + vb.w));
    }
}

__global__ void Float4GridStrideKernel(__restrict__ const float4* a,
                                       __restrict__ const float4* b,
                                       __restrict__ float4* c,
                                       long long count) {
    const long long stride =
        static_cast<long long>(blockDim.x) * gridDim.x;
    for (long long index = blockIdx.x * blockDim.x + threadIdx.x;
         index < count; index += stride) {
        const float4 va = a[index];
        const float4 vb = b[index];
        c[index] = make_float4(va.x + vb.x, va.y + vb.y,
                               va.z + vb.z, va.w + vb.w);
    }
}

__global__ void Float4GridStrideMulKernel(
    __restrict__ const float4* a, __restrict__ const float4* b,
    __restrict__ float4* c, long long count) {
    const long long stride =
        static_cast<long long>(blockDim.x) * gridDim.x;
    for (long long index = blockIdx.x * blockDim.x + threadIdx.x;
         index < count; index += stride) {
        const float4 va = a[index];
        const float4 vb = b[index];
        c[index] = make_float4(va.x * vb.x, va.y * vb.y,
                               va.z * vb.z, va.w * vb.w);
    }
}

void FillRandom(float* values, int count, float low, float high) {
    for (int i = 0; i < count; ++i) {
        values[i] = low + static_cast<float>(rand()) / RAND_MAX *
                         (high - low);
    }
}

bool Verify(const float* expected, const float* actual, int count) {
    for (int i = 0; i < count; ++i) {
        if (std::fabs(expected[i] - actual[i]) > 1e-5f) {
            std::fprintf(stderr,
                         "Mismatch at %d: expected %.6f, got %.6f\n",
                         i, expected[i], actual[i]);
            return false;
        }
    }
    return true;
}

double Median(std::vector<double>* values) {
    std::sort(values->begin(), values->end());
    const size_t count = values->size();
    if (count % 2 == 0) {
        return 0.5 * ((*values)[count / 2 - 1] + (*values)[count / 2]);
    }
    return (*values)[count / 2];
}

void LaunchKernel(KernelKind kind, int blocks, int threads,
                  const float* device_a, const float* device_b,
                  float* device_c, int element_count) {
    const float4* vector_a = reinterpret_cast<const float4*>(device_a);
    const float4* vector_b = reinterpret_cast<const float4*>(device_b);
    float4* vector_c = reinterpret_cast<float4*>(device_c);
    const int count = element_count / 4;

    switch (kind) {
        case KernelKind::kFloat4:
            Float4Kernel<<<blocks, threads>>>(vector_a, vector_b,
                                              vector_c, count);
            break;
        case KernelKind::kFloat4Lb256:
            Float4Lb256Kernel<<<blocks, threads>>>(vector_a, vector_b,
                                                   vector_c, count);
            break;
        case KernelKind::kFloat4Lb1024:
            Float4Lb1024Kernel<<<blocks, threads>>>(vector_a, vector_b,
                                                    vector_c, count);
            break;
        case KernelKind::kFloat4X4:
            Float4X4Kernel<<<blocks, threads>>>(vector_a, vector_b,
                                                vector_c, count);
            break;
        case KernelKind::kFloat4Mul:
            Float4MulKernel<<<blocks, threads>>>(vector_a, vector_b,
                                                 vector_c, count);
            break;
        case KernelKind::kFloat4X4Mul:
            Float4X4MulKernel<<<blocks, threads>>>(vector_a, vector_b,
                                                   vector_c, count);
            break;
        case KernelKind::kFloat4X4Streaming:
            Float4X4StreamingKernel<<<blocks, threads>>>(
                vector_a, vector_b, vector_c, count);
            break;
        case KernelKind::kFloat4X4StreamingMul:
            Float4X4StreamingMulKernel<<<blocks, threads>>>(
                vector_a, vector_b, vector_c, count);
            break;
        case KernelKind::kFloat4Streaming:
            Float4StreamingKernel<<<blocks, threads>>>(vector_a,
                                                       vector_b,
                                                       vector_c, count);
            break;
        case KernelKind::kFloat4CacheBypass:
            Float4CacheBypassKernel<<<blocks, threads>>>(
                vector_a, vector_b, vector_c, count);
            break;
        case KernelKind::kFloat4GridStride:
            Float4GridStrideKernel<<<blocks, threads>>>(
                vector_a, vector_b, vector_c,
                static_cast<long long>(count));
            break;
        case KernelKind::kFloat4GridStrideMul:
            Float4GridStrideMulKernel<<<blocks, threads>>>(
                vector_a, vector_b, vector_c,
                static_cast<long long>(count));
            break;
    }
    CUDA_CHECK(cudaGetLastError());
}

int BlocksRequired(KernelKind kind, int threads, int elements_per_thread,
                   int element_count, const cudaDeviceProp& prop) {
    const int vector4_count = element_count / 4;
    if (kind == KernelKind::kFloat4GridStride) {
        int blocks_per_sm = 0;
        CUDA_CHECK(cudaOccupancyMaxActiveBlocksPerMultiprocessor(
            &blocks_per_sm, Float4GridStrideKernel, threads, 0));
        const int blocks = prop.multiProcessorCount * blocks_per_sm;
        return blocks > 0 ? blocks : 1;
    }
    if (kind == KernelKind::kFloat4X4) {
        const int covered_by_block = threads * elements_per_thread * 4;
        return (vector4_count + covered_by_block - 1) / covered_by_block;
    }
    if (kind == KernelKind::kFloat4X4Mul ||
        kind == KernelKind::kFloat4X4StreamingMul) {
        const int covered_by_block = threads * elements_per_thread * 4;
        return (vector4_count + covered_by_block - 1) / covered_by_block;
    }
    if (kind == KernelKind::kFloat4X4Streaming) {
        const int covered_by_block = threads * elements_per_thread * 4;
        return (vector4_count + covered_by_block - 1) / covered_by_block;
    }
    if (elements_per_thread == 4) {
        const int covered_by_block = threads * elements_per_thread;
        return (element_count + covered_by_block - 1) / covered_by_block;
    }
    const int covered_by_block = threads * elements_per_thread;
    return (vector4_count + covered_by_block - 1) / covered_by_block;
}

double BenchmarkCase(KernelKind kind, int threads, int elements_per_thread,
                     const float* device_a, const float* device_b,
                     float* device_c, int element_count,
                     const cudaDeviceProp& prop, int iterations) {
    const int blocks =
        BlocksRequired(kind, threads, elements_per_thread, element_count,
                       prop);
    cudaEvent_t start;
    cudaEvent_t stop;
    CUDA_CHECK(cudaEventCreate(&start));
    CUDA_CHECK(cudaEventCreate(&stop));
    std::vector<double> times;
    times.reserve(iterations);

    for (int iteration = -1; iteration < iterations; ++iteration) {
        CUDA_CHECK(cudaEventRecord(start));
        LaunchKernel(kind, blocks, threads, device_a, device_b, device_c,
                     element_count);
        CUDA_CHECK(cudaEventRecord(stop));
        CUDA_CHECK(cudaEventSynchronize(stop));
        float elapsed_ms = 0.0f;
        CUDA_CHECK(cudaEventElapsedTime(&elapsed_ms, start, stop));
        if (iteration >= 0) {
            times.push_back(static_cast<double>(elapsed_ms));
        }
    }
    CUDA_CHECK(cudaEventDestroy(start));
    CUDA_CHECK(cudaEventDestroy(stop));
    return Median(&times);
}

int main(int argc, char** argv) {
    int element_count = 16 << 20;
    int iterations = 20;
    if (argc > 1) element_count = std::atoi(argv[1]);
    if (argc > 2) iterations = std::atoi(argv[2]);
    if (element_count <= 0 || element_count % 16 != 0 || iterations <= 0) {
        std::fprintf(stderr,
                     "Usage: %s [element_count divisible by 16] "
                     "[iterations]\n",
                     argv[0]);
        return EXIT_FAILURE;
    }

    int device_id = 0;
    cudaDeviceProp prop{};
    CUDA_CHECK(cudaGetDevice(&device_id));
    CUDA_CHECK(cudaGetDeviceProperties(&prop, device_id));
    CUDA_CHECK(cudaSetDeviceFlags(cudaDeviceScheduleBlockingSync));

    const size_t size = static_cast<size_t>(element_count) *
                        sizeof(float);
    float* host_a = nullptr;
    float* host_b = nullptr;
    float* device_a = nullptr;
    float* device_b = nullptr;
    float* device_c = nullptr;
    CUDA_CHECK(cudaMallocHost(&host_a, size));
    CUDA_CHECK(cudaMallocHost(&host_b, size));
    CUDA_CHECK(cudaMalloc(&device_a, size));
    CUDA_CHECK(cudaMalloc(&device_b, size));
    CUDA_CHECK(cudaMalloc(&device_c, size));
    std::vector<float> expected(element_count);
    std::vector<float> expected_mul(element_count);

    std::srand(42);
    FillRandom(host_a, element_count, -10.0f, 10.0f);
    FillRandom(host_b, element_count, -10.0f, 10.0f);
    for (int i = 0; i < element_count; ++i) {
        expected[i] = host_a[i] + host_b[i];
        expected_mul[i] = host_a[i] * host_b[i];
    }

    cudaEvent_t copy_start;
    cudaEvent_t copy_stop;
    CUDA_CHECK(cudaEventCreate(&copy_start));
    CUDA_CHECK(cudaEventCreate(&copy_stop));
    CUDA_CHECK(cudaMemcpyAsync(device_a, host_a, size,
                               cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpyAsync(device_b, host_b, size,
                               cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaEventRecord(copy_start));
    CUDA_CHECK(cudaMemcpyAsync(device_a, host_a, size,
                               cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpyAsync(device_b, host_b, size,
                               cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaEventRecord(copy_stop));
    CUDA_CHECK(cudaEventSynchronize(copy_stop));
    float copy_ms = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&copy_ms, copy_start, copy_stop));
    const double copy_gib_s =
        (2.0 * static_cast<double>(size)) /
        (static_cast<double>(copy_ms) * 1e-3) /
        (1024.0 * 1024.0 * 1024.0);

    struct Case {
        const char* name;
        KernelKind kind;
        int threads;
        int elements_per_thread;
    };
    const std::vector<Case> cases = {
        {"orig-like scalar", KernelKind::kFloat4, 256, 4},
        {"float4 vector", KernelKind::kFloat4, 256, 1},
        {"float4 vector", KernelKind::kFloat4, 512, 1},
        {"float4 vector", KernelKind::kFloat4, 1024, 1},
        {"float4 lb256", KernelKind::kFloat4Lb256, 256, 1},
        {"float4 lb1024", KernelKind::kFloat4Lb1024, 1024, 1},
        {"float4 x4 ldg", KernelKind::kFloat4X4, 256, 1},
        {"float4 x4 ldg", KernelKind::kFloat4X4, 512, 1},
        {"float4 x4 stream", KernelKind::kFloat4X4Streaming, 256, 1},
        {"float4 x4 stream", KernelKind::kFloat4X4Streaming, 512, 1},
        {"float4 stream", KernelKind::kFloat4Streaming, 256, 1},
        {"float4 stream", KernelKind::kFloat4Streaming, 512, 1},
        {"float4 bypass", KernelKind::kFloat4CacheBypass, 256, 1},
        {"float4 bypass", KernelKind::kFloat4CacheBypass, 512, 1},
        {"float4 grid-stride", KernelKind::kFloat4GridStride, 256, 1},
        {"float4 grid-stride", KernelKind::kFloat4GridStride, 512, 1},
        {"float4 grid-stride", KernelKind::kFloat4GridStride, 1024, 1},
        {"float4 mul", KernelKind::kFloat4Mul, 256, 1},
        {"float4 mul", KernelKind::kFloat4Mul, 512, 1},
        {"float4 x4 mul ldg", KernelKind::kFloat4X4Mul, 256, 1},
        {"float4 x4 mul ldg", KernelKind::kFloat4X4Mul, 512, 1},
        {"float4 x4 mul stream", KernelKind::kFloat4X4StreamingMul, 256, 1},
        {"float4 x4 mul stream", KernelKind::kFloat4X4StreamingMul, 512, 1},
        {"float4 mul grid-stride", KernelKind::kFloat4GridStrideMul, 256, 1},
        {"float4 mul grid-stride", KernelKind::kFloat4GridStrideMul, 512, 1},
        {"float4 mul grid-stride", KernelKind::kFloat4GridStrideMul, 1024, 1},
    };

    std::printf("GPU: %s, SMs: %d, CC: %d.%d, N: %d, iters: %d\n",
                prop.name, prop.multiProcessorCount, prop.major,
                prop.minor, element_count, iterations);
    std::printf("pinned H2D pair: %.3f ms, %.1f GiB/s\n",
                copy_ms, copy_gib_s);
    std::printf("%-24s %4s %12s %12s\n",
                "kernel", "blk", "median_ms", "GiB/s");

    for (const Case& item : cases) {
        const double median_ms =
            BenchmarkCase(item.kind, item.threads,
                          item.elements_per_thread, device_a, device_b,
                          device_c, element_count, prop, iterations);
        const double bytes = 3.0 * static_cast<double>(size);
        const double gib_s =
            bytes / (median_ms * 1e-3) / (1024.0 * 1024.0 * 1024.0);
        std::printf("%-24s %4d %12.4f %12.1f\n",
                    item.name, item.threads, median_ms, gib_s);
    }

    CUDA_CHECK(cudaMemset(device_c, 0, size));
    LaunchKernel(KernelKind::kFloat4, (element_count / 4 + 255) / 256, 256,
                 device_a, device_b, device_c, element_count);
    CUDA_CHECK(cudaMemcpy(host_a, device_c, size, cudaMemcpyDeviceToHost));
    if (!Verify(expected.data(), host_a, element_count)) {
        std::fprintf(stderr, "Verification FAILED!\n");
        return EXIT_FAILURE;
    }
    CUDA_CHECK(cudaMemset(device_c, 0, size));
    LaunchKernel(KernelKind::kFloat4X4Mul,
                 BlocksRequired(KernelKind::kFloat4X4Mul, 256, 1,
                                element_count, prop),
                 256, device_a, device_b, device_c, element_count);
    CUDA_CHECK(cudaMemcpy(host_a, device_c, size, cudaMemcpyDeviceToHost));
    if (!Verify(expected_mul.data(), host_a, element_count)) {
        std::fprintf(stderr, "Multiplication verification FAILED!\n");
        return EXIT_FAILURE;
    }
    std::printf("Vector add PASSED!\n");

    CUDA_CHECK(cudaEventDestroy(copy_start));
    CUDA_CHECK(cudaEventDestroy(copy_stop));
    CUDA_CHECK(cudaFree(device_a));
    CUDA_CHECK(cudaFree(device_b));
    CUDA_CHECK(cudaFree(device_c));
    CUDA_CHECK(cudaFreeHost(host_a));
    CUDA_CHECK(cudaFreeHost(host_b));
    return EXIT_SUCCESS;
}
