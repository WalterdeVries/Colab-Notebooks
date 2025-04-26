"""
Reactor Headspace Simulation with Inert Gas Accumulation and Purge

This script models the accumulation of nitrogen (N₂) and hydrogen (H₂) in the headspace 
of a continuous reactor converting olivine (forsterite + fayalite) with water and CO₂.

Conditions:
- T = 175°C, P = 100 bar
- Water is CO₂-saturated
- Fayalite reactivity is low; only 0.5% assumed to form H₂ based on experimental evidence
- CO₂ feed contains 0.1% N₂ impurity
- Purge is implemented at 5 wt% of CO₂ flow

Outputs:
- Vol% of H₂ and N₂ in headspace over time
- CSV export
- Warning if H₂ exceeds 10% of its Lower Explosive Limit (LEL)

Required packages:
pip install coolprop matplotlib numpy pandas
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from CoolProp.CoolProp import PropsSI
import datetime


# -----------------------------
# Configuration Block
# -----------------------------
config = {
    "time_h": 300,
    "dt": 1 / 60,  # 1 min in hours
    "headspace_volume_L": 2000,
    "water_feed_Lph": 130,
    "mineral_feed_kgph": 60,
    "forsterite_frac": 0.55*0.95,
    "fayalite_frac": 0.55*0.05,
    "forsterite_M": 140.69,
    "fayalite_M": 203.77,
    "CO2_M": 44.01,
    "N2_M": 28.014,
    "H2_M": 2.016,
    "forsterite_conversion": 0.98,
    "fayalite_conversion": 0.33,
    "h2_yield_per_fayalite": 0.005,  # updated based on paper (0.5%)
 
    "CO2_solubility_kg_per_100L": 3,
    "CO2_feed_purity": 0.997,
    "CO2_purge_wt_fraction": 0.01,
    "temperature_C": 175,
    "pressure_bar": 100,
    "save_to_csv": False,
    "debug": True
}

# -----------------------------
# Helper: Molar Volume via CoolProp
# -----------------------------
def get_molar_volume(gas, T_K, P_Pa):
    density = PropsSI("D", "T", T_K, "P", P_Pa, gas)
    molar_mass = PropsSI("M", gas)
    return molar_mass / density

# -----------------------------
# Unpack and derive parameters
# -----------------------------
T_K = config["temperature_C"] + 273.15
P_Pa = config["pressure_bar"] * 1e5
dt = config["dt"]
n_steps = int(config["time_h"] / dt)
headspace_volume_m3 = config["headspace_volume_L"] / 1000
n2_impurity = 1 - config["CO2_feed_purity"]

# Molar volumes [m³/mol]
Vmol_CO2 = get_molar_volume("CO2", T_K, P_Pa)
Vmol_N2 = get_molar_volume("N2", T_K, P_Pa)
Vmol_H2 = get_molar_volume("H2", T_K, P_Pa)


# CO2 dissolution
CO2_solubility_kgph = (config["CO2_solubility_kg_per_100L"] / 100) * config["water_feed_Lph"]
CO2_dissolved_molph = (CO2_solubility_kgph * 1000) / config["CO2_M"]

# Mineral feed to mol/h
forsterite_molph = (config["mineral_feed_kgph"] * 1000 * config["forsterite_frac"]) / config["forsterite_M"]
fayalite_molph = (config["mineral_feed_kgph"] * 1000 * config["fayalite_frac"]) / config["fayalite_M"]

# CO2 consumption
CO2_needed_molph = (
    forsterite_molph * 2 * config["forsterite_conversion"] +
    fayalite_molph * 2 * config["fayalite_conversion"]
)
CO2_feed_molph = CO2_needed_molph + CO2_dissolved_molph

# Calculate CO2 consumption in kg/h
CO2_consumed_reaction_kgph = CO2_needed_molph * config["CO2_M"] / 1000  # mol/h to kg/h
CO2_total_consumed_kgph = CO2_consumed_reaction_kgph + CO2_solubility_kgph 

# Print the CO2 consumption details
print("\n--- CO2 Consumption Details ---")
print(f"CO2 consumed by reaction: {CO2_consumed_reaction_kgph:.2f} kg/h")
print(f"CO2 consumed by water saturation: {CO2_solubility_kgph:.2f} kg/h")
print(f"Total CO2 consumed: {CO2_total_consumed_kgph:.2f} kg/h\n")


# Inert and H2 feed
N2_feed_molph = CO2_feed_molph / config["CO2_feed_purity"] * n2_impurity
H2_feed_molph = fayalite_molph * config["fayalite_conversion"] * config["h2_yield_per_fayalite"]
purge_molph = CO2_feed_molph * config["CO2_purge_wt_fraction"]

# ---------------------------------------------------------
# Estimate 95% Equilibrium Time for Inert Gases (Analytical)
# ---------------------------------------------------------
# We're modeling the accumulation of inert gases (H₂, N₂)
# into a constant-volume headspace with ideal gas behavior.
# These gases build up from a constant inflow and are removed
# proportionally via an ideal mixing purge (like a CSTR).
#
# The dynamic follows:
#   dC/dt = R_in - k * C     (1st order)
#   C_ss = R_in / k
#   t_95% ≈ 3 / k
#
# Where:
#   R_in = mol/h inflow of the gas (H₂ or N₂)
#   purge_molph = total purge rate in mol/h
#   k = purge_molph / total mol in headspace (assumed constant)
# ---------------------------------------------------------

# Estimate initial mol content of headspace (100% CO2 at start)
headspace_mol = headspace_volume_m3 / Vmol_CO2  # mol
# Effective purge constant
k_purge = purge_molph / headspace_mol  # 1/h
# Time to 95% equilibrium = 3 time constants
t95 = 3 / k_purge  # for any trace gas like H₂

print("\n--- Analytical Estimate of Time to 95% Equilibrium ---")
print(f"Headspace mol content: {headspace_mol:.1f} mol")
print(f"Purge rate: {purge_molph:.2f} mol/h")
print(f"Effective purge constant k: {k_purge:.4f} 1/h")
print(f"→ Estimated time to reach 95% of equilibrium for trace gases: {t95:.1f} hours\n")


# -----------------------------
# Simulation Loop
# -----------------------------
CO2_acc = headspace_volume_m3 / Vmol_CO2  # initial mol CO2 in headspace
N2_acc = 0.0
H2_acc = 0.0
vol_pct_N2, vol_pct_H2, time_series, purge_weights = [], [], [], []

print(f"Simulation started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

for step in range(n_steps):
    N2_acc += N2_feed_molph * dt
    H2_acc += H2_feed_molph * dt
    V_N2 = N2_acc * Vmol_N2
    V_H2 = H2_acc * Vmol_H2
    # Remaining volume = CO2 volume
    V_CO2 = headspace_volume_m3 - V_N2 - V_H2
    
    if V_CO2 < 0:
         raise ValueError(f"At time {step * dt:.2f} h, gas volume exceeds headspace! "
                                                   f"(V_N2 + V_H2 = {V_N2 + V_H2:.3f} m³)")
    CO2_acc = V_CO2 / Vmol_CO2  
    # Total mol in headspace
    total_mol = CO2_acc + N2_acc + H2_acc

    if total_mol > 0:
        # Mole fractions in the purge stream
        x_CO2 = CO2_acc / total_mol
        x_N2 = N2_acc / total_mol
        x_H2 = H2_acc / total_mol

        # Purge flow rates (mol/h) for each gas
        purge_CO2 = purge_molph * x_CO2
        purge_N2 = purge_molph * x_N2
        purge_H2 = purge_molph * x_H2

        # Purge flow weights (kg/h) for each gas
        purge_weight_CO2 = purge_CO2 * config["CO2_M"] / 1000
        purge_weight_N2 = purge_N2 * config["N2_M"] / 1000
        purge_weight_H2 = purge_H2 * config["H2_M"] / 1000

        # Total purge weight (kg/h)
        total_purge_weight = purge_weight_CO2 + purge_weight_N2 + purge_weight_H2
        purge_weights.append(total_purge_weight)

        # Update accumulations after purge
        N2_acc -= purge_N2 * dt
        H2_acc -= purge_H2 * dt
        CO2_acc -= purge_CO2 * dt

    vol_pct_N2.append(100 * V_N2 / headspace_volume_m3)
    vol_pct_H2.append(100 * V_H2 / headspace_volume_m3)
    time_series.append(step * dt)

    if config["debug"] and vol_pct_H2[-1] > 0.4:
        print(f"[WARNING] H2 exceeds 10% LEL at {time_series[-1]:.2f} hours: {vol_pct_H2[-1]:.3f}%")


# -----------------------------
# Plotting
# -----------------------------
plt.figure(figsize=(10, 5))
plt.plot(time_series, vol_pct_N2, label="N₂ vol%")
plt.plot(time_series, vol_pct_H2, label="H₂ vol%")
plt.axhline(0.4, color='red', linestyle='--', label="10% LEL H₂ (0.4%)")
plt.xlabel("Time [h]")
plt.ylabel("Gas Volume % in Headspace")
plt.title("Inert Gas Accumulation with 5 wt% CO₂ Purge")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ----------------------------- 
# Optional CSV Export
# -----------------------------
if config["save_to_csv"]:
    df = pd.DataFrame({
        "Time (h)": time_series,
        "N2 vol%": vol_pct_N2,
        "H2 vol%": vol_pct_H2
    })
    df.to_csv("reactor_headspace_gas_accumulation.csv", index=False)
    print("Saved results to reactor_headspace_gas_accumulation.csv")


# %%
