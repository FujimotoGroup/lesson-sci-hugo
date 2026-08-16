"""Lesson 1: build the smallest SymHam Hamiltonian."""

import numpy as np

import symham as sh


lattice = 2.0 * np.eye(3, dtype=float)
positions = np.array([[0.0, 0.0, 0.0]], dtype=float)
numbers = ["Si"]
orbitals = [sh.OrbitalRep.s()]

model = sh.TBModel(
    lattice,
    positions,
    numbers,
    orbitals,
    symprec=1e-6,
)
model.enumerate_bonds(
    r_cut=0.0,
    T_range=0,
    include_onsite=False,
)
model.classify_bonds_by_symmetry()
model.build_bond_orbit_basis()

print("param_names:", model.param_names)

H_R = model.real_space_hamiltonian(
    {},
    atomic_onsite={("Si", "s"): 0.2},
)
print("H_R[(0, 0, 0)]:")
print(H_R[(0, 0, 0)])

gamma = np.array([0.0, 0.0, 0.0], dtype=float)
H_gamma = model.Hk(gamma, H_R)
eigenvalues = np.linalg.eigvalsh(H_gamma)
print("eigenvalues at Gamma:", eigenvalues)
