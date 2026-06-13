#!/usr/bin/env python3
"""Genera cinestudio.ico — clapperboard sobre disco con degradado violeta→cian.
Multi-resolución (16..256) para que se vea nítido en barra de tareas y escritorio.
"""
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SS = 1024  # render grande y luego downscale = bordes suaves


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def render(size=SS):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c1, c2 = (124, 92, 255), (34, 211, 238)  # acc → acc2
    # disco con degradado diagonal (franjas finas)
    pad = int(size * 0.06)
    r = (size - 2 * pad) // 2
    cx = cy = size // 2
    for i in range(size):
        t = i / size
        d.line([(0, i), (size, i)], fill=lerp((22, 16, 40), (8, 13, 18), t))
    # círculo base
    disc = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    steps = r
    for i in range(steps, 0, -1):
        t = i / steps
        col = lerp(c1, c2, 1 - t)
        dd.ellipse([cx - i, cy - i, cx + i, cy + i], fill=col + (255,))
    img.alpha_composite(disc)
    # claqueta: barra superior con dientes diagonales
    bw = int(r * 1.55)
    bh = int(r * 0.34)
    bx = cx - bw // 2
    by = cy - int(r * 0.62)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(bh * 0.18),
                        fill=(15, 17, 24, 255))
    # dientes blancos diagonales
    n = 7
    tw = bw / n
    for k in range(n):
        x0 = bx + k * tw
        d.polygon([(x0, by), (x0 + tw * 0.55, by), (x0 + tw * 0.15, by + bh),
                   (x0 - tw * 0.4, by + bh)], fill=(231, 236, 245, 255))
    # cuerpo de la claqueta (rectángulo oscuro bajo la barra)
    cy0 = by + bh + int(r * 0.04)
    cy1 = cy + int(r * 0.66)
    d.rounded_rectangle([bx, cy0, bx + bw, cy1], radius=int(bh * 0.18),
                        fill=(18, 21, 30, 235))
    # triángulo play centrado, degradado simulado con color medio
    pr = int(r * 0.30)
    mid = lerp(c1, c2, 0.5)
    d.polygon([(cx - pr * 0.5, (cy0 + cy1) // 2 - pr),
               (cx - pr * 0.5, (cy0 + cy1) // 2 + pr),
               (cx + pr, (cy0 + cy1) // 2)], fill=mid + (255,))
    return img


def main():
    big = render()
    sizes = [256, 128, 64, 48, 32, 16]
    frames = [big.resize((s, s), Image.LANCZOS) for s in sizes]
    out = HERE / "cinestudio.ico"
    frames[0].save(out, format="ICO", sizes=[(s, s) for s in sizes],
                   append_images=frames[1:])
    print("escrito", out)


if __name__ == "__main__":
    main()
