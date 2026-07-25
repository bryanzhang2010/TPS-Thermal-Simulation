"""
visualise.py — Plotting functions for thermal profiles, material comparisons, and sweeps.
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# Apply dark theme styling
plt.style.use('dark_background')


def temp_chart(results, save_path="figures/comparison.png"):
    """
    Plots outer vs inner surface temperatures for all materials over time.
    Saves figure to disk[cite: 1].
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.figure(figsize=(10, 6))
    
    colors = {"aluminum": "#3a86ff", "alumina": "#ff006e", "pica": "#8338ec"}
    
    for name, res in results.items():
        t = res["times"]
        c = colors.get(name, "white")
        
        plt.plot(t, res["T_outer"], label=f"{name.capitalize()} (Outer)", color=c, linestyle="--", alpha=0.8)
        plt.plot(t, res["T_inner"], label=f"{name.capitalize()} (Inner)", color=c, linewidth=2.0)

    plt.axhline(y=600.0, color="red", linestyle=":", linewidth=1.5, label="Failure Threshold (600 K)")
    
    plt.xlabel("Time (s)", fontsize=11)
    plt.ylabel("Temperature (K)", fontsize=11)
    plt.title("TPS Material Surface Temperatures (1 MW/m² Heat Flux)", fontsize=13, pad=12)
    plt.grid(True, linestyle=":", alpha=0.4)
    plt.legend(loc="upper left")
    plt.ylim(0, 2000)
    plt.annotate("PICA outer surface exceeds 37,000 K (off-axis) — outer node absorbs flux; inner surface remains at 306 K",
             xy=(0.02, 0.97), xycoords='axes fraction', fontsize=8,
             color='gray', va='top')



    plt.tight_layout()
    
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved comparison plot to {save_path}")


def validation_plot(x, fd, exact, t_actual, save_path="figures/validation.png"):
    """
    Plots numerical finite difference solution against semi-infinite analytical baseline[cite: 1].
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.figure(figsize=(8, 5))
    
    plt.plot(x * 1000.0, fd, 'o', label="Finite Difference (FD)", color="#00f5d4", markersize=4)
    plt.plot(x * 1000.0, exact, '-', label="Analytical Semi-Infinite", color="#ff006e", linewidth=1.5)
    
    plt.xlabel("Depth into Shield (mm)", fontsize=11)
    plt.ylabel("Temperature (K)", fontsize=11)
    plt.title(f"Numerical FD vs Analytical Solution (t = {t_actual:.2f} s)", fontsize=12)
    plt.grid(True, linestyle=":", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved validation plot to {save_path}")


if __name__ == "__main__":
    from config import MATERIAL_LIB, BOUNDARY_CFG, GRID_CFG
    from analysis import compare_materials, validate
    
    print("Generating validation plot...")
    _, x, fd, exact, t_act = validate(MATERIAL_LIB["aluminum"], BOUNDARY_CFG, GRID_CFG, t_eval=2.0)
    validation_plot(x, fd, exact, t_act)
    
    print("Generating multi-material comparison plot...")
    results = compare_materials(MATERIAL_LIB, BOUNDARY_CFG, GRID_CFG)
    temp_chart(results)
    
    print("\n--- RESULTS SUMMARY ---")
    for name, res in results.items():
        t_crit_str = f"{res['t_critical']:.1f} s" if res['t_critical'] else "None (>90 s)"
        print(f"{name.capitalize():<10} | t_critical: {t_crit_str:<12} | Peak T_inner: {res['T_inner_max']:.1f} K")
