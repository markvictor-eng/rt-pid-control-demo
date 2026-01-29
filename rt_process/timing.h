#pragma once
#include <cstdint>
#include <time.h>

struct TimingStats {
    double period_us;
    double exec_time_us;
    double jitter_us;
};

timespec timespec_add_us(const timespec& t, long us);
double timespec_diff_us(const timespec& start, const timespec& end);
