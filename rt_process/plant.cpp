#include "plant.h"

void plant_init(ThermalPlant& plant,
                double initial_temp,
                double ambient_temp,
                double gain,
                double tau)
{
    plant.temperature = initial_temp;
    plant.ambient = ambient_temp;
    plant.gain = gain;
    plant.tau = tau;
}

double plant_update(ThermalPlant& plant,
                    double heater_power,
                    double dt)
{
    double dTdt =
        (plant.gain * heater_power -
         (plant.temperature - plant.ambient)) / plant.tau;

    plant.temperature += dTdt * dt;
    return plant.temperature;
}
