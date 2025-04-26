import math
import pandas as pd
import plotly.graph_objects as go

# -------------------------
# 1. Physical Constants
# -------------------------
cp = {
    "oil": 2200,        # J/kg.K
    "water": 4186,      # J/kg.K
    "minerals": 900,    # J/kg.K
    "steel": 500        # J/kg.K
}
rho = {
    "oil": 800,         # kg/m3
    "steel": 8000       # kg/m3
}

# -------------------------
# 2. Design Parameters
# -------------------------
design = {
    "heater_max_duty": 96e3,    # W
    "cooler_max_duty": 60e3,    # W
    "oil_volume_liters": 150,    # Liters
    "oil_flow_m3_per_h": 10,     # m3/h
    "cooling_water_temp": 20,    # °C
    "oil_max_temp": 250,         # °C
    "jacket_max_temp": 240,      # °C
    "reactor_max_temp": 175,     # °C
    "reaction_time": 60*60*2,    # seconds (hold reactor temp)
    "heat_exchange_areas": {
        "heater_oil": 3.0,       # m2
        "oil_jacket": math.pi * 1.5 * 2.0,
        "jacket_reactor": math.pi * 1.5 * 2.0,
        "cooler_oil": 2.0        # m2
    },
    "U_values": {
        "heater_oil": 200,       # W/m2.K
        "oil_jacket": 150,       # W/m2.K
        "jacket_reactor": 100,   # W/m2.K
        "cooler_oil": 180        # W/m2.K
    },
    "ambient_temp": 25,          # °C
    "pipe_loss_area": 0.25,      # m2
    "pipe_loss_U": 5             # W/m2.K
}

# -------------------------
# 3. Mass and Thermal Mass
# -------------------------
diameter = 1.5  # m
radius = diameter / 2
height = 2.0    # m
thickness = 0.1 # m

outer_volume = math.pi * (radius ** 2) * height
inner_volume = math.pi * ((radius - thickness) ** 2) * height
steel_volume_shell = outer_volume - inner_volume

outer_area = math.pi * (radius ** 2)
inner_area = math.pi * ((radius - thickness) ** 2)
steel_volume_ends = (outer_area - inner_area) * 2

total_steel_volume = steel_volume_shell + steel_volume_ends
mass_steel = total_steel_volume * rho["steel"]
mass_oil = (design["oil_volume_liters"] / 1000) * rho["oil"]

masses = {
    "reactor_steel": mass_steel,
    "water": 350,           
    "minerals": 150,
    "oil": mass_oil
}
thermal_mass = {
    k: masses[k] * cp["steel" if k == "reactor_steel" else k] for k in masses
}

# -------------------------
# 4. Helper Functions
# -------------------------
def heat_transfer(U, A, T_hot, T_cold):
    return U * A * max(T_hot - T_cold, 0)

def update_temp(T, Q, thermal_mass, dt):
    return T + Q * dt / thermal_mass

# -------------------------
# 5. Simulation Loop
# -------------------------
dt = 10  # timestep in seconds
time = list(range(0, 7200, dt))  # simulate 2 hours

# Initialize temperatures
T_oil = 25
T_jacket = 25
T_reactor = 25

# Store results
results = {
    "time": [],
    "T_oil_out_heater": [],
    "T_oil_in_jacket": [],
    "T_jacket": [],
    "T_reactor": [],
    "T_oil_out_jacket": [],
    "T_oil_back_to_heater": [],
    "Q_heater": [],
    "Q_cooler": [],
    "Q_oil_to_jacket": [],
    "Q_jacket_to_reactor": [],
    "Q_pipe_losses": [],
    "Q_jacket_loss": [],
    "Q_reactor_loss": []
}

# Control variables
heating = True
reaction_started = False
reaction_start_time = None

for t in time:
    # Determine mode
    if heating and T_reactor >= design["reactor_max_temp"]:
        heating = False
        reaction_started = True
        reaction_start_time = t

    if reaction_started and (t - reaction_start_time) >= design["reaction_time"]:
        cooling = True
    else:
        cooling = False

    # Heat or cool oil
    T_oil_in = T_oil
    if heating:
        Q_heater = min(design["heater_max_duty"], heat_transfer(
            design["U_values"]["heater_oil"],
            design["heat_exchange_areas"]["heater_oil"],
            design["oil_max_temp"],
            T_oil_in
        ))
        T_oil = update_temp(T_oil, Q_heater, thermal_mass["oil"], dt)
        Q_cooler = 0
    elif cooling:
        Q_cooler = min(design["cooler_max_duty"], heat_transfer(
            design["U_values"]["cooler_oil"],
            design["heat_exchange_areas"]["cooler_oil"],
            T_oil,
            design["cooling_water_temp"]
        ))
        T_oil = update_temp(T_oil, -Q_cooler, thermal_mass["oil"], dt)
        Q_heater = 0
    else:
        Q_heater = 0
        Q_cooler = 0

    # Pipe losses (forward and return)
    Q_pipe_loss = 2 * heat_transfer(
        design["pipe_loss_U"], design["pipe_loss_area"], T_oil, design["ambient_temp"]
    )
    T_oil -= Q_pipe_loss * dt / thermal_mass["oil"]

    # Oil to jacket
    Q_oil_jacket = heat_transfer(
        design["U_values"]["oil_jacket"],
        design["heat_exchange_areas"]["oil_jacket"],
        T_oil,
        T_jacket
    )
    T_jacket = update_temp(T_jacket, Q_oil_jacket, thermal_mass["reactor_steel"], dt)

    # Jacket to reactor
    T_reactor_contents = T_reactor
    Q_jacket_reactor = heat_transfer(
        design["U_values"]["jacket_reactor"],
        design["heat_exchange_areas"]["jacket_reactor"],
        T_jacket,
        T_reactor_contents
    )
    total_reactor_mass = thermal_mass["water"] + thermal_mass["minerals"]
    T_reactor = update_temp(T_reactor, Q_jacket_reactor, total_reactor_mass, dt)

    # Losses
    Q_jacket_loss = heat_transfer(5, design["heat_exchange_areas"]["oil_jacket"], T_jacket, design["ambient_temp"])
    T_jacket -= Q_jacket_loss * dt / thermal_mass["reactor_steel"]

    Q_reactor_loss = heat_transfer(3, 2 * math.pi * (radius**2), T_reactor, design["ambient_temp"])
    T_reactor -= Q_reactor_loss * dt / total_reactor_mass

    # Log
    results["time"].append(t)
    results["T_oil_out_heater"].append(T_oil)
    results["T_oil_in_jacket"].append(T_oil - 1)
    results["T_jacket"].append(T_jacket)
    results["T_reactor"].append(T_reactor)
    results["T_oil_out_jacket"].append(T_oil - 2)
    results["T_oil_back_to_heater"].append(T_oil - 3)
    results["Q_heater"].append(Q_heater)
    results["Q_cooler"].append(Q_cooler)
    results["Q_oil_to_jacket"].append(Q_oil_jacket)
    results["Q_jacket_to_reactor"].append(Q_jacket_reactor)
    results["Q_pipe_losses"].append(Q_pipe_loss)
    results["Q_jacket_loss"].append(Q_jacket_loss)
    results["Q_reactor_loss"].append(Q_reactor_loss)

# -------------------------
# 6. Plotting
# -------------------------
df = pd.DataFrame(results)

fig_temp = go.Figure()
for col in ["T_oil_out_heater", "T_oil_in_jacket", "T_jacket", "T_reactor", "T_oil_out_jacket", "T_oil_back_to_heater"]:
    fig_temp.add_trace(go.Scatter(x=df["time"], y=df[col], mode='lines', name=col))

fig_temp.update_layout(
    title='Temperature Profiles Over Time',
    xaxis_title='Time (s)',
    yaxis_title='Temperature (°C)',
    hovermode='x unified'
)

fig_duty = go.Figure()
for col in ["Q_heater", "Q_cooler", "Q_oil_to_jacket", "Q_jacket_to_reactor", "Q_pipe_losses", "Q_jacket_loss", "Q_reactor_loss"]:
    fig_duty.add_trace(go.Scatter(x=df["time"], y=df[col], mode='lines', name=col))

fig_duty.update_layout(
    title='Heat Duties Over Time',
    xaxis_title='Time (s)',
    yaxis_title='Duty (W)',
    hovermode='x unified'
)

fig_temp.show()
fig_duty.show()
