"""
solver.py — Pure 1D Finite Difference Thermal Solver.
Handles explicit time stepping and boundary condition enforcement.
"""

import numpy as np
from config import get_stable_dt

# ==============================================================================
# MODEL LIMITATION & ASSUMPTION CAVEAT: PICA ABLATION
# ------------------------------------------------------------------------------
# This solver models Phenolic-Impregnated Carbon Ablator (PICA) purely as a 
# static, non-ablating solid conducting heat via Fourier's Law. 
#
# Real-world PICA experiences endothermic chemical pyrolysis, gas blowing, 
# and surface recession under extreme heat fluxes (>1 MW/m²). By omitting 
# active ablation and recession mass loss, this model provides a conservative, 
# baseline lower-bound estimate of thermal insulation performance.
# 
# Reference: NASA SP-8014 (Aerothermodynamic Ablation)
# ==============================================================================


def fd_step(T, alpha, dt, dx):
    """Performs one explicit 1D finite difference step for interior nodes."""
    T_new = T.copy()
    r = alpha * dt / (dx ** 2)
    
    # Update interior nodes: 1 to N-2
    T_new[1:-1] = T[1:-1] + r * (T[:-2] - 2 * T[1:-1] + T[2:])
    return T_new


def apply_bc(T_new, T_old, mat, boundary_cfg, grid_cfg, dt):
    """
    Applies boundary conditions:
      - Outer (i=0): Applied heat flux Neumann BC (q_flux)
      - Inner (i=N-1): Insulated Neumann BC (dT/dx = 0)
    """
    k = mat["k"]
    alpha = k / (mat["rho"] * mat["cp"])
    dx = grid_cfg["DX"]
    q = boundary_cfg["q_flux"]
    r = alpha * dt / (dx ** 2)

    # Outer boundary (Heat flux in)
    T_new[0] = T_old[0] + (2 * alpha * dt / dx**2) * (T_old[1] - T_old[0]) + (2 * dt * q) / (mat["rho"] * mat["cp"] * dx)



    # Inner boundary (Insulated back face)
    T_new[-1] = T_old[-1] + r * (2 * T_old[-2] - 2 * T_old[-1])

    return T_new


def run_sim(mat, boundary_cfg, grid_cfg, save_every=100):
    """
    Runs full time-stepping loop for a given material.
    Returns saved temperature frames and time stamps.
    """
    alpha = mat["k"] / (mat["rho"] * mat["cp"])
    dx = grid_cfg["DX"]
    dt = get_stable_dt(mat, grid_cfg)
    
    duration = boundary_cfg["duration"]
    total_steps = int(np.ceil(duration / dt))
    
    # Initialize uniform temperature distribution
    T = np.full(grid_cfg["N"], boundary_cfg["T_init"], dtype=float)
    
    frames = [T.copy()]
    times = [0.0]
    
    t = 0.0
    for step in range(1, total_steps + 1):
        T_next = fd_step(T, alpha, dt, dx)
        T_next = apply_bc(T_next, T, mat, boundary_cfg, grid_cfg, dt)
        
        T = T_next
        t += dt
        
        # Save frame periodically for visualization and analysis
        if step % save_every == 0 or step == total_steps:
            frames.append(T.copy())
            times.append(min(t, duration))
            
    return frames, times


if __name__ == "__main__":
    from config import MATERIAL_LIB, BOUNDARY_CFG, GRID_CFG
    
    print("Testing solver with Aluminum 6061...")
    al_mat = MATERIAL_LIB["aluminum"]
    frames, times = run_sim(al_mat, BOUNDARY_CFG, GRID_CFG)
    
    print(f"Simulation completed successfully!")
    print(f"Total recorded frames: {len(frames)}")
    print(f"Final outer surface temp (t={times[-1]:.1f}s): {frames[-1][0]:.2f} K")
    print(f"Final inner surface temp (t={times[-1]:.1f}s): {frames[-1][-1]:.2f} K")
