from qsurface.main import initialize, run
from qsurface.svg_viz import draw_lattice_svg
import random

# random.seed(40203)


d = 5

print("\n" + "─" * 40)
print("INITIALIZING CODE...")
print("─" * 40)

code, decoder = initialize(
    (d, d),
    "rotated",
    "unionfind",
    enabled_errors=["pauli"],
    initial_states=(0, 0),
    plotting=False,
)


draw_lattice_svg(code, filename="initial_state.svg", save_png=True)

# run(
#     code,
#     decoder,
#     error_rates={"p_bitflip": 0.1, "p_phaseflip": 0.1},
#     decode_initial=False,
#     seed=402,
# )

print("\n" + "─" * 40)
print("INTRODUCING ERRORS...")
print("─" * 40)

code.random_errors(p_bitflip=0.1, p_phaseflip=0.1)
draw_lattice_svg(code, filename="error_state.svg", save_png=True)

# Store state BEFORE correction for comparison
states_before_correction = {}
for loc in code.data_qubits[0].keys():
    qubit = code.data_qubits[0][loc]
    states_before_correction[loc] = {"x": qubit.state["x"], "z": qubit.state["z"]}

print("\n" + "─" * 40)
print("SYNDROME BEFORE CORRECTION")
print("─" * 40)
syndrome_before = decoder.get_syndrome()
print(f"X-type syndromes: {syndrome_before[0]}")
print(f"Z-type syndromes: {syndrome_before[1]}")

print("\n" + "─" * 40)
print("APPLYING DECODER...")
print("─" * 40)
decoder.decode()

print("\n" + "─" * 40)
print("SYNDROME AFTER CORRECTION")
print("─" * 40)
syndrome_after = decoder.get_syndrome()
print(f"X-type syndromes: {syndrome_after[0]}")
print(f"Z-type syndromes: {syndrome_after[1]}")

# Compare states to find where corrections were applied
print("\n" + "─" * 40)
print("CORRECTIONS APPLIED AT LOCATIONS")
print("─" * 40)

corrections_x = []
corrections_z = []
corrections_both = []

for loc in code.data_qubits[0].keys():
    qubit = code.data_qubits[0][loc]
    x_before = states_before_correction[loc]["x"]
    z_before = states_before_correction[loc]["z"]
    x_after = qubit.state["x"]
    z_after = qubit.state["z"]

    # Detect if this qubit was corrected (state changed)
    x_corrected = x_before != x_after
    z_corrected = z_before != z_after

    if x_corrected and z_corrected:
        corrections_both.append(loc)
    elif x_corrected:
        corrections_x.append(loc)
    elif z_corrected:
        corrections_z.append(loc)

if corrections_x:
    print(f"X-corrections applied at: {sorted(corrections_x)}")
else:
    print("X-corrections applied at: (none)")

if corrections_z:
    print(f"Z-corrections applied at: {sorted(corrections_z)}")
else:
    print("Z-corrections applied at: (none)")

if corrections_both:
    print(f"Both X & Z corrections applied at: {sorted(corrections_both)}")

total_corrections = len(corrections_x) + len(corrections_z) + len(corrections_both)
print(f"\nTotal qubits corrected: {total_corrections}")


draw_lattice_svg(code, filename="final_state.svg", save_png=True)
print("Checking logical state: ", code.logical_state)
print("Logical error occurred: ", not code.no_error)
