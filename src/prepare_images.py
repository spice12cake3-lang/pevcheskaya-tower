"""Prepare committed WebP variants. Only this maintenance command needs Pillow.

Run from the project root with a Python environment containing Pillow.
The ordinary build remains dependency-free and uses image-manifest.json.
"""
from pathlib import Path
from hashlib import sha256
import json
import re
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
sources = '\n'.join(p.read_text() for p in (ROOT / 'src').iterdir()
                    if p.suffix in ('.html', '.json'))
paths = sorted(set(re.findall(r'assets/[\w/.-]+\.(?:png|jpe?g)', sources)))
manifest = {}
for source in paths:
    path = ROOT / 'dist' / source
    # Small logos and attribution labels are already lightweight and stay lossless.
    if path.stat().st_size < 30_000:
        continue
    digest = sha256(path.read_bytes() + b'webp-v2-q82').hexdigest()[:12]
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original)
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')
        maximum = min(image.width, 1920)
        widths = sorted(set(w for w in (320, 640, 960, 1280, maximum) if w <= maximum))
        variants = []
        for width in widths:
            height = round(width * image.height / image.width)
            resized = image.resize((width, height), Image.Resampling.LANCZOS)
            target = f'assets/optimized/{path.stem}-{digest}-{width}.webp'
            destination = ROOT / 'dist' / target
            destination.parent.mkdir(exist_ok=True)
            resized.save(destination, 'WEBP', method=6, quality=82, alpha_quality=90)
            variants.append({'src': target, 'width': width, 'bytes': destination.stat().st_size})
        manifest[source] = {'width': image.width, 'height': image.height,
                            'originalBytes': path.stat().st_size, 'variants': variants}
(ROOT / 'src/image-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Prepared {len(manifest)} images, {sum(len(m["variants"]) for m in manifest.values())} variants')
