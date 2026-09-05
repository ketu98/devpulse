from __future__ import annotations

import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


WIDTH = 1200
HEIGHT = 1200


def _font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate_diagram(title: str, steps: list[str], output_path: Path):
    """
    Render a clean square technical flow diagram.
    Uses no external image service and is deterministic/free.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    title_font = _font(52, bold=True)
    subtitle_font = _font(25, bold=False)
    node_font = _font(30, bold=True)
    footer_font = _font(22, bold=False)

    # Header
    wrapped_title = _wrap(draw, title, title_font, 1030)
    y = 55
    for line in wrapped_title[:2]:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (WIDTH - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, fill=(18, 38, 63), font=title_font)
        y += 62

    subtitle = "DevPulse • Practical Engineering POC"
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    draw.text(
        ((WIDTH - (bbox[2]-bbox[0]))/2, y+6),
        subtitle,
        fill=(80, 94, 110),
        font=subtitle_font
    )

    steps = [s.strip() for s in steps if s and s.strip()]
    if not steps:
        steps = ["Problem", "Implementation", "Validation", "Result"]
    steps = steps[:6]

    top = 255
    bottom = 1010
    node_h = 105
    node_w = 760
    gap = max(28, (bottom - top - node_h * len(steps)) // max(1, len(steps)-1))

    center_x = WIDTH // 2
    y = top

    for idx, step in enumerate(steps):
        x1 = center_x - node_w // 2
        y1 = y
        x2 = center_x + node_w // 2
        y2 = y + node_h

        # Rounded node
        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=28,
            fill=(239, 247, 255),
            outline=(50, 121, 200),
            width=4
        )

        # Number bubble
        bubble_r = 28
        bx = x1 + 48
        by = y1 + node_h // 2
        draw.ellipse(
            [bx-bubble_r, by-bubble_r, bx+bubble_r, by+bubble_r],
            fill=(34, 104, 182)
        )
        number = str(idx + 1)
        nb = draw.textbbox((0, 0), number, font=node_font)
        draw.text(
            (bx-(nb[2]-nb[0])/2, by-(nb[3]-nb[1])/2-2),
            number,
            fill="white",
            font=node_font
        )

        lines = _wrap(draw, step, node_font, node_w - 150)
        ty = y1 + 25
        for line in lines[:2]:
            draw.text((x1 + 100, ty), line, fill=(25, 49, 77), font=node_font)
            ty += 38

        if idx < len(steps) - 1:
            cx = center_x
            arrow_top = y2 + 10
            arrow_bottom = y2 + gap - 10
            draw.line([cx, arrow_top, cx, arrow_bottom], fill=(34, 104, 182), width=5)
            draw.polygon(
                [(cx-13, arrow_bottom-12), (cx+13, arrow_bottom-12), (cx, arrow_bottom+8)],
                fill=(34, 104, 182)
            )

        y += node_h + gap

    footer = "Generated automatically from the accompanying DevPulse mini-POC."
    fb = draw.textbbox((0, 0), footer, font=footer_font)
    draw.text(
        ((WIDTH-(fb[2]-fb[0]))/2, 1128),
        footer,
        fill=(105, 115, 125),
        font=footer_font
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", optimize=True)
    return output_path
