import time
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import csv

# Paths to logs
TIMING_LOG = "../rt_process/build/timing_log.csv"
RESPONSE_LOG = "../rt_process/build/response_log.csv"

# Constants
LOOP_HZ = 50
EXPECTED_PERIOD_US = 1_000_000 / LOOP_HZ
MAX_POINTS = 2000

# Deques for data
iterations = deque(maxlen=MAX_POINTS)
periods = deque(maxlen=MAX_POINTS)
exec_times = deque(maxlen=MAX_POINTS)
jitters = deque(maxlen=MAX_POINTS)
temps = deque(maxlen=MAX_POINTS)
setpoints = deque(maxlen=MAX_POINTS)

plt.ion()
fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
plt.subplots_adjust(hspace=0.4)

# Temperature plot
axs[0].set_title("Temperature vs Setpoint")
temp_line, = axs[0].plot([], [], label="Temperature", color="blue")
setpoint_line, = axs[0].plot([], [], label="Setpoint", color="orange", linestyle="--")
axs[0].set_ylabel("Temp (°C)")
axs[0].set_ylim(0, 50)
axs[0].legend()

# Period plot
axs[1].set_title("Loop Period (µs)")
period_line, = axs[1].plot([], [], label="Actual Period")
axs[1].axhline(EXPECTED_PERIOD_US, color="r", linestyle="--", label="Expected")
axs[1].set_ylabel("µs")
axs[1].legend()

# Execution time plot
axs[2].set_title("Execution Time (µs)")
exec_line, = axs[2].plot([], [], color="g")
axs[2].set_ylabel("µs")

# Jitter plot
axs[3].set_title("Jitter (µs)")
jitter_line, = axs[3].plot([], [], color="m")
axs[3].axhline(0, color="k", linestyle="--")
axs[3].set_ylabel("µs")
axs[3].set_xlabel("Iteration")

plt.tight_layout()

# Helper function to tail CSV
def tail_csv(filename):
    with open(filename, "r") as f:
        next(f)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.0005)
                continue
            yield line.strip()

timing_gen = tail_csv(TIMING_LOG)
response_gen = tail_csv(RESPONSE_LOG)

first_iteration = True

try:
    while True:
        # Read timing log
        timing_line = next(timing_gen)
        parts = timing_line.split(",")
        if len(parts) != 4:
            continue
        try:
            it = int(parts[0])
            period = float(parts[1])
            exec_t = float(parts[2])
            jitter = float(parts[3])
        except ValueError:
            continue

        # Skip first iteration to avoid negative period/jitter
        if first_iteration:
            first_iteration = False
            continue

        # Clamp negatives
        period = max(0.0, period)
        jitter = max(jitter, -period)  # optional safety

        # Read response log
        response_line = next(response_gen)
        parts_r = response_line.split(",")
        if len(parts_r) < 7:
            continue
        try:
            temp = float(parts_r[1])
            sp = float(parts_r[6])
        except ValueError:
            continue

        # Append data 
        iterations.append(it)
        periods.append(period)
        exec_times.append(exec_t)
        jitters.append(jitter)
        temps.append(temp)
        setpoints.append(sp)

        # Update plots 
        temp_line.set_data(iterations, temps)
        setpoint_line.set_data(iterations, setpoints)
        period_line.set_data(iterations, periods)
        exec_line.set_data(iterations, exec_times)
        jitter_line.set_data(iterations, jitters)

        # Update axes 
        xmax = max(50, iterations[-1])
        axs[0].set_xlim(0, xmax)
        axs[1].set_xlim(0, xmax)
        axs[2].set_xlim(0, xmax)
        axs[3].set_xlim(0, xmax)

        axs[0].set_ylim(0, 50)
        axs[1].set_ylim(min(periods)*0.98, max(periods)*1.02)
        axs[2].set_ylim(0, max(exec_times)*1.5)
        axs[3].set_ylim(min(jitters)*1.2, max(jitters)*1.2)

        fig.canvas.draw()
        fig.canvas.flush_events()

except KeyboardInterrupt:
    print("\nStopping timing visualizer...")

# RT Summary
if periods:
    print("\n=== RT Timing Summary ===")
    print(f"Expected period: {EXPECTED_PERIOD_US:.2f} µs")
    print(f"Avg period:      {np.mean(periods):.2f} µs")
    print(f"Max jitter:      {np.max(np.abs(jitters)):.2f} µs")
    print(f"Avg exec time:   {np.mean(exec_times):.2f} µs")
    print(f"Worst exec time: {np.max(exec_times):.2f} µs")

    # Write summary to CSV
    with open("timing_summary.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Expected period (µs)", "Avg period (µs)", "Max jitter (µs)",
                         "Avg exec time (µs)", "Worst exec time (µs)"])
        writer.writerow([EXPECTED_PERIOD_US, np.mean(periods), np.max(np.abs(jitters)),
                         np.mean(exec_times), np.max(exec_times)])
