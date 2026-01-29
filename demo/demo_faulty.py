from qsurface.main import initialize
from qsurface.svg_viz import draw_lattice_svg
import random

# random.seed(40203)

d = 5
num_rounds = 5

print("\n" + "─" * 60)
print(f"INITIALIZING CODE (d={d}, rounds={num_rounds}, faulty_measurements=True)...")
print("─" * 60)

code, decoder = initialize(
    (d, d),
    "rotated",
    "unionfind",
    enabled_errors=["pauli"],
    faulty_measurements=True,  # Enable 3D/faulty measurements
    layers=num_rounds,  # Specify number of rounds/layers
    initial_states=(0, 0),
    plotting=False,
)

# Draw initial state (round 0 - before any errors)
draw_lattice_svg(code, filename="faulty_initial.svg", round_index=0, save_png=True)

print(f"\nRunning simulation for {num_rounds} rounds (3D block)...")

# 1. Introduce errors (Simulates all layers)
# In FaultyMeasurements, random_errors runs through all 'layers' steps.
print("\nSyndrome during error injection before decoding:")
for it in range(num_rounds):
    code.random_errors(
        p_bitflip=0.01, p_phaseflip=0.01, p_bitflip_plaq=0.01, p_bitflip_star=0.01
    )
    # draw_lattice_svg(
    #     code, filename=f"faulty_error_{it}.svg", round_index=it, save_png=True
    # )
    syndromes = decoder.get_syndrome()
    print(f"X-type syndromes (round {it}): {syndromes[0]}")
    print(f"Z-type syndromes (round {it}): {syndromes[1]}")

decoder.decode()
syndromes = decoder.get_syndrome()
print("Syndrome after decoding:")
print(f"X-type syndromes: {syndromes[0]}")
print(f"Z-type syndromes: {syndromes[1]}")
# draw_lattice_svg(code, filename="faulty_final.svg", save_png=True)
code.logical_state
print("Logical error occurred: ", not code.no_error)
