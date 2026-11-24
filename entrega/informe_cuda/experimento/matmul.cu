// Benchmark used in the CUDA report: single-precision matrix multiplication
// C = A * B on the CPU (one thread), a naive CUDA kernel, a tiled CUDA kernel
// with shared memory and cuBLAS SGEMM. It also measures host<->device copies
// and a vector addition, to show when transfers dominate the run time.
//
// Build: nvcc -O3 -arch=native matmul.cu -lcublas -o matmul
// Run:   ./matmul > resultados.json
#include <cuda_runtime.h>
#include <cublas_v2.h>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

#define CHECK(call)                                                        \
  do {                                                                     \
    cudaError_t err_ = (call);                                                \
    if (err_ != cudaSuccess) {                                              \
      fprintf(stderr, "CUDA error %s at %s:%d\n", cudaGetErrorString(err_),   \
              __FILE__, __LINE__);                                         \
      exit(1);                                                             \
    }                                                                      \
  } while (0)

constexpr int TILE = 32;
constexpr int REPS = 10;

__global__ void matmul_naive(const float* A, const float* B, float* C, int n) {
  int row = blockIdx.y * blockDim.y + threadIdx.y;
  int col = blockIdx.x * blockDim.x + threadIdx.x;
  if (row < n && col < n) {
    float acc = 0.0f;
    for (int k = 0; k < n; ++k) acc += A[row * n + k] * B[k * n + col];
    C[row * n + col] = acc;
  }
}

__global__ void matmul_tiled(const float* A, const float* B, float* C, int n) {
  __shared__ float As[TILE][TILE];
  __shared__ float Bs[TILE][TILE];
  int row = blockIdx.y * TILE + threadIdx.y;
  int col = blockIdx.x * TILE + threadIdx.x;
  float acc = 0.0f;
  for (int t = 0; t < (n + TILE - 1) / TILE; ++t) {
    int ak = t * TILE + threadIdx.x;
    int bk = t * TILE + threadIdx.y;
    As[threadIdx.y][threadIdx.x] = (row < n && ak < n) ? A[row * n + ak] : 0.0f;
    Bs[threadIdx.y][threadIdx.x] = (bk < n && col < n) ? B[bk * n + col] : 0.0f;
    __syncthreads();
    for (int k = 0; k < TILE; ++k) acc += As[threadIdx.y][k] * Bs[k][threadIdx.x];
    __syncthreads();
  }
  if (row < n && col < n) C[row * n + col] = acc;
}

__global__ void vec_add(const float* a, const float* b, float* c, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) c[i] = a[i] + b[i];
}

static void cpu_matmul(const float* A, const float* B, float* C, int n) {
  for (int i = 0; i < n * n; ++i) C[i] = 0.0f;
  for (int i = 0; i < n; ++i)
    for (int k = 0; k < n; ++k) {
      float a = A[i * n + k];
      for (int j = 0; j < n; ++j) C[i * n + j] += a * B[k * n + j];
    }
}

static float max_rel_error(const std::vector<float>& x, const std::vector<float>& ref) {
  float worst = 0.0f;
  for (size_t i = 0; i < x.size(); ++i) {
    float d = std::fabs(x[i] - ref[i]) / (std::fabs(ref[i]) + 1e-3f);
    if (d > worst) worst = d;
  }
  return worst;
}

template <typename F>
static float time_gpu_ms(F launch) {
  cudaEvent_t s, e;
  CHECK(cudaEventCreate(&s));
  CHECK(cudaEventCreate(&e));
  launch();  // warm-up
  CHECK(cudaDeviceSynchronize());
  CHECK(cudaEventRecord(s));
  for (int r = 0; r < REPS; ++r) launch();
  CHECK(cudaEventRecord(e));
  CHECK(cudaEventSynchronize(e));
  float ms = 0.0f;
  CHECK(cudaEventElapsedTime(&ms, s, e));
  CHECK(cudaEventDestroy(s));
  CHECK(cudaEventDestroy(e));
  return ms / REPS;
}

int main() {
  cudaDeviceProp p;
  CHECK(cudaGetDeviceProperties(&p, 0));
  int rt = 0;
  CHECK(cudaRuntimeGetVersion(&rt));
  printf("{\n  \"gpu\": \"%s\", \"compute_capability\": \"%d.%d\", \"sms\": %d,\n",
         p.name, p.major, p.minor, p.multiProcessorCount);
  printf("  \"global_mem_mib\": %zu, \"shared_mem_per_block_kib\": %zu, \"warp_size\": %d,\n",
         p.totalGlobalMem >> 20, p.sharedMemPerBlock >> 10, p.warpSize);
  printf("  \"max_threads_per_block\": %d, \"cuda_runtime\": %d,\n", p.maxThreadsPerBlock, rt);
  printf("  \"reps\": %d, \"matmul\": [\n", REPS);

  cublasHandle_t h;
  cublasCreate(&h);
  const int sizes[] = {512, 1024, 2048};
  for (int si = 0; si < 3; ++si) {
    int n = sizes[si];
    size_t bytes = size_t(n) * n * sizeof(float);
    std::vector<float> A(n * n), B(n * n), Ccpu(n * n), Cgpu(n * n), Cref(n * n);
    srand(42);
    for (int i = 0; i < n * n; ++i) {
      A[i] = rand() / float(RAND_MAX) - 0.5f;
      B[i] = rand() / float(RAND_MAX) - 0.5f;
    }
    auto t0 = std::chrono::high_resolution_clock::now();
    cpu_matmul(A.data(), B.data(), Ccpu.data(), n);
    auto t1 = std::chrono::high_resolution_clock::now();
    double cpu_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    float *dA, *dB, *dC;
    CHECK(cudaMalloc(&dA, bytes));
    CHECK(cudaMalloc(&dB, bytes));
    CHECK(cudaMalloc(&dC, bytes));
    cudaEvent_t s, e;
    CHECK(cudaEventCreate(&s));
    CHECK(cudaEventCreate(&e));
    CHECK(cudaEventRecord(s));
    CHECK(cudaMemcpy(dA, A.data(), bytes, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(dB, B.data(), bytes, cudaMemcpyHostToDevice));
    CHECK(cudaEventRecord(e));
    CHECK(cudaEventSynchronize(e));
    float h2d_ms = 0.0f;
    CHECK(cudaEventElapsedTime(&h2d_ms, s, e));

    dim3 block(TILE, TILE), grid((n + TILE - 1) / TILE, (n + TILE - 1) / TILE);
    float naive_ms = time_gpu_ms([&] { matmul_naive<<<grid, block>>>(dA, dB, dC, n); });
    CHECK(cudaMemcpy(Cgpu.data(), dC, bytes, cudaMemcpyDeviceToHost));
    float naive_err = max_rel_error(Cgpu, Ccpu);

    float tiled_ms = time_gpu_ms([&] { matmul_tiled<<<grid, block>>>(dA, dB, dC, n); });
    CHECK(cudaMemcpy(Cgpu.data(), dC, bytes, cudaMemcpyDeviceToHost));
    float tiled_err = max_rel_error(Cgpu, Ccpu);

    const float alpha = 1.0f, beta = 0.0f;
    // Row-major C = A*B equals column-major C^T = B^T * A^T, so swap operands.
    float cublas_ms = time_gpu_ms([&] {
      cublasSgemm(h, CUBLAS_OP_N, CUBLAS_OP_N, n, n, n, &alpha, dB, n, dA, n, &beta, dC, n);
    });
    CHECK(cudaEventRecord(s));
    CHECK(cudaMemcpy(Cref.data(), dC, bytes, cudaMemcpyDeviceToHost));
    CHECK(cudaEventRecord(e));
    CHECK(cudaEventSynchronize(e));
    float d2h_ms = 0.0f;
    CHECK(cudaEventElapsedTime(&d2h_ms, s, e));
    float cublas_err = max_rel_error(Cref, Ccpu);

    printf("    {\"n\": %d, \"cpu_ms\": %.3f, \"naive_ms\": %.4f, \"tiled_ms\": %.4f, "
           "\"cublas_ms\": %.4f, \"h2d_ms\": %.4f, \"d2h_ms\": %.4f, "
           "\"naive_err\": %.2e, \"tiled_err\": %.2e, \"cublas_err\": %.2e}%s\n",
           n, cpu_ms, naive_ms, tiled_ms, cublas_ms, h2d_ms, d2h_ms, naive_err, tiled_err,
           cublas_err, si < 2 ? "," : "");
    cudaFree(dA);
    cudaFree(dB);
    cudaFree(dC);
    cudaEventDestroy(s);
    cudaEventDestroy(e);
  }
  cublasDestroy(h);

  // Vector addition: arithmetic is trivial, so the PCIe copies dominate.
  int n = 1 << 24;
  size_t bytes = size_t(n) * sizeof(float);
  std::vector<float> a(n, 1.0f), b(n, 2.0f), c(n);
  auto t0 = std::chrono::high_resolution_clock::now();
  for (int i = 0; i < n; ++i) c[i] = a[i] + b[i];
  auto t1 = std::chrono::high_resolution_clock::now();
  double cpu_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
  float *da, *db, *dc;
  CHECK(cudaMalloc(&da, bytes));
  CHECK(cudaMalloc(&db, bytes));
  CHECK(cudaMalloc(&dc, bytes));
  cudaEvent_t s, e;
  CHECK(cudaEventCreate(&s));
  CHECK(cudaEventCreate(&e));
  CHECK(cudaEventRecord(s));
  CHECK(cudaMemcpy(da, a.data(), bytes, cudaMemcpyHostToDevice));
  CHECK(cudaMemcpy(db, b.data(), bytes, cudaMemcpyHostToDevice));
  CHECK(cudaEventRecord(e));
  CHECK(cudaEventSynchronize(e));
  float h2d = 0.0f;
  CHECK(cudaEventElapsedTime(&h2d, s, e));
  float kern = time_gpu_ms([&] { vec_add<<<(n + 255) / 256, 256>>>(da, db, dc, n); });
  CHECK(cudaEventRecord(s));
  CHECK(cudaMemcpy(c.data(), dc, bytes, cudaMemcpyDeviceToHost));
  CHECK(cudaEventRecord(e));
  CHECK(cudaEventSynchronize(e));
  float d2h = 0.0f;
  CHECK(cudaEventElapsedTime(&d2h, s, e));
  bool ok = true;
  for (int i = 0; i < n; ++i) ok &= (c[i] == 3.0f);
  printf("  ],\n  \"vec_add\": {\"n\": %d, \"cpu_ms\": %.3f, \"kernel_ms\": %.4f, "
         "\"h2d_ms\": %.3f, \"d2h_ms\": %.3f, \"correct\": %s}\n}\n",
         n, cpu_ms, kern, h2d, d2h, ok ? "true" : "false");
  return 0;
}
