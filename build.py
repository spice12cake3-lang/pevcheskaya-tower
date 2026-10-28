"""Build a dependency-free local preview and a Tilda T123 HTML fragment."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
from datetime import date
import json
import re

SHORT_WORDS = re.compile(
    r'(?<![\w-])(?:в|во|на|к|ко|с|со|у|о|об|обо|от|ото|по|до|за|из|изо|'
    r'без|безо|для|при|про|под|подо|над|надо|перед|передо|через|между|'
    r'около|возле|ради|и|а|но|не)[ \t]+(?=[А-Яа-яЁёA-Za-z0-9«„“"])', re.IGNORECASE)


class Typography(HTMLParser):
    """Bind prepositions in text while preserving HTML attributes and URLs."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        self.parts.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.parts.append(f'</{tag}>')

    def handle_data(self, data):
        self.parts.append(SHORT_WORDS.sub(lambda m: m[0].rstrip(' \t') + '\N{NO-BREAK SPACE}', data))

    def handle_entityref(self, name):
        self.parts.append(f'&{name};')

    def handle_charref(self, name):
        self.parts.append(f'&#{name};')

    def handle_comment(self, data):
        self.parts.append(f'<!--{data}-->')

ROOT = Path(__file__).resolve().parent
shared_header = (ROOT / 'src/header.html').read_text()
shared_banquet = (ROOT / 'src/banquet-dialog.html').read_text()
page = (ROOT / 'src/page.html').read_text()
page = page.replace('<!-- SHARED_HEADER -->', shared_header.strip())
page = page.replace('<!-- BANQUET_DIALOG -->', shared_banquet)
schedule = json.loads((ROOT / 'src/schedule.json').read_text())
months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']


def schedule_rows(events):
    rows = []
    for event in sorted(events, key=lambda item: item['day']):
        day = date(schedule['year'], schedule['month'], event['day'])
        start = escape(event['start'])
        times = f'<time datetime="{day.isoformat()}T{start}">{start}</time>'
        if 'end' in event:
            end = escape(event['end'])
            times += f'–<time datetime="{day.isoformat()}T{end}">{end}</time>'
        age = f'<span class="pb__schedule-age">{escape(event["age"])}</span>' if 'age' in event else ''
        price = f'<span class="pb__schedule-price">{event["price"]} ₽</span>' if 'price' in event else ''
        rows.append(f'''<li class="pb__schedule-row">
        <time class="pb__schedule-date" datetime="{day.isoformat()}"><span class="pb__schedule-day">{day.day:02d}</span><span class="pb__schedule-weekday">{weekdays[day.weekday()]}</span></time>
        <div class="pb__schedule-copy"><span class="pb__schedule-time">{times}</span><h3 class="pb__schedule-title">{escape(event['title'])}{age}</h3></div>{price}
      </li>''')
    return '\n'.join(rows)


page = page.replace('<!-- SCHEDULE_MONTH -->', months[schedule['month'] - 1])
page = page.replace('<!-- SCHEDULE_WORKSHOPS -->', schedule_rows(schedule['workshops']))
page = page.replace('<!-- SCHEDULE_MUSIC -->', schedule_rows(schedule['music']))
typography = Typography()
typography.feed(page)
typography.close()
page = ''.join(typography.parts)
css = (ROOT / 'src/styles.css').read_text()
js = (ROOT / 'src/app.js').read_text() + '\n' + (ROOT / 'src/banquet.js').read_text()
form_js = (ROOT / 'src/contact-form.js').read_text()
js += '\n' + form_js
heading_js = (ROOT / 'src/heading-motion.js').read_text()
js += '\n' + heading_js
pdf_js = (ROOT / 'src/pdf-viewer.js').read_text()
pdf_js = pdf_js.replace('/* MENU_PREVIEWS */ {}', (ROOT / 'src/menu-previews.json').read_text().strip())
js += '\n' + pdf_js
fragment = f'<style>\n{css}\n</style>\n{page}\n<script>\n{js}\n</script>\n'
(ROOT / 'tilda-t123.html').write_text(fragment)
(ROOT / 'dist/index.html').write_text('''<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Певческая башня — гастрономическое и культурное пространство</title><meta name="description" content="Рестораны, апартаменты, обзорная площадка и залы для ваших событий в исторической Певческой башне в Пушкине."><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#065781"><link rel="icon" href="assets/logo.png"><link rel="preload" href="assets/fonts/bebas-neue-cyrillic.ttf" as="font" type="font/ttf" crossorigin><style>body{margin:0;background:#f7f2e9}</style></head><body>
''' + fragment + '</body></html>\n')
# Every space uses the same page, feedback form and footer.
venue_template = (ROOT / 'src/venue.html').read_text()
venues = json.loads((ROOT / 'src/venues.json').read_text())
contact_start = page.index('  <section class="pb__contact"')
footer_start = page.index('  <section class="pb__contacts ')
form = page[contact_start:footer_start]
contacts = page[footer_start:page.index('  <dialog class="pb__pdf')]
contacts = contacts.replace('<section ', '<footer ', 1).replace('</section>', '</footer>')
route = page[page.index('  <dialog class="pb__route'):page.index('  <dialog class="pb__navigation')]
venue_css = css + '\n' + (ROOT / 'src/restaurant.css').read_text()
venue_js = '\n'.join([(ROOT / 'src/restaurant.js').read_text(), (ROOT / 'src/banquet.js').read_text(), form_js, heading_js, pdf_js])
internal_header = shared_header.replace('href="#pb-spaces"', 'href="./#pb-spaces"').replace('href="#pb-agenda"', 'href="./#pb-agenda"').replace('href="#pb-events"', 'href="./#pb-events"')

travel_agents = json.loads((ROOT / 'src/travel-agents.json').read_text())
for venue in venues + [travel_agents]:
    title = escape(venue['title'])
    heading_title = title
    if 'desktopTitleLines' in venue:
        heading_title = ' '.join('<span class="pb__desktop-title-line">' + escape(line) + '</span>' for line in venue['desktopTitleLines'])
    floor = ', ' + escape(venue['floor']) if venue['floor'] else ''
    location = f'<p class="pb__restaurant-location"><span aria-hidden="true">●</span> <a href="./#pb-spaces" aria-label="Вернуться к пространствам башни">Башня</a>{floor}</p>'
    if not venue.get('showLocation', True):
        location = ''
    actions = []
    if venue['menus']:
        actions.append('<a class="pb__button" href="menu.html">Меню</a>')
    if 'action' in venue:
        action = venue['action']
        if action.get('type') == 'booking':
            actions.append(f'<button class="pb__button" type="button" data-booking-open>{escape(action["label"])}</button>')
        elif action.get('type') == 'download':
            actions.append(f'<a class="pb__button" href="{escape(action["href"])}" download="{escape(action["filename"])}" type="application/pdf">{escape(action["label"])}</a>')
        else:
            actions.append(f'<a class="pb__button" href="{escape(action["href"])}">{escape(action["label"])}</a>')
    gallery = []
    for image in venue['gallery']:
        caption = escape(image['alt'])
        src = escape(image['src'])
        gallery.append(f'<button type="button" data-gallery-src="{src}" data-gallery-alt="{caption}" aria-label="Показать: {caption}" aria-pressed="false"><img class="pb__gallery-thumbnail" src="{src}" width="{image["width"]}" height="{image["height"]}" alt="{caption}" loading="lazy"></button>')
    position = ' style="object-position:' + escape(venue['imagePosition']) + '"' if 'imagePosition' in venue else ''
    photo = f'<img id="pb-venue-photo" src="{escape(venue["mainImage"])}" width="{venue["mainWidth"]}" height="{venue["mainHeight"]}" alt="{escape(venue["mainAlt"])}" fetchpriority="high"{position}>'
    replacements = {
        '<!-- SHARED_HEADER -->': internal_header.strip(),
        '<!-- SHARED_BANQUET -->': shared_banquet.strip(),
        '<!-- VENUE_TITLE -->': heading_title,
        '<!-- VENUE_LOCATION -->': location,
        '<!-- VENUE_DESCRIPTION -->': escape(venue['description']),
        '<!-- VENUE_ACTIONS -->': ''.join(actions),
        '<!-- VENUE_GALLERY -->': ''.join(gallery),
        '<!-- VENUE_MAIN_PHOTO -->': photo,
        '<!-- SHARED_FORM -->': form.strip(),
        '<!-- SHARED_CONTACTS -->': contacts.strip(),
        '<!-- SHARED_ROUTE -->': route.strip(),
    }
    source = venue_template
    if not actions:
        source = source.replace('<div class="pb__restaurant-actions"><!-- VENUE_ACTIONS --></div>', '')
    for placeholder, content in replacements.items():
        source = source.replace(placeholder, content)
    if venue['slug'] == 'travel-agents':
        source = source.replace('class="pb pb--restaurant"', 'class="pb pb--restaurant pb--travel-agents"')
        source = source.replace('<a href="travel-agents.html">', '<a href="travel-agents.html" aria-current="page">')
    typography = Typography()
    typography.feed(source)
    typography.close()
    description = escape(venue['description'], quote=True)
    document = f'''<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} — Певческая башня</title><meta name="description" content="{description}"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#065781"><link rel="icon" href="assets/logo.png"><link rel="preload" href="assets/fonts/bebas-neue-cyrillic.ttf" as="font" type="font/ttf" crossorigin><style>body{{margin:0;background:#f7f2e9}}</style></head><body>
<style>{venue_css}</style>
{''.join(typography.parts)}
<script>{venue_js}</script>
</body></html>
'''
    (ROOT / 'dist' / (venue['slug'] + '.html')).write_text(document)
career_source = (ROOT / 'src/vacancies.html').read_text()
menus = venue_template[venue_template.index('  <dialog class="pb__pdf'):venue_template.index('  <div class="pb__toast"')]
menus = menus.replace('  <!-- SHARED_BANQUET -->\n', '')
menus = menus.replace('<a href="vacancies.html">', '<a href="vacancies.html" aria-current="page">')
for placeholder, content in {'<!-- SHARED_HEADER -->': internal_header.replace('<a href="vacancies.html">', '<a href="vacancies.html" aria-current="page">').strip(), '<!-- SHARED_CONTACTS -->': contacts.strip(), '<!-- SHARED_ROUTE -->': route.strip(), '<!-- SHARED_MENUS -->': menus.strip(), '<!-- SHARED_BANQUET -->': shared_banquet.strip()}.items():
    career_source = career_source.replace(placeholder, content)
typography = Typography()
typography.feed(career_source)
typography.close()
career_css = css + '\n' + (ROOT / 'src/vacancies.css').read_text()
career_js = venue_js
(ROOT / 'dist/vacancies.html').write_text('''<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Карьера — Певческая башня</title><meta name="description" content="Карьера в Певческой башне. Оставьте заявку: желаемая должность, опыт работы, ФИО и телефон."><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#065781"><link rel="icon" href="assets/logo.png"><link rel="preload" href="assets/fonts/bebas-neue-cyrillic.ttf" as="font" type="font/ttf" crossorigin><style>body{margin:0;background:#f7f2e9}</style></head><body>
''' + f'<style>{career_css}</style>\n' + ''.join(typography.parts) + f'\n<script>{career_js}</script>\n</body></html>\n')
# The menu catalog reuses the existing PDF lightbox and shared navigation.
catalog = json.loads((ROOT / 'src/menu-catalog.json').read_text())
catalog_cards = []
for item in catalog:
    featured = ' pb__menu-card--featured' if item.get('featured') else ''
    action_label = escape(item.get('action', 'Смотреть меню'))
    item_title = escape(item['title'])
    catalog_cards.append(f'''<a class="pb__menu-card{featured}" href="#pb-menu" data-pdf-source="{escape(item['source'])}" data-pdf-title="{item_title}" aria-haspopup="dialog" aria-controls="pb-menu" aria-label="{item_title} — открыть">
        <h2>{item_title}</h2><span class="pb__menu-card-plus" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg></span>
        <span class="pb__menu-card-action">{action_label}</span>
      </a>''')
catalog_overlays = venue_template[venue_template.index('  <dialog class="pb__pdf'):venue_template.index('  <div class="pb__toast"')]
catalog_overlays = catalog_overlays.replace('  <!-- SHARED_BANQUET -->\n', '')
catalog_source = (ROOT / 'src/menu.html').read_text()
for placeholder, content in {
    '<!-- SHARED_HEADER -->': internal_header.strip(),
    '<!-- MENU_CARDS -->': '\n'.join(catalog_cards),
    '<!-- SHARED_FORM -->': form.strip(),
    '<!-- SHARED_CONTACTS -->': contacts.strip(),
    '<!-- SHARED_ROUTE -->': route.strip(),
    '<!-- SHARED_MENUS -->': catalog_overlays.strip(),
    '<!-- SHARED_BANQUET -->': shared_banquet.strip(),
}.items():
    catalog_source = catalog_source.replace(placeholder, content)
catalog_source = catalog_source.replace('<a href="menu.html">', '<a href="menu.html" aria-current="page">')
typography = Typography()
typography.feed(catalog_source)
typography.close()
catalog_css = css + '\n' + (ROOT / 'src/menu.css').read_text()
(ROOT / 'dist/menu.html').write_text('''<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Меню — Певческая башня</title><meta name="description" content="Меню ресторана, индийское, китайское, детское меню и винная карта. Все меню действуют во всех залах Певческой башни."><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#065781"><link rel="icon" href="assets/logo.png"><link rel="preload" href="assets/fonts/bebas-neue-cyrillic.ttf" as="font" type="font/ttf" crossorigin><style>body{margin:0;background:#f7f2e9}</style></head><body>
''' + f'<style>{catalog_css}</style>\n' + ''.join(typography.parts) + f'\n<script>{venue_js}</script>\n</body></html>\n')
print('Готово: главная, ' + str(len(venues)) + ' страниц пространств, турагентам, карьера, меню и tilda-t123.html')

# Responsive assets are prepared once by src/prepare_images.py and checked in.
# Production builds need only the Python standard library.
image_manifest = json.loads((ROOT / 'src/image-manifest.json').read_text())


def image_srcset(source):
    return ', '.join(f'{v["src"]} {v["width"]}w' for v in image_manifest[source]['variants'])


def image_sizes(attrs):
    classes = attrs.get('class', '')
    if 'pb__space-photo' in classes:
        return '(max-width:639px) calc(100vw - 60px), (max-width:1199px) 46vw, 23vw'
    if 'pb__contact-background' in classes or 'pb__careers-background' in classes:
        return '(min-width:1568px) 1520px, 100vw'
    if attrs.get('src', '').endswith('footer-tower.png'):
        return '(max-width:639px) 80vw, 35vw'
    if attrs.get('src', '').endswith('route-map.png'):
        return '(min-width:1320px) 1280px, calc(100vw - 40px)'
    if attrs.get('id') == 'pb-venue-photo' or attrs.get('fetchpriority') == 'high':
        return '(max-width:639px) calc(100vw - 28px), 50vw'
    if 'pb__map-image' in classes:
        return '(max-width:899px) 100vw, 50vw'
    if 'pb__gallery-thumbnail' in classes:
        return '(max-width:639px) 30vw, 16vw'
    return '(max-width:639px) 100vw, 50vw'


class ImageTag(HTMLParser):
    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)


def responsive_image(match):
    parser = ImageTag()
    parser.feed(match[0])
    attrs = parser.attrs
    source = attrs.get('src', '')
    if source in image_manifest:
        variants = image_manifest[source]['variants']
        attrs['sizes'] = image_sizes(attrs)
        attrs['srcset'] = image_srcset(source)
        attrs['src'] = next((v['src'] for v in variants if v['width'] >= 960), variants[-1]['src'])
    attrs['decoding'] = 'async'
    if attrs.get('fetchpriority') == 'high':
        attrs['loading'] = 'eager'
    return '<img ' + ' '.join(key if value is None else f'{key}="{escape(value, quote=True)}"' for key, value in attrs.items()) + '>'


def responsive_markup(markup):
    markup = re.sub(r'<img\b[^>]*>', responsive_image, markup)
    # Gallery controls keep full-size optimized sources separately from thumbnails.
    def gallery_source(match):
        source = match[1]
        if source not in image_manifest:
            return match[0]
        return f'data-gallery-src="{image_manifest[source]["variants"][-1]["src"]}" data-gallery-srcset="{image_srcset(source)}"'
    markup = re.sub(r'data-gallery-src="([^"]+)"', gallery_source, markup)
    return markup


loading_head = (ROOT / 'src/loading-head.html').read_text()
loading_js = (ROOT / 'src/loading.js').read_text()
preloader = '<div class="pb-preloader" aria-hidden="true"><img src="assets/logo.png" width="88" height="70" alt=""><span></span></div>'
for document_path in (ROOT / 'dist').glob('*.html'):
    if document_path.name.startswith('qa-'):
        continue
    document = responsive_markup(document_path.read_text())
    document = document.replace('.ttf', '.woff2').replace('format("truetype")', 'format("woff2")').replace('type="font/ttf"', 'type="font/woff2"')
    hero = re.search(r'<img\b[^>]*fetchpriority="high"[^>]*>', document)
    preload = ''
    if hero:
        parser = ImageTag()
        parser.feed(hero[0])
        attrs = parser.attrs
        preload = '<link rel="preload" as="image" fetchpriority="high" href="' + attrs['src'] + '"'
        if 'srcset' in attrs:
            preload += ' imagesrcset="' + attrs['srcset'] + '" imagesizes="' + attrs['sizes'] + '"'
        preload += '>'
    document = document.replace('</head>', preload + loading_head + '</head>')
    document = document.replace('<body>', '<body>' + preloader, 1)
    document = document.replace('</body>', '<script>' + loading_js + '</script></body>')
    document_path.write_text(document)
(ROOT / 'tilda-t123.html').write_text(responsive_markup(fragment).replace('.ttf', '.woff2').replace('format("truetype")', 'format("woff2")'))
