"""Render the published menus once so visitors download only the page they read.

Run with the bundled Python runtime (Pillow and pypdfium2), then run build.py.
The source PDFs stay unchanged. Text menus use lossless WebP; photographic
menus use high quality WebP so a single page stays small on mobile networks.
"""
from pathlib import Path
import hashlib
import json

import pypdfium2 as pdfium
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
manifest = {}
for menu in json.loads((ROOT / 'src/menu-catalog.json').read_text()):
    source = ROOT / 'dist' / menu['source']
    digest = hashlib.sha256(source.read_bytes() + b'webp-960-1920-q92-v1').hexdigest()[:10]
    name = 'restaurant' if source.name == 'menu.pdf' else source.stem
    folder = Path('assets/menu-pages') / (name + '-' + digest)
    (ROOT / 'dist' / folder).mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(source)
    pages = []
    for number in range(len(document)):
        page = document[number]
        width, height = page.get_size()
        variants = []
        for target in (960, 1920):
            relative = folder / f'{number + 1:02d}-{target}.webp'
            output = ROOT / 'dist' / relative
            if not output.exists():
                bitmap = page.render(scale=target / width)
                image = bitmap.to_pil().convert('RGB')
                options = {'lossless': True} if name in ('restaurant', 'wine') else {'quality': 92}
                image.save(output, 'WEBP', method=6, **options)
                bitmap.close()
            with Image.open(output) as saved:
                variants.append({'src': relative.as_posix(), 'width': saved.width})
        pages.append({'width': width, 'height': height, 'variants': variants})
        page.close()
    document.close()
    manifest[menu['source']] = pages
    print(menu['title'], len(pages), 'pages', flush=True)
(ROOT / 'src/menu-previews.json').write_text(json.dumps(manifest, ensure_ascii=False, separators=(',', ':')) + '\n')
