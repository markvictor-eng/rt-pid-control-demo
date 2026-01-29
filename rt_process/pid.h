#pragma once

struct PID {
    double kp;
    double ki;
    double kd;

    double integral;
    double prev_error;

    double output_min;
    double output_max;
};

void pid_init(PID& pid,
              double kp,
              double ki,
              double kd,
              double output_min,
              double output_max);

double pid_update(PID& pid,
                  double setpoint,
                  double measurement,
                  double dt);
