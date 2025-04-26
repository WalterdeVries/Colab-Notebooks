import numpy as np
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP

def get_CO2_properties():
    """Retrieve critical and triple point properties for CO2."""
    T_trip = CP.PropsSI('Ttriple', 'CO2')  # Triple point temperature (K)
    P_trip = CP.PropsSI('ptriple', 'CO2')  # Triple point pressure (Pa)
    T_crit = CP.PropsSI('Tcrit', 'CO2')   # Critical point temperature (K)
    P_crit = CP.PropsSI('pcrit', 'CO2')   # Critical point pressure (Pa)
    return T_trip, P_trip, T_crit, P_crit

def calculate_boiling_curve(T_trip, T_crit):
    """Calculate the boiling curve using CoolProp."""
    T_points = np.linspace(T_trip, T_crit, 100)  # Temperature range (K)
    P_points = [CP.PropsSI('P', 'T', T, 'Q', 1, 'CO2') for T in T_points]  # Saturation pressure (Pa)
    return T_points - 273.15, np.array(P_points) / 1e5 - 1.01325  # Convert to °C and barg

#def calculate_sublimation_curve(T_trip, P_trip):
 #   """Calculate the sublimation curve using CoolProp."""
  #  T_points = np.linspace(T_trip - 20, T_trip, 50)  # Extend slightly below triple point
   # P_points = [CP.PropsSI('P', 'T', T, 'Q', 0, 'CO2') for T in T_points]  # Sublimation pressure (Pa)
    #return T_points - 273.15, np.array(P_points) / 1e5 - 1.01325  # Convert to °C and barg

def calculate_sublimation_curve():
    # Fixed values for CO2 sublimation curve
    # Format: (Temperature in °C, Pressure in bar)
    sublimation_points = [
        (-56.6, 5.18),    # Triple point
        (-60, 3.5),
        (-65, 2.0),
        (-70, 1.1),
        (-75, 0.6),
        (-80, 0.3),
        (-85, 0.15),
        (-90, 0.07),
        (-95, 0.03),
        (-100, 0.01)
    ]
    
    # Convert to lists and adjust pressure to barg
    T_points = [point[0] for point in sublimation_points]
    P_points = [point[1] - 1.01325 for point in sublimation_points]  # Convert to barg
    
    return T_points, P_points



def generate_property_grid():
    """Generate a grid of temperature, pressure, density, and enthalpy values."""
    # Define temperature and pressure ranges
    temperatures = np.linspace(-100 + 273.15, 250 + 273.15, 200)  # Kelvin
    pressures = np.linspace(0.01 * 1e5, 120 * 1e5, 200)  # Pascals

    # Create a meshgrid
    T, P = np.meshgrid(temperatures, pressures)

    # Calculate density and enthalpy for each point
    densities = np.vectorize(CP.PropsSI)('D', 'T', T, 'P', P, 'CO2')
    enthalpies = np.vectorize(CP.PropsSI)('H', 'T', T, 'P', P, 'CO2') / 1000  # Convert to kJ/kg

    return T, P, densities, enthalpies

def plot_iso_lines(ax, T, P, property_grid, levels, label_fmt, color, label_color):
    """Plot iso-lines for a given property grid."""
    # Convert temperature and pressure to °C and bar
    T_C = T - 273.15
    P_bar = P / 1e5

    # Plot iso-lines
    contour_lines = ax.contour(T_C, P_bar, property_grid, levels=levels, colors=color)
    ax.clabel(contour_lines, inline=True, fontsize=8, fmt=label_fmt, colors=label_color)

def create_phase_diagram():
    # Retrieve CO2 properties
    T_trip, P_trip, T_crit, P_crit = get_CO2_properties()

    # Calculate phase boundaries
    T_boiling, P_boiling = calculate_boiling_curve(T_trip, T_crit)
    T_sublimation, P_sublimation = calculate_sublimation_curve(T_trip, P_trip)

    # Generate property grid for iso-lines
    temperatures = np.linspace(-100 + 273.15, 250 + 273.15, 200)  # Kelvin
    pressures = np.linspace(0.01 * 1e5, 120 * 1e5, 200)  # Pascals
    T, P = np.meshgrid(temperatures, pressures)
    densities = np.vectorize(CP.PropsSI)('D', 'T', T, 'P', P, 'CO2')
    enthalpies = np.vectorize(CP.PropsSI)('H', 'T', T, 'P', P, 'CO2') / 1000  # Convert to kJ/kg

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot phase boundaries
    ax.plot(T_boiling, P_boiling, 'b-', label='Boiling Curve', linewidth=2)
    ax.plot(T_sublimation, P_sublimation, 'g-', label='Sublimation Curve', linewidth=2)

    # Add critical and triple points
    ax.plot(T_crit - 273.15, P_crit / 1e5 - 1.01325, 'ro', label='Critical Point')
    ax.plot(T_trip - 273.15, P_trip / 1e5 - 1.01325, 'ko', label='Triple Point')

    # Plot iso-lines for density
    contour_density = ax.contour(T - 273.15, P / 1e5 - 1.01325, densities, levels=np.arange(100, 1000, 100), colors='gray')
    ax.clabel(contour_density, inline=True, fontsize=8, fmt='%1.0f kg/m³')

    # Plot iso-lines for enthalpy
    contour_enthalpy = ax.contour(T - 273.15, P / 1e5 - 1.01325, enthalpies, levels=np.arange(100, 700, 100), colors='green')
    ax.clabel(contour_enthalpy, inline=True, fontsize=8, fmt='%1.0f kJ/kg')

    # Add labels, grid, and legend
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Pressure (barg)')
    ax.set_xlim(-100, 250)
    ax.set_ylim(-1, 120)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    ax.set_title('CO2 Phase Diagram with Iso-Lines', pad=20)

    # Show the plot
    plt.show()

if __name__ == "__main__":
    create_phase_diagram()