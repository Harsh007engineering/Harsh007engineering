#!/usr/bin/env python3
"""
High-Speed Cyber-Arcade Snake Generator for GitHub Profile.
Creates an appealing, fast-paced snake game animation with a lush, active contribution grid.
Generates:
  - dist/github-snake-dark.svg (Dark mode)
  - dist/github-snake.svg (Light mode)
"""

import os
import random

def build_snake_circuit():
    """
    Creates a non-self-colliding closed loop of orthogonal steps on a 53x7 grid.
    Returns list of (col, row) coordinates.
    """
    corners = [
        # Top rows weave
        (0, 0), (20, 0), (20, 2), (10, 2), (10, 1), (30, 1), (30, 0), (52, 0),
        # Right descent & loops
        (52, 3), (42, 3), (42, 2), (50, 2), (50, 4), (52, 4), (52, 6),
        # Bottom weave
        (35, 6), (35, 5), (45, 5), (45, 6), (20, 6), (20, 4), (25, 4), (25, 5), (15, 5),
        # Left weave & close loop
        (15, 6), (0, 6), (0, 3), (5, 3), (5, 4), (8, 4), (8, 3), (2, 3), (2, 1), (0, 1), (0, 0)
    ]
    
    path = []
    for i in range(len(corners) - 1):
        c1, r1 = corners[i]
        c2, r2 = corners[i + 1]
        cur_c, cur_r = c1, r1
        while (cur_c, cur_r) != (c2, r2):
            if cur_c < c2: cur_c += 1
            elif cur_c > c2: cur_c -= 1
            elif cur_r < r2: cur_r += 1
            elif cur_r > r2: cur_r -= 1
            path.append((cur_c, cur_r))
            
    return path

def generate_svg(is_dark=True, duration_ms=7200):
    path = build_snake_circuit()
    N = len(path)
    snake_len = 5
    
    # Select food cells along path (eaten in sequence)
    food_indices = []
    eaten_cells = set()
    for idx in range(3, N, 6):
        coord = path[idx]
        if coord not in eaten_cells:
            food_indices.append((idx, coord))
            eaten_cells.add(coord)
            
    # Deterministic pseudo-random seed for natural contribution pattern
    rng = random.Random(42)
    
    # Populate the rest of the board with lush green boxes (levels 1..4)
    # Total cells: 53 * 7 = 371
    grid_cells = {}
    for col in range(53):
        for row in range(7):
            coord = (col, row)
            if coord in eaten_cells:
                continue
            # Realistic commit activity pattern:
            # More active in recent weeks (col 30..52), steady streaks throughout
            prob = 0.32
            if col > 35:
                prob = 0.58
            elif col % 4 == 0 or col % 5 == 0:
                prob = 0.44
            elif row in [1, 2, 3, 4]:
                prob = 0.40
                
            if rng.random() < prob:
                weights = [0.38, 0.32, 0.20, 0.10]
                lvl = rng.choices([1, 2, 3, 4], weights=weights)[0]
                grid_cells[coord] = lvl

    # Theme colors
    if is_dark:
        bg_color = "#0d1117"
        empty_cell = "#161b22"
        border_color = "rgba(255, 255, 255, 0.05)"
        c1 = "#0e4429"  # Level 1
        c2 = "#006d32"  # Level 2
        c3 = "#26a641"  # Level 3
        c4 = "#39d353"  # Level 4
        # Snake: Glowing electric cyan / vibrant neon trail
        s_head = "#38bdf8"
        s_body1 = "#60a5fa"
        s_body2 = "#818cf8"
        s_body3 = "#a855f7"
        s_tail = "#c084fc"
        glow_color = "#38bdf8"
        bar_bg = "#21262d"
        bar_fill = "#38bdf8"
    else:
        bg_color = "#ffffff"
        empty_cell = "#ebedf0"
        border_color = "rgba(27, 31, 35, 0.06)"
        c1 = "#9be9a8"
        c2 = "#40c463"
        c3 = "#30a14e"
        c4 = "#216e39"
        # Snake: Crisp blue / indigo gradient
        s_head = "#0284c7"
        s_body1 = "#0ea5e9"
        s_body2 = "#3b82f6"
        s_body3 = "#6366f1"
        s_tail = "#8b5cf6"
        glow_color = "#0284c7"
        bar_bg = "#e5e7eb"
        bar_fill = "#0284c7"

    # Build CSS
    css = [
        f":root{{--cb:{border_color};--ce:{empty_cell};--c1:{c1};--c2:{c2};--c3:{c3};--c4:{c4};}}",
        f".c{{shape-rendering:geometricPrecision;fill:var(--ce);stroke-width:1px;stroke:var(--cb);width:12px;height:12px;rx:2.5px;ry:2.5px;}}",
        ".c.cg1{fill:var(--c1);}",
        ".c.cg2{fill:var(--c2);}",
        ".c.cg3{fill:var(--c3);}",
        ".c.cg4{fill:var(--c4);}",
        f".s{{shape-rendering:geometricPrecision;animation:none {duration_ms}ms linear infinite;}}",
        f".s0 rect{{fill:{s_head};}}",
        f".s1{{fill:{s_body1};animation-name:s1;}}",
        f".s2{{fill:{s_body2};animation-name:s2;}}",
        f".s3{{fill:{s_body3};animation-name:s3;}}",
        f".s4{{fill:{s_tail};animation-name:s4;}}",
        f".s0{{animation-name:s0;}}",
    ]

    # Food keyframes (smooth disappearance when eaten)
    for i, (step_idx, coord) in enumerate(food_indices):
        eat_pct = round((step_idx / N) * 100, 2)
        lvl = rng.choice([2, 3, 4])
        css.append(f".c.food{i}{{fill:var(--c{lvl});animation:none {duration_ms}ms linear infinite;animation-name:food{i};}}")
        css.append(f"@keyframes food{i}{{{{0%,{max(0, eat_pct - 0.05):.2f}%{{fill:var(--c{lvl});}}{eat_pct:.2f}%,100%{{fill:var(--ce);}}}}}}")

    # Snake segment keyframes (high-speed coordinates)
    for k in range(snake_len):
        kf_stops = []
        for t in range(N):
            pct = round((t / N) * 100, 2)
            c, r = path[(t - k) % N]
            x = c * 16
            y = r * 16
            kf_stops.append(f"{pct:.2f}%{{transform:translate({x}px,{y}px);}}")
        c0, r0 = path[(-k) % N]
        kf_stops.append(f"100%{{transform:translate({c0 * 16}px,{r0 * 16}px);}}")
        css.append(f"@keyframes s{k}{{{''.join(kf_stops)}}}")

    # Build SVG
    svg_parts = [
        f'<svg viewBox="-16 -24 880 180" width="880" height="180" xmlns="http://www.w3.org/2000/svg">',
        f'<defs>',
        f'<filter id="glow" x="-20%" y="-20%" width="140%" height="140%">',
        f'<feDropShadow dx="0" dy="0" stdDeviation="1.8" flood-color="{glow_color}" flood-opacity="0.7"/>',
        f'</filter>',
        f'</defs>',
        f'<style>{"".join(css)}</style>',
        f'<g>',
    ]

    # Render all 371 cells (53 cols x 7 rows)
    food_map = {coord: i for i, (step_idx, coord) in enumerate(food_indices)}
    for col in range(53):
        for row in range(7):
            coord = (col, row)
            cx = 2 + 16 * col
            cy = 2 + 16 * row
            if coord in food_map:
                food_id = food_map[coord]
                svg_parts.append(f'<rect class="c food{food_id}" x="{cx}" y="{cy}"/>')
            elif coord in grid_cells:
                lvl = grid_cells[coord]
                svg_parts.append(f'<rect class="c cg{lvl}" x="{cx}" y="{cy}"/>')
            else:
                svg_parts.append(f'<rect class="c" x="{cx}" y="{cy}"/>')

    # Status / score bar at bottom
    svg_parts.append(f'<rect x="2" y="128" width="832" height="6" rx="3" fill="{bar_bg}"/>')
    svg_parts.append(f'<rect x="2" y="128" width="832" height="6" rx="3" fill="{bar_fill}" opacity="0.9"/>')

    # Snake segments (Tail to Head)
    svg_parts.append(f'<rect class="s s4" x="3" y="3" width="10" height="10" rx="3"/>')
    svg_parts.append(f'<rect class="s s3" x="2.5" y="2.5" width="11" height="11" rx="3.5"/>')
    svg_parts.append(f'<rect class="s s2" x="2" y="2" width="12" height="12" rx="4"/>')
    svg_parts.append(f'<rect class="s s1" x="1.5" y="1.5" width="13" height="13" rx="4.5"/>')
    
    # Head with glowing cyber eyes
    svg_parts.append(f'<g class="s s0" filter="url(#glow)">')
    svg_parts.append(f'<rect x="1" y="1" width="14" height="14" rx="5"/>')
    svg_parts.append(f'<circle cx="5" cy="5" r="1.5" fill="#0b0f19"/>')
    svg_parts.append(f'<circle cx="11" cy="5" r="1.5" fill="#0b0f19"/>')
    svg_parts.append(f'<circle cx="5.6" cy="4.6" r="0.6" fill="#ffffff"/>')
    svg_parts.append(f'<circle cx="11.6" cy="4.6" r="0.6" fill="#ffffff"/>')
    svg_parts.append(f'</g>')

    svg_parts.append('</g>')
    svg_parts.append('</svg>')

    return "".join(svg_parts)

if __name__ == "__main__":
    # Duration of 7200ms for 216 steps = ~33ms per step (Fast and smooth arcade speed!)
    dark_svg = generate_svg(is_dark=True, duration_ms=7200)
    light_svg = generate_svg(is_dark=False, duration_ms=7200)

    os.makedirs("dist", exist_ok=True)
    with open("dist/github-snake-dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    with open("dist/github-snake.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)

    print(f"Generated SVGs successfully:")
    print(f"  Dark SVG: {len(dark_svg)} bytes")
    print(f"  Light SVG: {len(light_svg)} bytes")
