NVCC      := nvcc
NVCCFLAGS := -O3 -arch=native
TARGET    := vector_add

all: $(TARGET)

$(TARGET): vector_add.cu
	$(NVCC) $(NVCCFLAGS) -o $@ $< -lm

clean:
	rm -f $(TARGET)

.PHONY: all clean
