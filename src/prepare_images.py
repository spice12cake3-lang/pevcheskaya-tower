"""Prepare committed WebP variants. Only this maintenance command needs Pillow.

Run from the project root with a Python environment containing Pillow.
The ordinary build remains dependency-free and uses image-manifest.json.
"""
from pathlib import Path
from hashlib import sha256
import json
import re
import shutil
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
LOSSLESS_SOURCES = {
    'assets/sochi-cover.jpg', 'assets/shop-cover.jpg',
    'assets/apartments.jpg', 'assets/sochi.jpg', 'assets/odessa.jpg', 'assets/karaoke.jpg', 'assets/india.jpg', 'assets/shop.jpg', 'assets/kids-card.jpg',
    *(f'assets/venues/{venue}/{number}.jpg'
      for venue in ('apartments', 'sochi', 'odessa', 'karaoke', 'india', 'shop') for number in (1, 2, 3)),
}
sources = '\n'.join(p.read_text() for p in (ROOT / 'src').iterdir()
                    if p.suffix in ('.html', '.json') and p.name not in ('image-manifest.json', 'menu-previews.json'))
paths = sorted(set(re.findall(r'assets/[\w/.-]+\.(?:png|jpe?g)', sources)))
manifest = {}
for source in paths:
    path = ROOT / 'dist' / source
    # Small logos and attribution labels are already lightweight and stay lossless.
    if path.stat().st_size < 30_000:
        continue
    lossless = source in LOSSLESS_SOURCES
    recipe = b'webp-v3-lossless' if lossless else b'webp-v2-q82'
    digest = sha256(path.read_bytes() + recipe).hexdigest()[:12]
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original)
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')
        maximum = image.width if lossless else min(image.width, 1920)
        extra_widths = (1920, 2560) if lossless and maximum > 2560 else ()
        widths = sorted(set(w for w in (320, 640, 960, 1280, *extra_widths, maximum) if w <= maximum))
        variants = []
        for width in widths:
            # Large JPEG originals are already smaller than a full lossless WebP.
            # Keep their exact bytes; screen-sized variants handle normal visits.
            if lossless and width == maximum and maximum > 2560 and path.suffix.lower() in ('.jpg', '.jpeg'):
                variants.append({'src': source, 'width': width, 'bytes': path.stat().st_size})
                continue
            height = round(width * image.height / image.width)
            target = f'assets/optimized/{path.stem}-{digest}-{width}.webp'
            destination = ROOT / 'dist' / target
            destination.parent.mkdir(exist_ok=True)
            if not destination.exists():
                resized = image if width == image.width else image.resize((width, height), Image.Resampling.LANCZOS)
                if lossless:
                    resized.save(destination, 'WEBP', lossless=True, method=6,
                                 icc_profile=original.info.get('icc_profile', b''))
                else:
                    resized.save(destination, 'WEBP', method=6, quality=82, alpha_quality=90)
            # A lossless WebP of an existing JPEG can be larger than the JPEG.
            # Keep smaller responsive sizes, then use the untouched original.
            if lossless and destination.stat().st_size >= path.stat().st_size:
                if width == image.width:
                    original_target = str(Path(target).with_suffix(path.suffix))
                    shutil.copyfile(path, ROOT / 'dist' / original_target)
                    variants.append({'src': original_target, 'width': width, 'bytes': path.stat().st_size})
                continue
            variants.append({'src': target, 'width': width, 'bytes': destination.stat().st_size})
        manifest[source] = {'width': image.width, 'height': image.height,
                            'originalBytes': path.stat().st_size, 'variants': variants}
    if lossless:
        manifest[source]['compression'] = 'lossless'
(ROOT / 'src/image-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Prepared {len(manifest)} images, {sum(len(m["variants"]) for m in manifest.values())} variants')
