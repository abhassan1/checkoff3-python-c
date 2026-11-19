#include <stdint.h>

/* Sum n 64-bit integers stored contiguously in memory. */
int64_t sum_array(const int64_t *a, int64_t n) {
    int64_t total = 0;
    for (int64_t i = 0; i < n; i++) {
        total += a[i];
    }
    return total;
}

/* A trivial function: add two numbers. */
int64_t add(int64_t a, int64_t b) {
    return a + b;
}