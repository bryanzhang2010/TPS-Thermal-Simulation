"""
config.py — System constants, material data, boundary conditions, and grid setup.
No physics or execution logic here.
"""

import numpy as np

# 1. Material Library
# Properties: k (W/m·K), rho (kg/m³), cp (J/kg·K)
MATERIAL_LIB = {
    "aluminum": {
        "k": 167.0,
        "rho": 2700.0,
        "cp": 896.0,
        "source": "MatWeb (Aluminum 6061-T6)"
    },
    "alumina": {
        "k": 30.0,
        "rho": 3960.0,
        "cp": 880.0,
        "source": "MatWeb (Aluminium Oxide 99.5%)"
    },
    "pica": {
        "k": 0.30,
        "rho": 270.0,
        "cp": 1050.0,
        "source": "NASA TM-2004-213069"
    }
}

# 2. Boundary & Simulation Conditions
BOUNDARY_CFG = {
    "q_flux": 1.0e6,      # Heat flux on outer surface (W/m² = 1 MW/m²)
    "T_init": 300.0,      # Initial uniform temperature (K)
    "duration": 90.0,     # Simulation time (seconds)
    "T_critical": 600.0   # Failure threshold for inner surface (K)
}

# 3. Spatial Grid Configuration
GRID_CFG = {
    "N": 60,              # Number of nodes
    "thickness": 0.05     # Shield thickness in meters (5 cm)
}

# Derived Spatial Step Size (DX)
GRID_CFG["DX"] = GRID_CFG["thickness"] / (GRID_CFG["N"] - 1)

# Function to compute stable dt dynamically per material
def get_stable_dt(mat_dict, grid_cfg, safety_factor=0.45):
    """Computes max stable time step dt according to the CFL stability limit."""
    alpha = mat_dict["k"] / (mat_dict["rho"] * mat_dict["cp"])
    dt_max = (grid_cfg["DX"] ** 2) / (2.0 * alpha)
    return safety_factor * dt_max

# Quick verification output on import
if __name__ == "__main__":
    print("=== CONFIGURATION CHECK ===")
    print(f"Grid: {GRID_CFG['N']} nodes over {GRID_CFG['thickness']} m (DX = {GRID_CFG['DX']:.6f} m)")
    print("\nMaterial Diffusivities & Max Stable Time Steps:")
    for name, mat in MATERIAL_LIB.items():
        alpha = mat["k"] / (mat["rho"] * mat["cp"])
        dt = get_stable_dt(mat, GRID_CFG)
        print(f" - {name.capitalize():<10}: alpha = {alpha:.3e} m²/s | dt = {dt:.6f} s")