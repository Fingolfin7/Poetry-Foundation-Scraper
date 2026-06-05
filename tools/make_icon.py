"""Generate a valid multi-size Windows .ico for the app.

This avoids brittle manual .ico creation and ensures PyInstaller accepts it.
"""

from __future__ import annotations

import os

from PIL import Image, ImageDraw


def main() -> None:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(repo_root, "assets", "app_icon.ico")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []

    for s in sizes:
        img = Image.new("RGBA", (s, s), (18, 24, 38, 255))
        d = ImageDraw.Draw(img)

        # Simple "quill"/feather-ish mark
        pad = max(2, s // 8)
        d.ellipse((pad, pad, s - pad, s - pad), outline=(255, 255, 255, 230), width=max(1, s // 16))
        d.line((s * 0.30, s * 0.68, s * 0.72, s * 0.28), fill=(255, 255, 255, 235), width=max(1, s // 12))
        d.line((s * 0.52, s * 0.48, s * 0.78, s * 0.48), fill=(255, 255, 255, 200), width=max(1, s // 18))

        images.append(img)

    # Save multi-resolution .ico
    images[0].save(out_path, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

