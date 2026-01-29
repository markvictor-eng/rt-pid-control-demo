import time
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import struct
import mmap

SHM_FILE = "/tmp/pid_shm.bin"

# PID object backed by file mmap
class PIDParams:
    def __init__(self, Kp=2.0, Ki=0.5, Kd=0.1, setpoint=22.0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint

# Open mmap
with open(SHM_FILE, "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)

def read_params():
    buf = mm[:32]
    Kp, Ki, Kd, sp = struct.unpack("dddd", buf)
    return PIDParams(Kp, Ki, Kd, sp)

def write_params(params):
    mm[:32] = struct.pack("dddd", params.Kp, params.Ki, params.Kd, params.setpoint)

# Live plot
RESPONSE_LOG = "../rt_process/build/response_log.csv"

plt.ion()
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, bottom=0.25)
temp_line, = ax.plot([], [], label="Temperature")
setpoint_line, = ax.plot([], [], label="Setpoint", linestyle='--')
ax.set_xlabel("Iteration")
ax.set_ylabel("Temperature (°C)")
ax.set_title("PID Temperature Control (Live)")
ax.set_ylim(0, 50)
ax.legend()

# Slider axes
axcolor = 'lightgoldenrodyellow'
ax_kp = plt.axes([0.1, 0.15, 0.3, 0.03], facecolor=axcolor)
ax_ki = plt.axes([0.1, 0.1, 0.3, 0.03], facecolor=axcolor)
ax_kd = plt.axes([0.1, 0.05, 0.3, 0.03], facecolor=axcolor)
ax_sp = plt.axes([0.6, 0.05, 0.3, 0.03], facecolor=axcolor)

slider_kp = Slider(ax_kp, 'Kp', 0.0, 5.0, valinit=1.0)
slider_ki = Slider(ax_ki, 'Ki', 0.0, 1.0, valinit=0.0)
slider_kd = Slider(ax_kd, 'Kd', 0.0, 1.0, valinit=0.0)
slider_sp = Slider(ax_sp, 'Setpoint', 0.0, 50.0, valinit=22.0)

# Callback to write slider values to mmap
def update(val):
    p = PIDParams(slider_kp.val, slider_ki.val, slider_kd.val, slider_sp.val)
    write_params(p)

slider_kp.on_changed(update)
slider_ki.on_changed(update)
slider_kd.on_changed(update)
slider_sp.on_changed(update)

iterations = []
temperatures = []
setpoints = []

def tail_csv(filename):
    with open(filename, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.05)
                continue
            yield line.strip()

log_lines = tail_csv(RESPONSE_LOG)
next(log_lines)

# Main
try:
    for line in log_lines:
        parts = line.split(",")
        if len(parts) < 7:
            continue
        try:
            iteration = int(parts[0])
            temp = float(parts[1])
            sp = float(parts[6])
        except ValueError:
            continue

        iteration = int(parts[0])
        temp = float(parts[1])
        sp = float(parts[6])

        iterations.append(iteration)
        temperatures.append(temp)
        setpoints.append(sp)

        temp_line.set_data(iterations, temperatures)
        setpoint_line.set_data(iterations, setpoints)

        ax.set_xlim(0, max(50, iteration+1))
        fig.canvas.draw()
        fig.canvas.flush_events()

except KeyboardInterrupt:
    print("Exiting...")
