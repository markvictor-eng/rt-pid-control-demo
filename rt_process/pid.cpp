#include "pid.h"

void pid_init(PID& pid,
              double kp,
              double ki,
              double kd,
              double output_min,
              double output_max)
{
    pid.kp = kp;
    pid.ki = ki;
    pid.kd = kd;

    pid.integral = 0.0;
    pid.prev_error = 0.0;

    pid.output_min = output_min;
    pid.output_max = output_max;
}

double pid_update(PID& pid,
                  double setpoint,
                  double measurement,
                  double dt)
{
    double error = setpoint - measurement;

    pid.integral += error * dt;
    double derivative = (error - pid.prev_error) / dt;

    double output =
        pid.kp * error +
        pid.ki * pid.integral +
        pid.kd * derivative;

    // Clamp output
    if (output > pid.output_max) output = pid.output_max;
    if (output < pid.output_min) output = pid.output_min;

    pid.prev_error = error;
    return output;
}
