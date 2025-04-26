# Reactor Heat Model: Full Simulation Code
# -----------------------------------------------------
# Simulates heating, reaction, and cooling cycles of a jacketed reactor
# Includes oil flow loop with pipe losses, heat exchanger limitations (area, flow, device)
# Tracks oil temperature throughout the circuit and logs rate-limiting steps

import math
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import plotly.io as pio

# -------------------------
# 1. Physical Constants
# -------------------------
cp = {
    "oil": 2200,       # J/kg.K
    "water": 4186,     # J/kg.K
    "minerals": 900,   # J/kg.K
    "steel": 500       # J/kg.K
}
rho = {
    "oil": 800,        # kg/m3
    "steel": 8000,     # kg/m3
    "water": 1000      # kg/m3
}
approach_temp = 0.5  # Minimum temperature difference for effective heat transfer (°C)

# -------------------------
# 2. Design Parameters
# -------------------------
filename = "simulation_results_big_huber_low_Oil_temp.html"

design = {
    "heater_max_duty": 96e3,   # W 96 or 36kW
    "cooler_max_duty": 60e3,   # W

    "oil_flow_m3_per_h": 10,   # m3/h 10 or 6m3/h
    "water_flow_m3_per_h": 30, # m3/h

    "cooling_water_temp": 10,  # °C
    "oil_max_temp": 200,       # °C 250 or 200 °C
    "jacket_max_temp": 240,    # °C
    "reactor_max_temp": 175,   # °C
    "ambient_temp": 25,        # °C

    "reaction_time": 1*3600,     # s (in hours)
}

Mineral_weight = 350 # kg
Water_weight = 150 # kg
K_p = 92.0  # Proportional gain (adjust as needed for stability)


# Reactor geometry
diameter = 1.5  # m
radius = diameter / 2
height = 2.0    # m
thickness = 0.03 # m

# Pipe geometry
pipe_length = 10 # m
pipe_diameter = 0.0254# m
pipe_area = math.pi * pipe_diameter * pipe_length # m2
pipe_volume = math.pi * (pipe_diameter / 2)**2 * pipe_length # m3

# simulation parameters
dt = 60 #sec
end_time = 6 * 3600 #sec


# Heat exchange areas
design["heat_exchange_areas"] = {
    "heater_oil": 5.0, # m2
    "oil_jacket": math.pi * diameter * height,
    "jacket_reactor": math.pi * diameter * height,
    "cooler_oil": 3.0, # m2
    "pipe_outside" : pipe_area,
    "jacket_outside": math.pi * diameter * height,
    "reactor_outside": 2*math.pi * radius**2
}

# Heat transfer coefficients
design["U_values"] = {
    "heater_oil": 200,
    "oil_jacket": 150,
    "jacket_reactor": 100,
    "cooler_oil": 400,
    "pipe_outside": 2, # W/m2.K (assumed for pipe losses)
    "jacket_outside": 2, # W/m2.K (assumed for jacket losses over outer shell)
    "reactor_outside": 3 # W/m2.K (assumed for reactor losses over top and bottom)
}

# -------------------------
# 4. Flow Rates
# -------------------------
m_dot_oil = rho["oil"] * design["oil_flow_m3_per_h"] / 3600  # kg/s
m_dot_water = rho["water"] * design["water_flow_m3_per_h"] / 3600
# -------------------------
# 3. Mass and Thermal Mass
# -------------------------
shell_volume  = math.pi * (radius**2 - (radius - thickness)**2) * height
end_volume = 2 * math.pi * radius**2 * thickness # top and bottom of reactor
                  
mass_jacket = shell_volume * rho["steel"]
mass_reactor = end_volume * rho["steel"] # kg
mass_oil = pipe_volume/ 1000 * rho["oil"] # kg

masses = {
    "steel_jacket": mass_jacket,
    "steel_reactor": mass_reactor,
    "oil_pipe": mass_oil,
    "oil_flow": m_dot_oil * dt, # kg
    "water_cooling": m_dot_water * dt, # kg
}
thermal_mass = {
    k.split("_")[1]: masses[k] * cp[k.split("_")[0]] for k in masses # J/K
}

thermal_mass["reactor_contents"] = Mineral_weight * cp["minerals"] + Water_weight * cp["water"]
thermal_mass["reactor"] = thermal_mass["reactor"] + thermal_mass["reactor_contents"]


thermal_mass_kWh = {k: v * 150 / 1000 / 3600 for k, v in thermal_mass.items()}  # kWh for 150 degree increase



# -------------------------
# 5. Heat Transfer Function
# -------------------------
# Add debug flag
DEBUG_LIMIT_REASON = False


def calculate_insulation_loss(component_name, T_current):
    """
    Calculate insulation heat loss for a component and update its temperature.
    Handles both static and flowing components.
    """
    key_outside = f"{component_name}_outside"
    U = design["U_values"][key_outside]
    A = design["heat_exchange_areas"][key_outside]

    Q_loss = U * A * (T_current - design["ambient_temp"])

    if component_name == "pipe":  # Flowing component
        m_dot = m_dot_oil  # Mass flow rate of oil
        cp_oil = cp["oil"]
        T_updated = T_current - Q_loss / (m_dot * cp_oil)
    else:  # Static component
        Tmass = thermal_mass[component_name]
        T_updated = T_current - (Q_loss * dt / Tmass)

    if DEBUG_LIMIT_REASON:
        print(f"[{component_name}] Insulation loss: Q_loss={Q_loss:.1f} W, T_updated={T_updated:.2f} °C")

    return Q_loss, T_updated

# Updated calculate_heat_transfer function with optional debug print

def calculate_heat_transfer(T_hot_in, T_cold_in, thermal_mass_hot, thermal_mass_cold, max_duty=None, Exchanger_name=""):
    """
    Calculate heat transfer between two sides (hot and cold) of a heat exchanger.
    Uses global variables for U_values, heat_exchange_areas, and dt.
    """
    # Fetch U and A dynamically based on Exchanger_name
    U = design["U_values"][Exchanger_name]
    A = design["heat_exchange_areas"][Exchanger_name]

    # Calculate temperature difference
    delta_T = max(T_hot_in - T_cold_in - approach_temp, 0)
    if delta_T <= 0:
        if DEBUG_LIMIT_REASON and Exchanger_name:
            print(f"[{Exchanger_name}] No heat transfer (T_hot={T_hot_in:.2f}, T_cold={T_cold_in:.2f})")
        return 0.0, T_hot_in, T_cold_in, "no transfer"

    # Calculate Q based on area
    Q_area = U * A * delta_T

    # Calculate Q based on thermal mass limits
    Q_flow_hot = thermal_mass_hot * delta_T / dt
    Q_flow_cold = thermal_mass_cold * delta_T / dt

    # Determine the limiting Q
    Q = Q_area
    reason = "area"
    if Q_flow_hot < Q:
        Q = Q_flow_hot
        reason = "hot flow"
    if Q_flow_cold < Q:
        Q = Q_flow_cold
        reason = "cold flow"
    if max_duty is not None and Q > max_duty:
        Q = max_duty
        reason = "device"

    if DEBUG_LIMIT_REASON and Exchanger_name:
        print(f"[{Exchanger_name}] Q={Q:.1f} W (limit: {reason}, dT={delta_T:.2f} K, U={U}, A={A}, thermal_mass_hot={thermal_mass_hot}, thermal_mass_cold={thermal_mass_cold})")

    # Update temperatures based on the limiting Q
    T_hot_out = T_hot_in - (Q * dt / thermal_mass_hot)
    T_cold_out = T_cold_in + (Q * dt / thermal_mass_cold)
    return Q, T_hot_out, T_cold_out, reason



# -------------------------
# 6. Simulation
# -------------------------

T_oil = T_jacket = T_reactor = design["ambient_temp"]
status = "heating"
reaction_start_time = None

# Initialize results dictionary with additional columns for rate-limiting reasons
results = {
    "time": [],
    "T_oil_out_heater": [], "T_oil_after_pipe_to_jacket": [], "T_oil_after_jacket": [], "T_oil_after_pipe_to_heater": [],
    "T_jacket": [], "T_reactor": [],
    "Q_heater": [], "Q_cooler": [], "Q_oil_jacket": [], "Q_jacket_reactor": [],
    "Q_pipe_to_jacket": [], "Q_pipe_to_heater": [], "Q_jacket_loss": [], "Q_reactor_loss": [],
    "limit_heater": [], "limit_cooler": [], "limit_oil_jacket": [], "limit_jacket_reactor": [],
    "Q_total_loss": []
}

for t in range(0, end_time, dt):
    # 1. Update status based on reactor temperature and reaction time
    if status == "heating" and T_reactor >= design["reactor_max_temp"]:
        status = "reaction"
        reaction_start_time = t
        #Q_heater = Q_total_loss  # Keep steady temperature
    if status == "reaction" and (t - reaction_start_time) >= design["reaction_time"]:
        status = "cooling"

    # 2. Heater: Heat oil to maximum temperature
    if status in ["heating", "reaction"]:
        T_error = design["reactor_max_temp"]+5-T_reactor
        T_heater_exit = min(design["oil_max_temp"], T_oil + K_p * T_error)

        Q_heater, _, T_oil, reason = calculate_heat_transfer(
            T_heater_exit, T_oil,
            thermal_mass["flow"], thermal_mass["flow"],
            max_duty=design["heater_max_duty"], Exchanger_name="heater_oil"
        )
        Q_cooler = 0
        limit_heater = reason
        limit_cooler = "no transfer"
    elif status == "cooling":
        Q_cooler, _, T_oil, reason = calculate_heat_transfer(
            T_oil, design["cooling_water_temp"],
            thermal_mass["flow"], thermal_mass["cooling"],
            max_duty=design["cooler_max_duty"], Exchanger_name="cooler_oil"
        )
        Q_heater = 0
        limit_cooler = reason
        limit_heater = "no transfer"
    else:
        Q_heater = Q_cooler = 0
        limit_heater = limit_cooler = "no transfer"
    T_oil_out_heater = T_oil

    # 3. Pipe to Jacket: Heat loss to ambient
    Q_pipe_to_jacket, T_oil = calculate_insulation_loss("pipe", T_oil)
    T_oil_pipe_out = T_oil

    # 4. Oil to Jacket: Heat transfer to jacket
    Q_oil_jacket, T_oil, T_jacket, reason = calculate_heat_transfer(
        T_oil, T_jacket,
        thermal_mass["flow"], thermal_mass["jacket"],
        Exchanger_name="oil_jacket"
    )
    limit_oil_jacket = reason
    T_oil_jacket_out = T_oil

    # 5. Jacket to Reactor: Heat transfer to reactor
    Q_jacket_reactor, T_jacket, T_reactor, reason = calculate_heat_transfer(
        T_jacket, T_reactor,
        thermal_mass["jacket"], thermal_mass["reactor"],
        Exchanger_name="jacket_reactor"
    )
    limit_jacket_reactor = reason

    # 6. Jacket Insulation Loss
    Q_jacket_loss, T_jacket = calculate_insulation_loss("jacket", T_jacket)

    # 7. Reactor Insulation Loss
    Q_reactor_loss, T_reactor = calculate_insulation_loss("reactor", T_reactor)

    # 8. Pipe to Heater: Heat loss to ambient
    Q_pipe_to_heater, T_oil = calculate_insulation_loss("pipe", T_oil)
    T_oil_return = T_oil

    # Calculate total heat loss due to insulation
    Q_total_loss = Q_pipe_to_heater + Q_jacket_loss + Q_reactor_loss + Q_pipe_to_jacket


    # 9. Log results
    results["time"].append(t)
    results["T_oil_out_heater"].append(T_oil_out_heater)
    results["T_oil_after_pipe_to_jacket"].append(T_oil_pipe_out)
    results["T_oil_after_jacket"].append(T_oil_jacket_out)
    results["T_oil_after_pipe_to_heater"].append(T_oil_return)
    results["T_jacket"].append(T_jacket)
    results["T_reactor"].append(T_reactor)
    results["Q_heater"].append(Q_heater)
    results["Q_cooler"].append(Q_cooler)
    results["Q_oil_jacket"].append(Q_oil_jacket)
    results["Q_jacket_reactor"].append(Q_jacket_reactor)
    results["Q_pipe_to_jacket"].append(Q_pipe_to_jacket)
    results["Q_pipe_to_heater"].append(Q_pipe_to_heater)
    results["Q_jacket_loss"].append(Q_jacket_loss)
    results["Q_reactor_loss"].append(Q_reactor_loss)
    results["limit_heater"].append(limit_heater)
    results["limit_cooler"].append(limit_cooler)
    results["limit_oil_jacket"].append(limit_oil_jacket)
    results["limit_jacket_reactor"].append(limit_jacket_reactor)
    results["Q_total_loss"].append(Q_total_loss)
    Q_total_loss = Q_pipe_to_heater+Q_jacket_loss+Q_reactor_loss+Q_pipe_to_jacket
    1+1
    # debug line

# -------------------------
# 7. Visualization and Limit Summary
# -------------------------
df = pd.DataFrame(results)
print(df.head())  # Print the first few rows for debugging
print(df.tail())  # Print the last few rows for debugging

# Convert time from seconds to minutes
df["time_minutes"] = df["time"] / 60  # Add a new column for time in minutes
df["time_hours"] = df["time"] / 3600  # Add a new column for time in hours

# Create a subplot figure with two rows
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=("Temperature Profiles", "Heat Duties Over Time"),
    shared_xaxes=True  # Share the x-axis between the two plots
)

# Add temperature profiles to the first subplot
for col in ["T_oil_out_heater", "T_oil_after_pipe_to_jacket", "T_oil_after_jacket", "T_oil_after_pipe_to_heater", "T_jacket", "T_reactor"]:
    fig.add_trace(
        go.Scatter(x=df["time_hours"], y=df[col], mode='lines', name=col),
        row=1, col=1
    )

# Add heat duties to the second subplot
for col in ["Q_heater", "Q_cooler", "Q_oil_jacket", "Q_jacket_reactor", "Q_pipe_to_jacket", "Q_pipe_to_heater", "Q_jacket_loss", "Q_reactor_loss", "Q_total_loss"]:
    fig.add_trace(
        go.Scatter(x=df["time_hours"], y=df[col], mode='lines', name=col),
        row=2, col=1
    )

# Update layout for the combined figure
fig.update_layout(
    title="Simulation Results",
    xaxis_title="Time (hours)",  # Update x-axis title to reflect minutes
    yaxis_title="Temperature (°C)",
    yaxis2_title="Duty (W)",
    hovermode="x unified",
    height=800  # Adjust height for better visibility
)

# Show the combined figure
#fig.show()


# Save the plot as an HTML file
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the full path for the HTML file
html_file_path = os.path.join(script_dir, filename)

# Save the plot as an HTML file in the same directory as the script
pio.write_html(fig, file=html_file_path, auto_open=True)
