import drawsvg as draw


def draw_lattice_svg(
    code,
    filename="lattice.svg",
    unit_width=100,
    padding=50,
    round_index=0,
    save_png=False,
):
    """
    Draws the surface code lattice to an SVG file with specific styling and error coloring.

    Parameters:
        code: qsurface code object
        filename: Output filename (e.g., "lattice.svg")
        unit_width: scaling factor for coordinates (pixels per unit distance)
        padding: Padding around the lattice
        round_index: Measurement round index (default: 0)
        save_png: If True, also save a PNG version (requires cairosvg)
    """

    # 1. Gather Data and Ancilla locations for the specified round
    data_qubits = code.data_qubits[round_index]
    ancilla_qubits = code.ancilla_qubits[round_index]

    data_locs = list(data_qubits.keys())
    ancilla_locs = list(ancilla_qubits.keys())

    if not data_locs:
        print("No data qubits to draw.")
        return

    all_locs = data_locs + ancilla_locs
    xs = [loc[0] for loc in all_locs]
    ys = [loc[1] for loc in all_locs]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # 2. Setup Canvas
    width = (max_x - min_x) * unit_width + 2 * padding
    height = (max_y - min_y) * unit_width + 2 * padding

    # Check if height/width are 0 (single point), add some default size
    if width == 2 * padding:
        width += unit_width
    if height == 2 * padding:
        height += unit_width

    d = draw.Drawing(width, height, origin="top-left")

    # Styling constants (from draw_rot_surface.py)
    data_radius = 15
    ancilla_radius = 12
    z_color = "#dbb2af"  # Blueish-Red (Z-type)
    x_color = "#bcbde6"  # Reddish-Blue (X-type)
    data_color = "#813991ff"  #
    data_text_color = "#dcdde1"
    connection_default_color = "#dcdde1"

    # Helper to map simulation coords to SVG coords (flipping Y because SVG origin is top-left)
    def get_coords(loc):
        x, y = loc
        # Normalize x, y relative to min
        rel_x = x - min_x
        rel_y = y - min_y

        # Scale
        svg_x = padding + rel_x * unit_width
        # Flip Y: standard generic coordinates usually have Y going up, SVG has Y going down.
        # But let's check input coords. If they are matrix indices (row, col), Y goes down.
        # qsurface often uses (x,y) cartesian.
        # Let's assume (x,y) cartesian where Y is up.
        # To map Y_cart (min_y to max_y) to Y_svg (height-padding to padding)
        svg_y = height - (padding + rel_y * unit_width)
        return svg_x, svg_y

    # 3. Connection Layer (Lines)
    # In rotated surface code:
    # - Data qubits are at integer coordinates (0,0), (0,1), (1,0), etc.
    # - Ancilla qubits are at half-integer coordinates (0.5, 0.5), (0.5, 1.5), etc.
    # - Each data qubit connects to nearby ancillas at distance sqrt(0.5^2 + 0.5^2) ≈ 0.707
    # - Distance squared = 0.5

    connections = draw.Group(id="connections", stroke_width=3)

    # Connect each data qubit to nearby ancilla qubits
    for d_loc, d_qubit in data_qubits.items():
        dx, dy = d_loc

        # Check all ancilla qubits for proximity
        for a_loc, a_qubit in ancilla_qubits.items():
            ax, ay = a_loc

            # Calculate distance squared
            dist_sq = (dx - ax) ** 2 + (dy - ay) ** 2

            # In rotated surface code, valid connections have dist_sq = 0.5
            # Allow small tolerance for floating point
            if 0.4 < dist_sq < 0.6:  # This catches the 0.5 distance
                # Determine edge color based on errors
                stroke_color = connection_default_color
                stroke_width = 3

                x_err = d_qubit.state.get("x", 0)
                z_err = d_qubit.state.get("z", 0)
                anc_type = a_qubit.state_type  # "x" or "z"

                # User request: Z error -> highlight edge to Z-ancilla
                # X error -> highlight edge to X-ancilla
                if z_err and anc_type == "z":
                    stroke_color = "#ff5e00ff"
                    stroke_width = 5
                elif x_err and anc_type == "x":
                    stroke_color = "#ff8c00ff"
                    stroke_width = 5

                # Draw the connection
                x1, y1 = get_coords(d_loc)
                x2, y2 = get_coords(a_loc)
                connections.append(
                    draw.Line(
                        x1, y1, x2, y2, stroke=stroke_color, stroke_width=stroke_width
                    )
                )

    d.append(connections)

    # 4. Draw Ancilla Qubits
    ancilla_group = draw.Group(id="ancilla-qubits")
    for loc, ancilla in ancilla_qubits.items():
        ax, ay = get_coords(loc)
        anc_type = ancilla.state_type

        # Shapes: Square for X, Diamond/Rhombus for Z (or similar distinct shapes)
        # Using draw_rot_surface.py style: Z=BlueishRed, X=ReddishBlue.
        # But let's follow the user prompts if implied, otherwise stick to nice colors.

        fill = z_color if anc_type == "z" else x_color

        # Check syndrome status for highlighting?
        # User didn't explicitly ask to change node color, just edge color.
        # But generally useful to see syndrome.
        has_syndrome = ancilla.syndrome
        stroke = "red" if has_syndrome else "grey"
        stroke_w = 4 if has_syndrome else 0.5

        # Draw ancilla as circle
        ancilla_group.append(
            draw.Circle(
                ax,
                ay,
                ancilla_radius,
                fill=fill,
                stroke=stroke,
                stroke_width=stroke_w,
            )
        )

        # Add label
        label = "Z" if anc_type == "z" else "X"
        ancilla_group.append(
            draw.Text(
                label, 10, ax, ay, center=True, fill="grey", dominant_baseline="middle"
            )
        )

    d.append(ancilla_group)

    # 5. Draw Data Qubits
    data_group = draw.Group(id="data-qubits")
    for loc, qubit in data_qubits.items():
        dx, dy = get_coords(loc)

        # Check error state to display label
        x_err = qubit.state.get("x", 0)
        z_err = qubit.state.get("z", 0)

        # Determine error label
        error_label = None
        if x_err and z_err:
            error_label = "Y"
        elif x_err:
            error_label = "X"
        elif z_err:
            error_label = "Z"

        data_group.append(
            draw.Circle(
                dx, dy, data_radius, fill=data_color, stroke="#2c3e50", stroke_width=0.5
            )
        )

        # Add error label if present
        if error_label:
            data_group.append(
                draw.Text(
                    error_label,
                    14,
                    dx,
                    dy,
                    center=True,
                    fill="#ffc7bfff",
                    font_weight="bold",
                    dominant_baseline="middle",
                )
            )

    d.append(data_group)

    # Save - append round index to filename
    if round_index > 0:
        # Insert round index before file extension
        base_name, ext = (
            filename.rsplit(".", 1) if "." in filename else (filename, "svg")
        )
        filename_with_round = f"{base_name}_{round_index}.{ext}"
    else:
        filename_with_round = filename

    # Save SVG
    d.save_svg(filename_with_round)
    print(f"Saved lattice visualization to {filename_with_round}")

    # Save PNG if requested
    if save_png:
        try:
            import cairosvg

            png_filename = filename_with_round.replace(".svg", ".png")
            cairosvg.svg2png(url=filename_with_round, write_to=png_filename)
            print(f"Saved PNG version to {png_filename}")
        except ImportError:
            print("Warning: cairosvg not installed. Install with: pip install cairosvg")
            print("PNG export skipped.")
        except Exception as e:
            print(f"Warning: Failed to save PNG: {e}")


if __name__ == "__main__":
    pass
