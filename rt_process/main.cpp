#include <iostream>
#include <fstream>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <cstring>

#include "pid.h"
#include "plant.h"
#include "timing.h"
#include "ipc.h"

constexpr int LOOP_HZ = 50;
constexpr long LOOP_PERIOD_US = 1000000 / LOOP_HZ;
constexpr int NUM_ITERATIONS = 5000;

PID pid;
ThermalPlant plant;

// Shared memory pointer
PIDParams* shm_pid = nullptr;
const char* SHM_FILE = "/tmp/pid_shm.bin";

// Initialize file backed mmap for PID parameters
void init_shared_memory() {
    int fd = open(SHM_FILE, O_RDWR | O_CREAT, 0666);
    if (fd == -1) {
        perror("open");
        exit(1);
    }

    if (ftruncate(fd, sizeof(PIDParams)) == -1) {
        perror("ftruncate");
        exit(1);
    }

    void* ptr = mmap(nullptr, sizeof(PIDParams),
                     PROT_READ | PROT_WRITE,
                     MAP_SHARED, fd, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }

    shm_pid = reinterpret_cast<PIDParams*>(ptr);

    // Initialize PID defaults
    shm_pid->Kp = 2.0;
    shm_pid->Ki = 0.5;
    shm_pid->Kd = 0.1;
    shm_pid->setpoint = 22.0;

    close(fd);
}

void* rt_loop(void*) {
    std::ofstream timing_log("timing_log.csv");
    timing_log << "iteration,period_us,exec_time_us,jitter_us\n";

    std::ofstream response_log("response_log.csv");
    response_log << "iteration,temperature,heater_output,Kp,Ki,Kd,setpoint\n";

    // Plant init
    plant_init(plant, 18.0, 10.0, 10.0, 5.0); // initial, ambient, gain, inertia
    pid_init(pid, shm_pid->Kp, shm_pid->Ki, shm_pid->Kd, 0.0, 1.0);

    double dt = 1.0 / LOOP_HZ;

    timespec prev_start{};
    bool first_iteration = true;

    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        timespec start{}, end{};
        clock_gettime(CLOCK_MONOTONIC, &start);

        // Update PID from file backed mmap
        pid.kp = shm_pid->Kp;
        pid.ki = shm_pid->Ki;
        pid.kd = shm_pid->Kd;
        double setpoint = shm_pid->setpoint;

        // PID + Plant update
        double heater = pid_update(pid, setpoint, plant.temperature, dt);
        double temp   = plant_update(plant, heater, dt);

        // Log response
        response_log << i << "," << temp << "," << heater << ","
             << pid.kp << "," << pid.ki << "," << pid.kd << "," << setpoint << std::endl;
        response_log.flush();

        // Dummy deterministic workload
        volatile int dummy = 0;
        for (int j = 0; j < 1000; ++j) dummy += j;

        clock_gettime(CLOCK_MONOTONIC, &end);

        // Timing measurement
        double exec_time_us = timespec_diff_us(start, end);
        if (!first_iteration) {
            double period_us = timespec_diff_us(prev_start, start);
            double jitter_us = period_us - LOOP_PERIOD_US;
            timing_log << i << "," << period_us << "," << exec_time_us << "," << jitter_us << "\n";
            timing_log.flush();
        } else {
            // Skip logging first iteration to avoid negative period/jitter
            first_iteration = false;
        }

        prev_start = start;

        // Sleep to maintain loop rate
        timespec sleep_time{};
        sleep_time.tv_sec  = 0;
        sleep_time.tv_nsec = LOOP_PERIOD_US * 1000;
        nanosleep(&sleep_time, nullptr);
    }

    timing_log.close();
    response_log.close();
    return nullptr;
}

int main() {
    init_shared_memory();

    pthread_t rt_thread;
    pthread_create(&rt_thread, nullptr, rt_loop, nullptr);
    pthread_join(rt_thread, nullptr);

    std::cout << "RT loop finished. Timing data written to timing_log.csv and response_log.csv\n";
    return 0;
}
