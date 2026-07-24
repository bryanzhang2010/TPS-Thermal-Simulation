# 1D Thermal Protection System (TPS) Simulation

A 1D explicit finite difference solver for transient thermal conduction through atmospheric entry heat shield materials: Aluminum 6061-T6, Alumina Ceramic, and Phenolic-Impregnated Carbon Ablator (PICA).

![TPS Surface Temperature Comparison](figures/comparison.png)

---

## Overview

This project models heat propagation across a 1D spatial domain subject to high aerodynamic thermal flux (1.0 MW/m²). It calculates stability bounds, compares time-to-failure metrics against structural temperature constraints (600 K), and validates numerical approximations against closed-form analytical solutions.

## Architecture

* `config.py`: Material thermal properties, boundary conditions, and spatial discretization limits.
* `solver.py`: 1D explicit forward-time centered-space (FTCS) heat conduction engine.
* `analysis.py`: Analytical validation routines and parameter sweep functions.
* `visualise.py`: Matplotlib plotting tools for profile and comparison outputs.
* `main.py`: Command-line driver for execution modes.

---

## Governing Equations

### Heat Conduction
Heat diffusion through the material domain is governed by Fourier's 1D heat equation:

$$\frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2}, \quad \alpha = \frac{k}{\rho c_p}$$

### Discretization & Stability
The domain is discretized across N = 60 spatial nodes. To guarantee stability in explicit time integration, time step size Δt satisfies the Courant-Friedrichs-Lewy (CFL) stability criterion:

$$r = \frac{\alpha \Delta t}{\Delta x^2} \le 0.5$$

### Boundary Conditions
* Outer Surface (x = 0): Constant heat flux boundary, -k (∂T/∂x)|x=0 = q_flux
* Inner Surface (x = L): Adiabatic / insulated back face, (∂T/∂x)|x=L = 0

---

## Execution

### Run Material Comparison
Simulate temperature distributions across all materials over 90 seconds:
```bash
python3 main.py --material all