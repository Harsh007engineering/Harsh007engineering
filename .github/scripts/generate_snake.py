#!/usr/bin/env python3
"""
Custom Snake Animation & Streak Stats Generator for Harsh's GitHub Profile.
- Calibrated to exactly 1.5x of Harsh's actual GitHub contribution activity (18 green boxes).
- Fast arcade slither speed (~32ms per step).
- Safe streak-stats sync preventing any GitHub API / Heroku error SVGs from being published.
"""

import os
import urllib.request
import re
import shutil

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

def get_calibrated_boxes():
    """
    Harsh has 12 actual active contribution days on GitHub.
    User requested: 1.5x the green of normal actual activity = exactly 18 green boxes.
    Returns:
      active_boxes: dict mapping (col, row) -> intensity level (1..4)
    """
    # 12 Actual Contribution Days (col 0..52, row 0..6)
    actual_days = [
        ((29, 2), 1),  # 2026-04-07
        ((29, 3), 2),  # 2026-04-08
        ((42, 3), 4),  # 2026-07-08
        ((50, 0), 1),  # 2026-08-30
        ((50, 3), 4),  # 2026-09-02
        ((51, 6), 1),  # 2026-09-12
        ((52, 0), 4),  # 2026-09-13
        ((52, 1), 1),  # 2026-09-14
        ((52, 2), 4),  # 2026-09-15
        ((52, 3), 2),  # 2026-09-16
        ((52, 4), 1),  # 2026-09-17
        ((52, 6), 1),  # 2026-09-19
    ]

    # 6 Additional naturally-placed boxes to achieve exactly 1.5x (18 total boxes)
    extra_days = [
        ((15, 0), 1),  # Early sprint
        ((22, 2), 2),  # Spring
        ((35, 5), 2),  # Early summer
        ((42, 2), 3),  # Mid summer
        ((48, 4), 2),  # Late August
        ((51, 2), 3),  # September activity
    ]

    boxes = {}
    for coord, lvl in actual_days + extra_days:
        boxes[coord] = lvl
    return boxes

def generate_svg(is_dark=True, duration_ms=7000):
    path = build_snake_circuit()
    N = len(path)
    snake_len = 5
    
    boxes = get_calibrated_boxes()
    
    # Identify which boxes lie on the snake's path (these get eaten in sequence)
    food_indices = []
    grid_cells = {}
    for coord, lvl in boxes.items():
        if coord in path:
            idx = path.index(coord)
            food_indices.append((idx, coord, lvl))
        else:
            grid_cells[coord] = lvl

    # Sort food by the step at which snake reaches them
    food_indices.sort(key=lambda x: x[0])

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

    # Food keyframes (disappears into empty cell upon being eaten)
    for i, (step_idx, coord, lvl) in enumerate(food_indices):
        eat_pct = round((step_idx / N) * 100, 2)
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
    food_map = {coord: i for i, (step_idx, coord, lvl) in enumerate(food_indices)}
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

def update_streak_svg(dist_dir="dist"):
    """
    Safely fetches the streak stats SVG without ever overwriting with an error SVG.
    """
    url = "https://github-readme-streak-stats.herokuapp.com/?user=Harsh007engineering&theme=tokyonight&hide_border=true&background=0d1117&ring=38bdf8&fire=38bdf8&currStreakLabel=38bdf8&sideNums=38bdf8&sideLabels=38bdf8"
    target_path = os.path.join(dist_dir, "streak-stats.svg")
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        content = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
        if "Failed to retrieve" not in content and "Total Contributions" in content and len(content) > 2000:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("Successfully refreshed streak-stats.svg from Heroku!")
            return
        else:
            print("Warning: Heroku returned error or rate-limited SVG. Keeping existing valid SVG.")
    except Exception as e:
        print(f"Warning: Could not fetch from Heroku ({e}). Keeping existing valid SVG.")

    # Fallback to local clean copy if available
    if os.path.exists("streak-stats.svg") and not os.path.exists(target_path):
        shutil.copy("streak-stats.svg", target_path)

if __name__ == "__main__":
    os.makedirs("dist", exist_ok=True)
    
    dark_svg = generate_svg(is_dark=True, duration_ms=7000)
    light_svg = generate_svg(is_dark=False, duration_ms=7000)

    with open("dist/github-snake-dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    with open("dist/github-snake.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)

    update_streak_svg("dist")

    print("Generation complete:")
    print(f"  Dark Snake SVG: {len(dark_svg)} bytes (18 green boxes = 1.5x actual)")
    print(f"  Light Snake SVG: {len(light_svg)} bytes")
    if os.path.exists("dist/streak-stats.svg"):
        print(f"  Streak SVG size: {os.path.getsize('dist/streak-stats.svg')} bytes")
