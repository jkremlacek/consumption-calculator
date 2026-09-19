# Home Assistant custom integration plan

## Goal

Create a custom Home Assistant integration that combines:

1. a home consumption sensor in kW
2. a network-sharing energy availability sensor in kW
3. an optional home solar production sensor in kW
4. two configured pricing constants:
   - electricity price per kWh
   - distribution price per kWh

and computes the effective electricity cost based on how much energy is drawn from the grid, the sharing network, and the home’s own solar production.

## Business rules

- The company calculates usage in 15-minute windows.
- The energy offered by the sharing network and the energy consumed by the home are evaluated within the same 15-minute time bucket.
- If energy is taken from the home grid, the total price is:
  - electricity price + distribution price
- If energy is taken from the external solar producer over the sharing network, only:
  - distribution price applies
- If energy is produced by the home’s own solar system, it should reduce the cost by avoiding both electricity and distribution charges for that portion of load.
- If the optional home solar sensor is not configured, the logic falls back to the previous grid + sharing model.
- The integration should calculate the split between the sources and estimate the total cost for the current 15-minute interval.

## Core calculation

For a 15-minute measurement window:

- `home_load_kW` = actual energy consumption of the home in that window
- `shared_available_kW` = amount of external shared energy available in that same window
- `home_solar_kW` = optional local solar production available to cover household load in that same window
- `shared_used_kW = min(home_load_kW, shared_available_kW)`
- `remaining_after_shared_kW = max(home_load_kW - shared_used_kW, 0)`
- `home_solar_used_kW = min(remaining_after_shared_kW, home_solar_kW)` when the home solar sensor is configured
- `grid_used_kW = max(home_load_kW - shared_used_kW - home_solar_used_kW, 0)`

This is a power-rate view for a period; since the company settles in 15-minute intervals, the actual energy values are:

- `shared_energy_kWh = shared_used_kW * 0.25`
- `home_solar_energy_kWh = home_solar_used_kW * 0.25` when configured
- `grid_energy_kWh = grid_used_kW * 0.25`

The cost for the 15-minute window is then:

- `shared_cost = shared_energy_kWh * distribution_price_per_kWh`
- `home_solar_cost = 0`
- `grid_cost = grid_energy_kWh * (electricity_price_per_kWh + distribution_price_per_kWh)`
- `total_cost = shared_cost + grid_cost`

In other words, local solar energy is treated as a zero-cost source for the household, reducing the amount that must be supplied by the grid or the sharing network.

If a sensor needs a rate-style output for display, it can still be expressed as a per-hour equivalent, but the underlying calculation must be based on 15-minute energy totals.

## Home Assistant design

### Integration type

Use a standard custom integration structure for Home Assistant, with:

- manifest metadata
- setup entry flow
- config entry for user-supplied sensor entity IDs and pricing values
- coordinator using `DataUpdateCoordinator` or similar polling pattern
- sensor entities that expose computed values

### Entities to configure

The user will provide:

- `consumption_sensor_entity_id` — actual home consumption in kW
- `sharing_sensor_entity_id` — available energy from the sharing network in kW
- `home_solar_sensor_entity_id` — optional local solar production in kW that reduces household cost
- `electricity_price_per_kwh` — numeric constant
- `distribution_price_per_kwh` — numeric constant

### Computed sensors to expose

Planned sensors:

1. `energy_from_grid_kW` — power supplied from the grid in the current measurement snapshot
2. `energy_from_shared_network_kW` — power supplied from the sharing network in the current measurement snapshot
3. `energy_from_home_solar_kW` — power supplied by the optional home solar sensor in the current snapshot
4. `grid_energy_15min_kwh` — grid energy used during the current 15-minute settlement period
5. `shared_energy_15min_kwh` — shared-network energy used during the current 15-minute settlement period
6. `home_solar_energy_15min_kwh` — home solar energy used during the current 15-minute settlement period
7. `current_15min_cost` — cost for the current 15-minute window
8. `current_cost_per_hour` — per-hour equivalent value for human-friendly display and chart trend analysis
9. optional `source_mix_percentage` — share of home load coming from grid vs shared network vs solar

These should all be standard Home Assistant numeric sensors so they can be visualized with built-in charts, history graphs, and statistics cards without custom widget code.

## File layout

The implementation will likely follow this structure:

- `manifest.json`
- `__init__.py`
- `const.py`
- `coordinator.py`
- `sensor.py`
- `config_flow.py`
- `strings.json`
- `translations/en.json` and any other localization files required
- optional `services.yaml` if actions are needed

## Configuration flow approach

The integration should support either:

- a simple YAML config, or
- UI configuration via config flow where the user selects the two sensor entities and enters the two price constants

The UI flow is cleaner for Home Assistant and should be preferred unless there is a strong reason to use YAML only.

## Validation plan

After implementation, verify with a small set of representative inputs:

1. no shared energy available, no home solar, home load 3.0 kW
   - expected grid energy = 3.0 kW
   - expected total cost = 3.0 \* (electricity + distribution)
2. shared energy available equals full home load, no home solar, home load 3.0 kW
   - expected shared energy = 3.0 kW
   - expected grid energy = 0
   - expected total cost = 3.0 \* distribution
3. partial overlap, home load 4.0 kW and shared available 1.5 kW, no home solar
   - expected shared energy = 1.5 kW
   - expected grid energy = 2.5 kW
   - expected total cost = 1.5 _ distribution + 2.5 _ (electricity + distribution)
4. home solar covers part of the load, home load 4.0 kW, shared available 1.0 kW, home solar 2.5 kW
   - expected shared energy = 1.0 kW
   - expected home solar used = 2.5 kW
   - expected grid energy = 0.5 kW
   - expected total cost = 1.0 _ distribution + 0.5 _ (electricity + distribution)
   - no charge applied to the 2.5 kW covered by self-produced solar
5. home solar exceeds home load, home load 2.0 kW, solar 3.0 kW, shared 0
   - expected home solar used = 2.0 kW
   - expected grid energy = 0
   - expected total cost = 0

The optional home solar sensor should be treated as a zero-cost source reducing the load before the grid and sharing network are considered.

## Assumptions

- sensor values are read as kW
- prices are expressed in currency per kWh
- the settlement interval is 15 minutes
- energy from each source is calculated using the same 15-minute window for both offered and consumed power
- no storage or battery logic is required for the first version

## Open steps

The integration should expose both of the following:

- a primary 15-minute cost sensor representing the actual billed settlement window
- a derived per-hour equivalent sensor for easier reading and charting in Home Assistant

The chart requirement is satisfied by exposing both as numeric sensors with timestamps, which allows Home Assistant’s built-in graphs and statistics widgets to render historical trends without custom visualization code.

The implementation can proceed with this as the target design.
