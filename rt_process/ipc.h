#pragma once

struct PIDParams {
    double Kp;
    double Ki;
    double Kd;
    double setpoint;
};

// Initialize default PID values
inline void init_pid_params(PIDParams &params) {
    params.Kp = 2.0;
    params.Ki = 0.5;
    params.Kd = 0.1;
    params.setpoint = 22.0;
}
