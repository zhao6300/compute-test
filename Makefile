NVCC      := nvcc
NVCCFLAGS := -O3 -arch=native
TARGETS   := vector_add cuda_graph_test

all: $(TARGETS)

vector_add: vector_add.cu
	$(NVCC) $(NVCCFLAGS) -o $@ $< -lm

cuda_graph_test: cuda_graph_test.cu
	$(NVCC) $(NVCCFLAGS) -o $@ $< -lm

clean:
	rm -f $(TARGETS)

check: $(TARGETS)
	./vector_add 6144 200
	./cuda_graph_test --count 8192 --launches 8 --iterations 24

.PHONY: all clean check
