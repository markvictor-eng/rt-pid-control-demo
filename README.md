# RT PID Control Demo

**Author:** Mark Eid
**Date:** Jan 2026  

This repository contains a demonstration of a PID control loop implemented in C++ with Python utilities for live monitoring, tuning, and timing analysis. The system was designed to demonstrate real-time control, parameter tuning, and timing determinism.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Architecture](#architecture)  
3. [Build & Run Instructions](#build--run-instructions)  
4. [Python Utilities](#python-utilities)  
5. [Timing and Determinism](#timing-and-determinism)  
6. [Caveats](#caveats)  
7. [Results](#results)  

---

## Project Overview

This project implements:

- **C++ Real-Time Loop (`main.cpp`)**
  - PID controller regulating a simulated thermal plant
  - File backed shared memory (`mmap`) for live parameter updates
  - Timing instrumentation to measure loop period, execution time, and jitter
- **Python PID Client (`pid_client.py`)**
  - Interactive GUI with sliders to set/get PID parameters (`Kp`, `Ki`, `Kd`, `setpoint`)
  - Live temperature vs setpoint plot
- **Python Timing Visualizer (`pid_visualizer.py`)**
  - Live plots for:
    - Temperature vs Setpoint
    - Loop Period
    - Execution Time
    - Jitter
  - Computes summary statistics (average, max, worst-case)

This setup demonstrates:

- PID response to parameter and setpoint changes in steady state  
- Soft real time behavior of a periodic control loop  
- Timing determinism and jitter during steady operation and parameter updates  

---

## Architecture

- **C++ RT Loop**
  - Runs at a fixed rate (50 Hz)
  - Reads PID parameters from a memory-mapped file
  - Logs timing and plant response to CSV
- **Python PID Client**
  - Writes PID parameters to shared memory
  - Displays live temperature and setpoint
- **Python Visualizer**
  - Tails CSV logs
  - Displays timing behavior and control response

---

## Build & Run Instructions

### Requirements

- macOS or Linux (POSIX compliant)
- C++ compiler (`clang++` or `g++`)
- Python 3.x
- Python packages:
  - `matplotlib`
  - `numpy`

---

### Build the RT Process

```bash
cd rt_process
make clean && make
```

---

### Run the RT Control Loop
`./rt_loop`

This will generate:
- timing_log.csv
- response_log.csv

---

### Run the Python PID Client (Live Tuning)
```
cd python_client
python3 pid_client.py
```
- Adjust Kp, Ki, Kd, and setpoint using sliders
- Observe live temperature response

---

### Run the Timing Visualizer
`python3 pid_visualizer.py`

- Displays live plots for:
  - Temperature vs Setpoint
  - Loop Period
  - Execution Time
  - Jitter
- Prints a timing summary when stopped

---

### Python Utilities
pid_client.py
- Uses mmap to communicate PID parameters to the RT process
- Provides real time interactive tuning
- Confirms control response visually

pid_visualizer.py
- Continuously tails RT logss
- Demonstrates time determinism and jitter
- Produces numerical summaries suitable for reporting

---

### Timing and Determinism
- Target loop frequency: 50 Hz
- Expected period: 20,000 µs
Metrics captured:
- Actual loop period
- Execution time per iteration
- Jitter (difference from expected period)
Timing behavior is shown:
- In steady-state operation
- While changing PID gains and setpoints at run time

---

### Caveats
- This implementation is soft real time.
- The demo was developed and tested on macOS, which is not a true RTOS.
- Timing behavior may differ on:
  - Linux with PREEMPT_RT
  - Embedded RTOS environments
- Shared memory via file backed mmap is used to simulate IPC.
  - Embedded systems may use message queues, shared RAM, or hardware registers.
- The thermal plant is simulated. Real hardware dynamics will vary.

---

### Results
- Control Performance
  - PID stabilizes temperature at the target setpoint
  - System responds smoothly to runtime parameter changes
- Timing Performance
  - Loop period remains near the target
  - Execution time remains low and consistent
  - Jitter is measurable and visualized for analysis

---

### Example timing summary from a run:
- Expected period: 20000 µs
- Avg period:      ~24,000 µs
- Max jitter:      ~20,000 µs
- Avg exec time:   ~10 µs
- Worst exec time: ~850 µs
