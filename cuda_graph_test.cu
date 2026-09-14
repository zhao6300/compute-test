#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include <cuda_runtime.h>

#define CUDA_CHECK(call)                                                    \
    do {                                                                     \
        const cudaError_t check_err__ = (call);                              \
        if (check_err__ != cudaSuccess) {                                    \
            std::fprintf(stderr, "CUDA Error: %s at %s:%d\n",                \
                         cudaGetErrorString(check_err__), __FILE__,          \
                         __LINE__);                                          \
            std::exit(EXIT_FAILURE);                                         \
        }                                                                    \
    } while (false)

__global__ void AddKernel4(const char4* left, const char4* right,
                           char4* output, long long count) {
    const long long index =
        static_cast<long long>(blockIdx.x) * blockDim.x + threadIdx.x;
    if (index < count) {
        const char4 left_value = left[index];
        const char4 right_value = right[index];
        output[index] = make_char4(left_value.x + right_value.x,
                                   left_value.y + right_value.y,
                                   left_value.z + right_value.z,
                                   left_value.w + right_value.w);
    }
}

namespace {

bool CompareBuffers(const std::vector<char>& candidate,
                    const std::vector<char>& expected,
                    const std::vector<char>* left = nullptr,
                   const std::vector<char>* right = nullptr) {
    for (size_t index = 0; index < expected.size(); ++index) {
        if (candidate[index] != expected[index]) {
            std::printf("mismatch %zu: left=%d, right=%d, got=%d, "
                        "expected=%d, computed=%d\n",
                        index, left == nullptr ? 0 : left->at(index),
                        left == nullptr ? 0 : right->at(index),
                        candidate[index], expected[index],
                        static_cast<char>(left->at(index) + right->at(index)));
            return false;
        }
    }
    return true;
}

void PrepareHostBuffers(long long count, std::vector<char>& left,
                        std::vector<char>& right, std::vector<char>& result,
                        std::vector<char>& expected) {
    left.resize(count * sizeof(char4));
    right.resize(count * sizeof(char4));
    result.resize(count * sizeof(char4));
    expected.resize(count * sizeof(char4));

    const long long byte_count = static_cast<long long>(count * sizeof(char4));
    for (long long index = 0; index < byte_count; ++index) {
        left[index] = static_cast<char>((index * 7) % 128);
        right[index] = static_cast<char>((index * 11) % 128);
        const int sum =
            static_cast<int>(left[index]) + static_cast<int>(right[index]);
        expected[index] = static_cast<char>(sum & 0xff);
    }
}

void LaunchBatch(cudaStream_t stream, const char4* device_left,
                 const char4* device_right, char4* device_result,
                 long long count, int blocks, int launches) {
    for (int launch = 0; launch < launches; ++launch) {
        AddKernel4<<<blocks, 128, 0, stream>>>(device_left, device_right,
                                                device_result, count);
    }
}

void BuildCapturedGraph(cudaStream_t stream, const char4* device_left,
                        const char4* device_right, char4* device_result,
                        long long count, int blocks, int launches,
                        cudaGraph_t* graph, cudaGraphExec_t* graph_exec) {
    cudaStreamBeginCapture(stream, cudaStreamCaptureModeThreadLocal);
    for (int launch = 0; launch < launches; ++launch) {
        AddKernel4<<<blocks, 128, 0, stream>>>(device_left, device_right,
                                                device_result, count);
    }
    cudaStreamEndCapture(stream, graph);
    cudaGraphInstantiate(graph_exec, *graph, nullptr, nullptr, 0);
}

float MedianTime(cudaEvent_t start, cudaEvent_t stop) {
    float elapsed = 0.0f;
    cudaEventSynchronize(stop);
    cudaEventElapsedTime(&elapsed, start, stop);
    return elapsed;
}

}  // namespace

int main(int argc, char** argv) {
    long long count = 8192;
    int iterations = 24;
    int launches = 8;

    for (int arg = 1; arg < argc; ++arg) {
        if ((std::strcmp(argv[arg], "--count") == 0) && arg + 1 < argc) {
            count = std::atoll(argv[++arg]);
        } else if ((std::strcmp(argv[arg], "--iterations") == 0) &&
                   arg + 1 < argc) {
            iterations = std::atoi(argv[++arg]);
        } else if ((std::strcmp(argv[arg], "--launches") == 0) &&
                   arg + 1 < argc) {
            launches = std::atoi(argv[++arg]);
        } else {
            std::fprintf(stderr,
                         "Usage: %s [--count N] [--iterations N] "
                         "[--launches N]\n",
                         argv[0]);
            return EXIT_FAILURE;
        }
    }

    if (count < 128 || iterations <= 0 || launches <= 0 || count % 4 != 0) {
        std::fprintf(stderr,
                     "count must be a positive multiple of 4; "
                     "iterations and launches must be positive\n");
        return EXIT_FAILURE;
    }

    int device = 0;
    CUDA_CHECK(cudaGetDevice(&device));
    cudaDeviceProp props;
    CUDA_CHECK(cudaGetDeviceProperties(&props, device));

    cudaStream_t stream;
    CUDA_CHECK(cudaStreamCreate(&stream));
    char4* device_left = nullptr;
    char4* device_right = nullptr;
    char4* device_result = nullptr;
    const size_t bytes = static_cast<size_t>(count * sizeof(char4));
    CUDA_CHECK(cudaMalloc(&device_left, bytes));
    CUDA_CHECK(cudaMalloc(&device_right, bytes));
    CUDA_CHECK(cudaMalloc(&device_result, bytes));

    std::vector<char> host_left;
    std::vector<char> host_right;
    std::vector<char> host_result;
    std::vector<char> expected;
    PrepareHostBuffers(count, host_left, host_right, host_result, expected);
    std::printf("buffers: left[0]=%d, right[0]=%d, expected[0]=%d\n",
                static_cast<int>(host_left[0]),
                static_cast<int>(host_right[0]),
                static_cast<int>(expected[0]));
    CUDA_CHECK(cudaMemcpy(device_left, host_left.data(), bytes,
                          cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(device_right, host_right.data(), bytes,
                          cudaMemcpyHostToDevice));

    const int blocks = static_cast<int>((count + 127) / 128);
    cudaGraph_t graph = nullptr;
    cudaGraphExec_t graph_exec = nullptr;
    float direct_median = 0.0f;
    float graph_median = 0.0f;

    auto run_direct = [&]() -> bool {
        AddKernel4<<<blocks, 128, 0, stream>>>(device_left, device_right,
                                                device_result, count);
        CUDA_CHECK(cudaStreamSynchronize(stream));
        CUDA_CHECK(cudaMemcpy(host_result.data(), device_result, bytes,
                              cudaMemcpyDeviceToHost));
        return CompareBuffers(host_result, expected, &host_left, &host_right);
    };

    auto run_graph = [&]() -> bool {
        CUDA_CHECK(cudaGraphLaunch(graph_exec, stream));
        CUDA_CHECK(cudaStreamSynchronize(stream));
        CUDA_CHECK(cudaMemcpy(host_result.data(), device_result, bytes,
                              cudaMemcpyDeviceToHost));
        return CompareBuffers(host_result, expected, &host_left, &host_right);
    };

    if (!run_direct()) {
        std::fprintf(stderr, "Direct stream launch verification FAILED\n");
        return EXIT_FAILURE;
    }

    BuildCapturedGraph(stream, device_left, device_right, device_result, count,
                       blocks, launches, &graph, &graph_exec);
    const cudaError_t graph_error = cudaGetLastError();
    if (graph_error != cudaSuccess) {
        std::fprintf(stderr, "CUDA graph capture FAILED: %s\n",
                     cudaGetErrorString(graph_error));
        return EXIT_FAILURE;
    }
    if (!run_graph()) {
        std::fprintf(stderr, "CUDA graph launch verification FAILED\n");
        return EXIT_FAILURE;
    }

    for (int warmup = 0; warmup < 3; ++warmup) {
        LaunchBatch(stream, device_left, device_right, device_result, count,
                    blocks, launches);
    }
    CUDA_CHECK(cudaStreamSynchronize(stream));

    cudaEvent_t direct_start;
    cudaEvent_t direct_stop;
    cudaEvent_t graph_start;
    cudaEvent_t graph_stop;
    CUDA_CHECK(cudaEventCreate(&direct_start));
    CUDA_CHECK(cudaEventCreate(&direct_stop));
    CUDA_CHECK(cudaEventCreate(&graph_start));
    CUDA_CHECK(cudaEventCreate(&graph_stop));

    for (int iteration = 0; iteration < iterations; ++iteration) {
        CUDA_CHECK(cudaEventRecord(direct_start, stream));
        LaunchBatch(stream, device_left, device_right, device_result, count,
                    blocks, launches);
        CUDA_CHECK(cudaEventRecord(direct_stop, stream));
        direct_median += MedianTime(direct_start, direct_stop);
    }
    direct_median /= static_cast<float>(iterations);

    for (int warmup = 0; warmup < 3; ++warmup) {
        CUDA_CHECK(cudaGraphLaunch(graph_exec, stream));
    }
    CUDA_CHECK(cudaStreamSynchronize(stream));
    for (int iteration = 0; iteration < iterations; ++iteration) {
        CUDA_CHECK(cudaEventRecord(graph_start, stream));
        CUDA_CHECK(cudaGraphLaunch(graph_exec, stream));
        CUDA_CHECK(cudaEventRecord(graph_stop, stream));
        graph_median += MedianTime(graph_start, graph_stop);
    }
    graph_median /= static_cast<float>(iterations);

    const double saved =
        100.0 * (1.0 - static_cast<double>(graph_median) / direct_median);
    std::printf("GPU: %s, elements: %lld, launches per batch: %d, "
                "iterations: %d\n",
                props.name, count, launches, iterations);
    std::printf("stream:  %.6f ms/batch\n", direct_median);
    std::printf("graph:   %.6f ms/batch\n", graph_median);
    std::printf("graph saved: %s%.2f%% vs stream\n",
                saved < 0.0 ? "-" : "", std::abs(saved));
    std::printf("direct and graph vector add PASSED\n");

    CUDA_CHECK(cudaEventDestroy(graph_stop));
    CUDA_CHECK(cudaEventDestroy(graph_start));
    CUDA_CHECK(cudaEventDestroy(direct_stop));
    CUDA_CHECK(cudaEventDestroy(direct_start));
    CUDA_CHECK(cudaGraphExecDestroy(graph_exec));
    CUDA_CHECK(cudaGraphDestroy(graph));
    CUDA_CHECK(cudaStreamDestroy(stream));
    CUDA_CHECK(cudaFree(device_left));
    CUDA_CHECK(cudaFree(device_right));
    CUDA_CHECK(cudaFree(device_result));
    return EXIT_SUCCESS;
}
