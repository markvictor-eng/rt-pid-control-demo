#pragma once

struct ThermalPlant {
    double temperature;
    double ambient;
    double gain;
    double tau;
};

void plant_init(ThermalPlant& plant,
                double initial_temp,
                double ambient_temp,
                double gain,
                double tau);

double plant_update(ThermalPlant& plant,
                    double heater_power,
                    double dt);
