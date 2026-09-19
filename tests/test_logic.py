import unittest

from custom_components.consumption_calculator.logic import calculate_window
from custom_components.consumption_calculator.sensor import ENTITY_DESCRIPTIONS


class ConsumptionCalculatorLogicTests(unittest.TestCase):
    def test_grid_only_cost(self):
        result = calculate_window(
            home_load_kW=3.0,
            shared_available_kW=0.0,
            home_solar_kW=0.0,
            electricity_price_per_kwh=0.30,
            distribution_price_per_kwh=0.10,
        )

        self.assertAlmostEqual(result["shared_used_kW"], 0.0)
        self.assertAlmostEqual(result["grid_used_kW"], 3.0)
        self.assertAlmostEqual(result["shared_energy_kwh"], 0.0)
        self.assertAlmostEqual(result["grid_energy_kwh"], 0.75)
        self.assertAlmostEqual(result["total_cost"], 0.3)

    def test_shared_energy_reduces_grid_cost(self):
        result = calculate_window(
            home_load_kW=4.0,
            shared_available_kW=1.5,
            home_solar_kW=0.0,
            electricity_price_per_kwh=0.30,
            distribution_price_per_kwh=0.10,
        )

        self.assertAlmostEqual(result["shared_used_kW"], 1.5)
        self.assertAlmostEqual(result["grid_used_kW"], 2.5)
        self.assertAlmostEqual(result["shared_energy_kwh"], 0.375)
        self.assertAlmostEqual(result["grid_energy_kwh"], 0.625)
        self.assertAlmostEqual(result["total_cost"], 0.2875)

    def test_home_solar_avoids_grid_and_distribution_cost(self):
        result = calculate_window(
            home_load_kW=4.0,
            shared_available_kW=1.0,
            home_solar_kW=2.5,
            electricity_price_per_kwh=0.30,
            distribution_price_per_kwh=0.10,
        )

        self.assertAlmostEqual(result["shared_used_kW"], 1.0)
        self.assertAlmostEqual(result["home_solar_used_kW"], 2.5)
        self.assertAlmostEqual(result["grid_used_kW"], 0.5)
        self.assertAlmostEqual(result["total_cost"], 0.075)

    def test_home_solar_can_cover_all_load(self):
        result = calculate_window(
            home_load_kW=2.0,
            shared_available_kW=0.0,
            home_solar_kW=3.0,
            electricity_price_per_kwh=0.30,
            distribution_price_per_kwh=0.10,
        )

        self.assertAlmostEqual(result["home_solar_used_kW"], 2.0)
        self.assertAlmostEqual(result["grid_used_kW"], 0.0)
        self.assertAlmostEqual(result["total_cost"], 0.0)

    def test_cost_component_sensors_exist(self):
        sensor_keys = {entity.key for entity in ENTITY_DESCRIPTIONS}

        self.assertIn("current_15min_cost", sensor_keys)
        self.assertIn("current_shared_cost_15min", sensor_keys)
        self.assertIn("current_grid_cost_15min", sensor_keys)
        self.assertIn("current_cost_history_dataset", sensor_keys)


if __name__ == "__main__":
    unittest.main()
