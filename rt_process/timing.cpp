#include "timing.h"

timespec timespec_add_us(const timespec& t, long us) {
    timespec out = t;
    out.tv_nsec += us * 1000;
    while (out.tv_nsec >= 1e9) {
        out.tv_nsec -= 1e9;
        out.tv_sec += 1;
    }
    return out;
}

double timespec_diff_us(const timespec& start, const timespec& end) {
    double sec = end.tv_sec - start.tv_sec;
    double nsec = end.tv_nsec - start.tv_nsec;
    return sec * 1e6 + nsec / 1e3;
}
