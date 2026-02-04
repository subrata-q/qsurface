from qsurface.main import initialize
from qsurface.svg_viz import draw_lattice_svg
import random

random.seed(40203)

d = 5
num_rounds = d

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
draw_lattice_svg(code, filename="faulty_initial.svg", round_index=0, save_png=False)

print(f"\nRunning simulation for {num_rounds} rounds (3D block)...")

# 1. Introduce errors (Simulates all layers)
# In FaultyMeasurements, random_errors runs through all 'layers' steps.
print("\nSyndrome during error injection before decoding:")


code.random_errors(
    p_bitflip=0.02, p_phaseflip=0.02, p_bitflip_plaq=0.01, p_bitflip_star=0.01
)

syndromes = decoder.get_syndrome()
print(f"X-type syndromes: {syndromes[0]}")
print(f"Z-type syndromes: {syndromes[1]}")

# Extraction logic for x, y, round
with open("syndromes_locations.txt", "w") as f:
    f.write("X-type syndromes\n(x, y, round):\n")
    for s in syndromes[0]:
        x, y = s.loc
        f.write(f"({x}, {y}, {int(s.z)})\n")
    f.write("\nZ-type syndromes\n(x, y, round):\n")
    for s in syndromes[1]:
        x, y = s.loc
        f.write(f"({x}, {y}, {int(s.z)})\n")
print("Saved syndrome locations to syndromes_locations.txt")

draw_lattice_svg(
    code,
    filename=f"faulty_error.svg",
    round_index=num_rounds - 1,
    save_png=False,
)

states_before_correction = {}
for it in range(num_rounds):
    states_before_correction[it] = {}
    for loc in code.data_qubits[it].keys():
        qubit = code.data_qubits[it][loc]
        states_before_correction[it][loc] = {
            "x": qubit.state["x"],
            "z": qubit.state["z"],
        }

decoder.decode()
syndromes = decoder.get_syndrome()
print("Syndrome after decoding:")
print(f"X-type syndromes: {syndromes[0]}")
print(f"Z-type syndromes: {syndromes[1]}")


draw_lattice_svg(
    code,
    filename=f"faulty_final.svg",
    round_index=num_rounds - 1,
    save_png=False,
)

corrections_x = {}
corrections_z = {}
corrections_both = {}

# for it in range(num_rounds):
it = num_rounds - 1  # only the last round
corrections_x[it] = []
corrections_z[it] = []
corrections_both[it] = []
for loc in code.data_qubits[it].keys():
    qubit = code.data_qubits[it][loc]
    x_before = states_before_correction[it][loc]["x"]
    z_before = states_before_correction[it][loc]["z"]
    x_after = qubit.state["x"]
    z_after = qubit.state["z"]

    # Detect if this qubit was corrected (state changed)
    x_corrected = x_before != x_after
    z_corrected = z_before != z_after

    if x_corrected and z_corrected:
        corrections_both[it].append(loc)
    elif x_corrected:
        corrections_x[it].append(loc)
    elif z_corrected:
        corrections_z[it].append(loc)


it = num_rounds - 1
print(f"\nCorrections after round {it}")
if corrections_x[it]:
    print(f"X-corrections applied at: {sorted(corrections_x[it])}")
else:
    print("X-corrections applied at: (none)")

if corrections_z[it]:
    print(f"Z-corrections applied at: {sorted(corrections_z[it])}")
else:
    print("Z-corrections applied at: (none)")

if corrections_both[it]:
    print(f"Both X & Z corrections applied at: {sorted(corrections_both)}")

total_corrections = (
    len(corrections_x[it]) + len(corrections_z[it]) + len(corrections_both[it])
)
print(f"\nTotal qubits corrected: {total_corrections}")

with open("corrections.txt", "w") as f:
    f.write("X-corrections\n(x, y, round):\n")
    for loc in corrections_x[it]:
        x, y = loc
        f.write(f"({x}, {y}, {int(it)})\n")
    f.write("\nZ-corrections\n(x, y, round):\n")
    for loc in corrections_z[it]:
        x, y = loc
        f.write(f"({x}, {y}, {int(it)})\n")
    f.write("\nBoth X & Z corrections\n(x, y, round):\n")
    for loc in corrections_both[it]:
        x, y = loc
        f.write(f"({x}, {y}, {int(it)})\n")


code.logical_state
print("Logical error occurred: ", not code.no_error)
