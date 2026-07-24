"""
main.py — Entry point for TPS Thermal Simulation.
Orchestrates solver, analysis, and visualization via command-line arguments.
"""

import argparse
from config import MATERIAL_LIB, BOUNDARY_CFG, GRID_CFG
from analysis import compare_materials, validate, param_sweep
from visualise import temp_chart, validation_plot


def main():
    parser = argparse.ArgumentParser(description="1D Thermal Protection System (TPS) Finite Difference Simulation")
    parser.add_argument("--validate", action="store_true", help="Run analytical validation against semi-infinite model")
    parser.add_argument("--material", choices=["all", "aluminum", "alumina", "pica"], default="all", help="Select material to run")
    parser.add_argument("--sweep", choices=["thickness", "flux"], help="Run parameter sweep mode")
    
    args = parser.parse_args()

    if args.validate:
        print("=== RUNNING ANALYTICAL VALIDATION ===")
        mat = MATERIAL_LIB["aluminum"]
        max_err, x, fd, exact, t_act = validate(mat, BOUNDARY_CFG, GRID_CFG, t_eval=2.0)
        validation_plot(x, fd, exact, t_act)
        print(f"Validation complete at t = {t_act:.2f} s. Max Error: {max_err:.3f}%")

    elif args.sweep:
        print(f"=== RUNNING PARAMETER SWEEP: {args.sweep.upper()} ===")
        if args.sweep == "thickness":
            vals = [0.01, 0.02, 0.03, 0.04, 0.05]
            res = param_sweep("thickness", vals, MATERIAL_LIB, BOUNDARY_CFG, GRID_CFG)
            print("Thickness (m) vs Peak T_inner (K):")
            for v, t_peak in zip(res["values"], res["T_inner_max"]):
                print(f"  {v:.2f} m  ->  {t_peak:.1f} K")
        elif args.sweep == "flux":
            vals = [0.5e6, 1.0e6, 1.5e6, 2.0e6]
            res = param_sweep("flux", vals, MATERIAL_LIB, BOUNDARY_CFG, GRID_CFG)
            print("Flux (MW/m²) vs Peak T_inner (K):")
            for v, t_peak in zip(res["values"], res["T_inner_max"]):
                print(f"  {v/1e6:.1f} MW/m²  ->  {t_peak:.1f} K")

    else:
        print("=== RUNNING MULTI-MATERIAL SIMULATION ===")
        if args.material == "all":
            results = compare_materials(MATERIAL_LIB, BOUNDARY_CFG, GRID_CFG)
        else:
            single_lib = {args.material: MATERIAL_LIB[args.material]}
            results = compare_materials(single_lib, BOUNDARY_CFG, GRID_CFG)
            
        temp_chart(results)
        print("\nResults summary:")
        for name, res in results.items():
            t_crit_str = f"{res['t_critical']:.1f} s" if res['t_critical'] else "None (>90 s)"
            print(f"  {name.capitalize():<10} | t_critical: {t_crit_str:<12} | Peak T_inner: {res['T_inner_max']:.1f} K")


if __name__ == "__main__":
    main()
