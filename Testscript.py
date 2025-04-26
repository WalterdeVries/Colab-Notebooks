#%%
# from coolprop.CoolProp import PropsSI
from CoolProp.CoolProp import PropsSI
# from CoolProp import Plots
# import CoolProp.CoolProp as CoolProp

print("Testing CoolProp...")
density = PropsSI("D", "T", 300, "P", 101325, "CO2")
print(f"CO₂ density at 300K and 1 atm: {density:.2f} kg/m³")

#%%
cpCO2 = PropsSI("C", "T", 300, "P", 21325, "CO2")


# %%
