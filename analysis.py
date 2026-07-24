"""
analysis.py — Post-processing, analytical validation, material comparisons, and parameter sweeps.
"""

import numpy as np
from scipy.special import erfc
from solver import run_sim

def analytical_solution(x, t, mat, boundary_cfg):
    """
    Computes exact closed-form solution for a semi-infinite solid with constant heat flux.
    T(x,t) = T0 + (2q/k)*sqrt(alpha*t/pi)*exp(-x^2/(4*alpha*t)) - (q*x/k)*erfc(x / (2*sqrt(alpha*t)))[cite: 1]
    """
    if t <= 0:
        return np.full_like(x, boundary_cfg["T_init"])
        
    k = mat["k"]
    alpha = k / (mat["rho"] * mat["cp"])
    q = boundary_cfg["q_flux"]
    T0 = boundary_cfg["T_init"]
    
    term1 = (2 * q / k) * np.sqrt(alpha * t / np.pi) * np.exp(- (x**2) / (4 * alpha * t))
    term2 = (q * x / k) * erfc(x / (2 * np.sqrt(alpha * t)))
    
    return T0 + term1 - term2


def validate(mat, boundary_cfg, grid_cfg, t_eval=2.0):
    """
    Compares numerical FD result against analytical semi-infinite solution[cite: 1].
    Evaluated at t_eval before back-boundary thermal reflections occur[cite: 1].
    Returns max percentage error across nodes[cite: 1].
    """
    frames, times = run_sim(mat, boundary_cfg, grid_cfg)
    
    # Find snapshot closest to t_eval
    idx = int(np.argmin(np.abs(np.array(times) - t_eval)))
    t_actual = times[idx]
    fd_profile = frames[idx]
    
    # Evaluate spatial grid points x
    x = np.linspace(0, grid_cfg["thickness"], grid_cfg["N"])
    
    # Calculate analytical profile
    exact_profile = analytical_solution(x, t_actual, mat, boundary_cfg)
    
    # Percentage error across nodes (excluding points near ambient initial temp)
    valid_mask = exact_profile > (boundary_cfg["T_init"] + 0.5)
    pct_error = np.abs((fd_profile[valid_mask] - exact_profile[valid_mask]) / exact_profile[valid_mask]) * 100.0
    max_err = np.max(pct_error) if len(pct_error) > 0 else 0.0
    
    return max_err, x, fd_profile, exact_profile, t_actual


def compare_materials(material_lib, boundary_cfg, grid_cfg):
    """
    Runs solver for each material and extracts metrics for paper results[cite: 1].
    """
    results = {}
    for name, mat in material_lib.items():
        frames, times = run_sim(mat, boundary_cfg, grid_cfg)

        T_outer = [f[0] for f in frames]
        T_inner = [f[-1] for f in frames]
        delta_T = [f[0] - f[-1] for f in frames]

        T_crit = boundary_cfg["T_critical"]
        idx = next((i for i, T in enumerate(T_inner) if T >= T_crit), None)
        t_crit = times[idx] if idx is not None else None

        results[name] = {
            "T_outer": T_outer,
            "T_inner": T_inner,
            "delta_T": delta_T,
            "t_critical": t_crit,
            "T_inner_max": max(T_inner),
            "T_outer_max": max(T_outer),
            "alpha": mat["k"] / (mat["rho"] * mat["cp"]),
            "times": times,
        }

    return results


def param_sweep(sweep_type, values, material_lib, boundary_cfg, grid_cfg, mat_name="pica"):
    """
    Executes parameter sweeps for thickness or incident heat flux[cite: 1].
    """
    results = {"values": values, "T_inner_max": []}
    mat = material_lib[mat_name]
    
    for val in values:
        bcfg = boundary_cfg.copy()
        gcfg = grid_cfg.copy()
        
        if sweep_type == "thickness":
            gcfg["thickness"] = val
            gcfg["DX"] = val / (gcfg["N"] - 1)
        elif sweep_type == "flux":
            bcfg["q_flux"] = val
        else:
            raise ValueError(f"Unknown sweep type: {sweep_type}")
            
        frames, times = run_sim(mat, bcfg, gcfg)
        T_inner = [f[-1] for f in frames]
        results["T_inner_max"].append(max(T_inner))
        
    return results


if __name__ == "__main__":
    from config import MATERIAL_LIB, BOUNDARY_CFG, GRID_CFG
    
    print("Running validation check on Aluminum 6061 at t = 2.0s...")
    al_mat = MATERIAL_LIB["aluminum"]
    max_err, x, fd, exact, t_act = validate(al_mat, BOUNDARY_CFG, GRID_CFG, t_eval=2.0)
    
    print(f"Validation evaluated at t = {t_act:.2f} s")
    print(f"Max FD Error vs Analytical: {max_err:.3f}%")
    
    if max_err < 2.0:
        print("SUCCESS: Validation passes (<2% error threshold)!")
        print("Milestone 2 (Validation Complete) unlocked!")
    else:
        print("WARNING: Error exceeds 2%. Check time step resolution.")
