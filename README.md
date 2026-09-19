# Consumption Calculator

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jkremlacek&repository=consumption-calculator)

Home Assistant custom integration that calculates the cost of household electricity consumption using a 15-minute settlement window.

## Inputs

The integration expects:

- home consumption sensor (kW)
- shared network availability sensor (kW)
- optional home solar production sensor (kW)
- electricity price per kWh
- distribution price per kWh

## Pricing rules

- Shared network energy is used first when available.
- Home solar production is treated as zero-cost power and reduces the remaining demand.
- Remaining demand is supplied from the grid.
- Grid energy is charged as:
  - electricity price + distribution price
- Shared network energy is charged as:
  - distribution price only
- Local solar power is not charged.

## Example calculation

For a 15-minute window:

- `shared_used_kW = min(home_load_kW, shared_available_kW)`
- `home_solar_used_kW = min(home_load_kW - shared_used_kW, home_solar_kW)`
- `grid_used_kW = max(home_load_kW - shared_used_kW - home_solar_used_kW, 0)`

Then convert to kWh with a 0.25-hour window:

- `shared_energy_kwh = shared_used_kW * 0.25`
- `home_solar_energy_kwh = home_solar_used_kW * 0.25`
- `grid_energy_kwh = grid_used_kW * 0.25`

And compute cost:

- `shared_cost = shared_energy_kwh * distribution_price_per_kwh`
- `grid_cost = grid_energy_kwh * (electricity_price_per_kwh + distribution_price_per_kwh)`
- `total_cost = shared_cost + grid_cost`

## Install via HACS

Use the button at the top of this page after publishing the repository to GitHub. It opens the custom repository directly inside Home Assistant.

If you prefer to add it manually:

1. In Home Assistant, open HACS.
2. Go to Integrations.
3. Click the three-dot menu in the top-right.
4. Choose Custom repositories.
5. Add the repository URL in the form:
   - Repository: your GitHub repo URL, for example `https://github.com/your-user/consumption-calculator`
   - Category: Integration
6. Click Add.
7. Search for `Consumption Calculator` and install it.
8. Restart Home Assistant.

After installation, open Settings → Devices & Services → Add Integration and select Consumption Calculator.

## Manual installation

If you prefer not to use HACS, add the custom component to `custom_components/consumption_calculator` in your Home Assistant installation and configure it from the UI.

The integration exposes:

- `energy_from_grid_kW`
- `energy_from_shared_network_kW`
- `energy_from_home_solar_kW`
- `grid_energy_15min_kwh`
- `shared_energy_15min_kwh`
- `home_solar_energy_15min_kwh`
- `current_15min_cost`
- `current_cost_per_hour`

These values are designed to work with Home Assistant’s built-in charts and history graphs.

## Example chart over time

A practical dashboard can show the billed cost for each 15-minute slot together with the hourly equivalent:

- X axis: time, grouped in 15-minute intervals
- Y axis: cost in EUR
- series 1: `current_15min_cost` — actual settlement-window cost
- series 2: `current_cost_per_hour` — normalized equivalent for easier reading

Example trend:

```text
€
0.30 |                      ╭─────╮
0.25 |                  ╭────╯     ╰────╮
0.20 |        ╭─────╯                   ╰─╮
0.15 |   ╭────╯                            ╰────
0.10 |  ╰──────────────────────────────────────────
     +---------------------------------------------->
       08:00  08:15  08:30  08:45  09:00  09:15

Legend:
  current_15min_cost       = settlement-window billed cost
  current_cost_per_hour    = normalized display equivalent
```

This gives a clear view of price changes over time while still keeping the true billing basis on 15-minute calculation windows.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
