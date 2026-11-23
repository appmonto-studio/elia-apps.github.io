from datetime import date
from pathlib import Path
from html import escape

# Every page is rendered from this one file, so when it changes they all change.
# A single generation-day stamp is therefore honest, and never goes stale the way
# a hardcoded date does.
LASTMOD = date.today().isoformat()
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://getelia.app"
LANGS = ["en", "de", "es"]
LOCALES = {"en": "en_US", "de": "de_DE", "es": "es_ES"}
LANG_LABELS = {"en": "EN", "de": "DE", "es": "ES"}
THEME_LABELS = {
    "en": ("Use dark theme", "Use light theme"),
    "de": ("Dunkles Design verwenden", "Helles Design verwenden"),
    "es": ("Usar tema oscuro", "Usar tema claro"),
}
URL_PREFIXES = {"en": "", "de": "de", "es": "es"}
APPS = ["contractions", "feeding", "moments"]
APP_ICONS = ["contractions", "feeding", "moments"]
APP_NAMES = {"contractions": "Contractions", "feeding": "Feeding", "moments": "Moments"}
CARD_ACCENTS = {"contractions": "rose", "feeding": "honey", "moments": "sage"}
CARD_KEYS = {"contractions": "contr_card", "feeding": "feed_card", "moments": "moments_card"}

# Published store listings. An app absent from this map is still "Coming soon".
# Only add a URL after confirming the listing is publicly reachable.
STORES = {
    "contractions": {
        "google_play": "https://play.google.com/store/apps/details?id=app.elia.contractions",
    },
    "feeding": {
        "google_play": "https://play.google.com/store/apps/details?id=app.elia.feeding",
    },
}
ACCENTS = {
    "feeding": ("#C9976A", "#A9784C", "#F3E3D1", "#352A20"),
    "moments": ("#687F59", "#53663F", "#DCE5D5", "#2B3526"),
}


def url(lang, route=""):
    route = route.strip("/")
    prefix = URL_PREFIXES[lang]
    prefix = f"{prefix}/" if prefix else ""
    path = f"{prefix}{route}/" if route else prefix
    return f"{BASE}/{path}".replace("//", "/").replace("https:/", "https://")


def href(lang, route="", current_lang=None, current_route=""):
    # Clean, canonical root-relative path (trailing slash, no index.html),
    # matching canonical/hreflang/sitemap exactly. current_* kept for signature
    # compatibility; a root-relative path needs no source context.
    return urlparse(url(lang, route)).path


def relpath(target, source_dir):
    return Path(__import__("os").path.relpath(target, source_dir)).as_posix()


def asset(path, current_lang, current_route=""):
    target = ROOT / path.strip("/")
    source_dir = out_path(current_lang, current_route).parent
    return relpath(target, source_dir)


def out_path(lang, route=""):
    route = route.strip("/")
    prefix = URL_PREFIXES[lang]
    if not prefix:
      return ROOT / (route or "") / "index.html"
    return ROOT / prefix / (route or "") / "index.html"

def alternates(route):
    links = [f'  <link rel="alternate" hreflang="{lang}" href="{url(lang, route)}" />' for lang in LANGS]
    links.append(f'  <link rel="alternate" hreflang="x-default" href="{url("en", route)}" />')
    return "\n".join(links)


def og_locales(lang):
    lines = [f'  <meta property="og:locale" content="{LOCALES[lang]}" />']
    lines.extend(f'  <meta property="og:locale:alternate" content="{LOCALES[x]}" />' for x in LANGS if x != lang)
    return "\n".join(lines)


def lang_switch(lang, route, label):
    links = []
    for x in LANGS:
        current = ' aria-current="true"' if x == lang else ""
        links.append(f'<a href="{href(x, route, lang, route)}"{current} hreflang="{x}" lang="{x}">{LANG_LABELS[x]}</a>')
    return f'<nav class="lang-switch" aria-label="{escape(label)}">{"".join(links)}</nav>'


def head(lang, route, title, description, icon="svg", image=None, extra=""):
    icon_link = '\n'.join([
        f'  <link rel="icon" type="image/png" href="{asset("assets/img/favicon-elia.png", lang, route)}" />',
        f'  <link rel="apple-touch-icon" href="{asset("assets/img/apple-touch-icon-elia.png", lang, route)}" />',
    ])
    if icon in APP_ICONS:
        icon_link = '\n'.join([
            f'  <link rel="icon" type="image/png" href="{asset(f"assets/img/favicon-{icon}.png", lang, route)}" />',
            f'  <link rel="apple-touch-icon" href="{asset(f"assets/img/apple-touch-icon-{icon}.png", lang, route)}" />',
        ])
    image_tags = ""
    if image:
        image_tags = f"""
  <meta property="og:image" content="{image}" />
  <meta property="og:image:type" content="image/jpeg" />
  <meta property="og:image:width" content="1024" />
  <meta property="og:image:height" content="500" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{image}" />"""
    return f"""<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script>try{{document.documentElement.dataset.theme=localStorage.getItem('elia-theme')==='dark'?'dark':'light'}}catch(_){{document.documentElement.dataset.theme='light'}}</script>
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}" />
  <meta name="theme-color" content="#FBF9F8" />
{icon_link}
  <link rel="stylesheet" href="{asset('assets/css/styles.css', lang, route)}" />
  <link rel="canonical" href="{url(lang, route)}" />
{alternates(route)}

  <meta property="og:type" content="website" />
  <meta property="og:title" content="{escape(title)}" />
  <meta property="og:description" content="{escape(description)}" />
  <meta property="og:url" content="{url(lang, route)}" />
{og_locales(lang)}{image_tags}
{extra}</head>"""


def header(lang, route, nav, aria):
    def nav_href(link):
        if link.startswith("#"):
            return link
        if link.startswith("home#"):
            return href(lang, "", lang, route) + link.removeprefix("home")
        return href(lang, link, lang, route)
    nav_html = "\n        ".join(f'<a href="{nav_href(link)}">{escape(text)}</a>' for text, link in nav)
    dark_label, light_label = THEME_LABELS[lang]
    return f"""<header class="site-header">
    <div class="container">
      <a class="brand" href="{href(lang, "", lang, route)}" aria-label="Elia home">
        <img class="brand__mark" src="{asset("assets/img/logo-elia.png", lang, route)}" alt="" />
        <span class="brand__name">Elia</span>
      </a>
      <nav class="nav" aria-label="Primary">
        {nav_html}
      </nav>
      <div class="header-tools">
        {lang_switch(lang, route, aria)}
        <button class="theme-toggle" type="button" data-theme-toggle data-label-dark="{escape(dark_label)}" data-label-light="{escape(light_label)}" aria-label="{escape(dark_label)}" aria-pressed="false"><svg class="theme-toggle__sun" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3.5"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.66 6.34l1.41-1.41"/></svg><svg class="theme-toggle__moon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 15.1A8.5 8.5 0 0 1 8.9 4a8.5 8.5 0 1 0 11.1 11.1Z"/></svg></button>
      </div>
    </div>
  </header>"""


# Elia is a brand of Appmonto Studio. The studio site carries the Austrian
# imprint for every brand, so link to it rather than duplicating the text here.
STUDIO_NAME = "Appmonto Studio"
STUDIO_URL = "https://appmonto.com"
STUDIO_IMPRINT_URL = "https://appmonto.com/legal/"


def studio_line(lang):
    t = STUDIO[lang]
    brand = f'<a href="{STUDIO_URL}{href(lang)}" rel="noopener">{STUDIO_NAME}</a>'
    imprint = f'<a href="{STUDIO_IMPRINT_URL}" rel="noopener">{escape(t["imprint"])}</a>'
    return f'{t["brand_of"].format(studio=brand)} · {imprint}'


STUDIO = {
    "en": {"brand_of": "An {studio} brand", "imprint": "Imprint",
           "operator": f"Elia is a brand of {STUDIO_NAME}, Austria."},
    "de": {"brand_of": "Eine Marke von {studio}", "imprint": "Impressum",
           "operator": f"Elia ist eine Marke von {STUDIO_NAME}, Österreich."},
    "es": {"brand_of": "Una marca de {studio}", "imprint": "Aviso legal",
           "operator": f"Elia es una marca de {STUDIO_NAME}, Austria."},
}


def footer(lang, links, note, route=""):
    links_html = "\n        ".join(f'<a href="{href(lang, link, lang, route)}">{escape(text)}</a>' if not link.startswith("mailto:") and not link.startswith("#") else f'<a href="{link}">{escape(text)}</a>' for text, link in links)
    return f"""<footer class="site-footer">
    <div class="container">
      <a class="brand" href="{href(lang, "", lang, route)}" aria-label="Elia home">
        <img class="brand__mark" src="{asset("assets/img/logo-elia.png", lang, route)}" alt="" />
        <span class="brand__name">Elia</span>
      </a>
      <div class="foot-links">
        {links_html}
      </div>
      <small>{escape(note)} © <span id="year">2026</span> Elia. {studio_line(lang)}</small>
    </div>
  </footer>

  <script src="{asset('assets/js/site.js', lang, route)}" defer></script>"""


T = {'en': {'lang': 'Language',
        'note': 'Not a medical device.',
        'home': {'title': 'Elia — apps for birth and the first years',
                 'description': 'Time contractions, record feeds and look back at the entries on your phone. Both apps work offline.',
                 'nav': [('Apps', '#apps'), ('Philosophy', '#philosophy'), ('Story', '#story')],
                 'hero': ['Elia',
                          'When was the last contraction? The last feed?',
                          'Time contractions, record feeds and look back at the entries on your phone. Both apps work offline.',
                          'See the apps',
                          'Why Elia'],
                 'apps_head': ['The apps',
                               'Choose an app',
                               'Contractions and Feeding are available on Android. Moments is in development.'],
                 'coming': 'Coming soon',
                 'on_play': 'On Google Play',
                 'get_play': 'Get it on Google Play',
                 'learn': 'Learn more',
                 'contr_card': ['Elia Contractions',
                                'Record when each contraction starts and ends. Share the times with your midwife or doctor.'],
                 'feed_card': ['Elia Feeding',
                               'Record feeds, pumping sessions and diaper changes. Check when you last switched sides.'],
                 'promise': ['The promise',
                             'Use Elia without signing in',
                             'Timing contractions and logging feeds are free and work offline. If you want cloud backup or family sharing, you can opt in where your app supports it. Elia Account activation is a one-time purchase. Invited family members can join without a separate purchase.'],
                 'chips': ['Free offline use', 'No ads', 'No analytics'],
                 'story': ['Our story',
                           'Elia was born in a delivery room.',
                           'During labor, a partner reached for a contraction app. It lagged. The main button never '
                           'made it clear whether tracking had started. Useful features were locked behind a '
                           'subscription. After three contractions it said to go to the hospital — where the family '
                           'already was.',
                           'The app added stress. Elia is the answer to that moment: the companion we wished we had.',
                           'Their baby was born that evening. Elia was born the same day — and grew into a small '
                           'family of apps for the quiet, tired, important days that follow.']}},
 'de': {'lang': 'Sprache',
        'note': 'Kein Medizinprodukt.',
        'home': {'title': 'Elia — Apps für die Geburt und die ersten Jahre',
                 'description': 'Miss die Dauer der Wehen, halte Mahlzeiten fest und sieh auf dem Handy nach, wann die letzte war. Beide Apps funktionieren offline.',
                 'nav': [('Apps', '#apps'), ('Philosophie', '#philosophy'), ('Geschichte', '#story')],
                 'hero': ['Elia',
                          'Wann war die letzte Wehe? Und die letzte Mahlzeit?',
                          'Miss die Dauer der Wehen, halte Mahlzeiten fest und sieh auf dem Handy nach, wann die letzte war. Beide Apps funktionieren offline.',
                          'Apps ansehen',
                          'Warum Elia'],
                 'apps_head': ['Die Apps',
                               'App auswählen',
                               'Contractions und Feeding sind für Android erhältlich. Moments ist in Entwicklung.'],
                 'coming': 'Demnächst',
                 'on_play': 'Bei Google Play',
                 'get_play': 'Bei Google Play herunterladen',
                 'learn': 'Mehr erfahren',
                 'contr_card': ['Elia Contractions',
                                'Erfasse Beginn und Ende jeder Wehe. Die Zeiten kannst du mit deiner Hebamme oder deinem Arzt teilen.'],
                 'feed_card': ['Elia Feeding',
                               'Erfasse Mahlzeiten, Abpumpen und Windelwechsel. Sieh nach, an welcher Seite du zuletzt gestillt hast.'],
                 'promise': ['Das Versprechen',
                             'Elia ohne Anmeldung nutzen',
                             'Wehen messen und Mahlzeiten festhalten kannst du kostenlos und offline. Wo deine App es unterstützt, kannst du Cloud-Backups oder das Teilen mit deiner Familie einschalten. Für die Aktivierung deines Elia Account zahlst du einmalig. Mit einer Familieneinladung kannst du ohne weiteren Kauf beitreten.'],
                 'chips': ['Offline kostenlos nutzbar', 'Keine Werbung', 'Keine Nutzungsanalyse'],
                 'story': ['Unsere Geschichte',
                           'Elia entstand in einem Kreißsaal.',
                           'Während der Geburt griff ein Partner zu einer Wehen-App. Sie reagierte träge. Der '
                           'Hauptknopf machte nie klar, ob die Aufzeichnung begonnen hatte. Nützliche Funktionen lagen '
                           'hinter einem Abo. Nach drei Wehen sagte sie, man solle ins Krankenhaus fahren — wo die '
                           'Familie bereits war.',
                           'Die App machte den Moment stressiger. Elia ist die Antwort darauf: der Begleiter, den wir '
                           'uns gewünscht hätten.',
                           'Das Baby wurde an diesem Abend geboren. Elia entstand am selben Tag — und wuchs zu einer '
                           'kleinen App-Familie für die leisen, müden und wichtigen Tage danach.']}},
 'es': {'lang': 'Idioma',
        'note': 'No es un dispositivo médico.',
        'home': {'title': 'Elia — apps para el parto y los primeros años',
                 'description': 'Cronometra las contracciones, anota las tomas y consulta los registros en tu móvil. Ambas apps funcionan sin conexión.',
                 'nav': [('Apps', '#apps'), ('Filosofía', '#philosophy'), ('Historia', '#story')],
                 'hero': ['Elia',
                          '¿Cuándo fue la última contracción? ¿Y la última toma?',
                          'Cronometra las contracciones, anota las tomas y consulta los registros en tu móvil. Ambas apps funcionan sin conexión.',
                          'Ver las apps',
                          'Por qué Elia'],
                 'apps_head': ['Las apps',
                               'Elige una app',
                               'Contractions y Feeding están disponibles para Android. Moments está en desarrollo.'],
                 'coming': 'Próximamente',
                 'on_play': 'En Google Play',
                 'get_play': 'Consíguelo en Google Play',
                 'learn': 'Más información',
                 'contr_card': ['Elia Contractions',
                                'Anota cuándo empieza y termina cada contracción. Puedes compartir los tiempos con tu equipo médico.'],
                 'feed_card': ['Elia Feeding',
                               'Anota las tomas, las extracciones y los cambios de pañal. Consulta qué pecho diste la última vez.'],
                 'promise': ['La promesa',
                             'Usa Elia sin iniciar sesión',
                             'Puedes cronometrar las contracciones y registrar las tomas gratis y sin conexión. Si tu app lo permite, puedes activar las copias en la nube o compartir datos con tu familia. La activación de Elia Account se paga una sola vez. Si recibes una invitación familiar, puedes unirte sin volver a pagar.'],
                 'chips': ['Uso sin conexión gratuito', 'Sin anuncios', 'Sin analíticas'],
                 'story': ['Nuestra historia',
                           'Elia nació en una sala de parto.',
                           'Durante el parto, una pareja abrió una app de contracciones. Iba lenta. El botón principal '
                           'nunca dejaba claro si el registro había empezado. Las funciones útiles estaban detrás de '
                           'una suscripción. Tras tres contracciones dijo que fueran al hospital, donde la familia ya '
                           'estaba.',
                           'La app añadió estrés. Elia es la respuesta a ese momento: la compañera que nos habría '
                           'gustado tener.',
                           'Su bebé nació esa noche. Elia nació el mismo día y creció hasta convertirse en una pequeña '
                           'familia de apps para los días silenciosos, cansados e importantes que vienen después.']}}}


APP = {'en': {'common': {'overview': 'Overview',
                   'support': 'Support',
                   'privacy': 'Privacy',
                   'all': 'All apps',
                   'back': '← All Elia apps',
                   'what': 'What it is',
                   'does': 'What it does',
                   'promise': 'The promise',
                   'why': 'Why it exists',
                   'still': 'Still need help?',
                   'read': 'We read every message.'},
        'contractions': {'title': 'Elia Contractions — contraction timer',
                         'desc': 'Tap at the start of a contraction and again at the end. The app records its duration and the time between starts.',
                         'tag': 'Time your contractions',
                         'sub': 'Tap at the start of a contraction and again at the end. The app records its duration and the time between starts.',
                         'head': ['What it is', 'Your contraction history'],
                         'left': 'Elia Contractions helps you',
                         'right': 'What it is not',
                         'yes': ['Record contractions with one clear tap.',
                                 'Review timing and intervals at a glance.',
                                 'Stay focused during a contraction.',
                                 'Stay present between them.',
                                 'Keep a simple, honest history.',
                                 'Share a clear summary with your care team, if useful.'],
                         'no': ['A medical device or diagnostic tool.', 'A replacement for doctors or midwives.', 'A pregnancy or baby tracker.', 'An advertising surface.', 'Something that tells you what to do.'],
                         'story': ['Why it exists',
                                   'Born from a real birth.',
                                   'It began in a hospital room, during labor. Things moved quickly, and soon the '
                                   'contractions left almost no pause in between.',
                                   'The partner reached for a contraction app. The one they found lagged. The main '
                                   'button never made it clear whether tracking had started or stopped. Useful '
                                   'features were locked behind a subscription. After a few contractions, it told the '
                                   'family to leave for the hospital — where they already were, under care.',
                                   'The app added stress. Elia is the answer to that moment.',
                                   'Their baby was born that evening. Elia was born the same day.'],
                         'principles': ['Use Elia without signing in',
                                        ['Free offline use', 'No ads', 'No analytics'],
                                        'Elia Contractions is not a medical device and does not provide medical advice '
                                        'or diagnosis. It never tells you when to go to the hospital. Always follow '
                                        'the guidance of your doctors and midwives.']},
        'feeding': {'title': 'Elia Feeding — feeding and diaper log',
                    'desc': 'Log breastfeeding, bottles, diapers and pumping. The home screen shows the last feed and diaper change.',
                    'tag': 'When did the baby last eat?',
                    'sub': 'Log breastfeeding, bottles, diapers and pumping. The home screen shows the last feed and diaper change.',
                    'pull': ['Which side was it last time?',
                             'The breastfeeding timer records the side. If you switch during a feed, both sides stay in the same entry.'],
                    'head': ['What it does', 'What you can record'],
                    'left': 'In the app',
                    'right': 'Deliberately not included',
                    'yes': ['Breastfeeding timer with Left / Right side.',
                            'Bottle feeding log, with optional amount.',
                            'Simple diaper log: wet, dirty, or both.',
                            'Pumping sessions, with side, duration and optional amount.',
                            'Review a day, 7 days or 30 days. Edit or delete individual entries in History.',
                            'Share or export as plain text.'],
                    'no': ['Growth charts and analytics.', 'Feeding targets, streaks, or warnings.', 'Medical recommendations.', 'Sleep and medication logs.'],
                    'principles': ['Use Elia without signing in',
                                   'No goals, warnings, or pressure. Elia remembers what you log — nothing more.',
                                   ['Free offline use', 'No ads', 'No analytics'],
                                   'Elia Feeding is a feeding log. It does not give medical '
                                   "advice and does not define what is normal. For anything about your baby's health, "
                                   'talk to your pediatrician or midwife.']}},
 'de': {'common': {'overview': 'Überblick',
                   'support': 'Hilfe',
                   'privacy': 'Datenschutz',
                   'all': 'Alle Apps',
                   'back': '← Alle Elia-Apps',
                   'what': 'Was es ist',
                   'does': 'Was es tut',
                   'promise': 'Versprechen',
                   'why': 'Warum es existiert',
                   'still': 'Brauchst du Hilfe?',
                   'read': 'Wir lesen jede Nachricht.'},
        'contractions': {'title': 'Elia Contractions — Wehen-Timer',
                         'desc': 'Tippe zu Beginn und am Ende einer Wehe. Die App zeigt die Dauer und den Abstand zwischen zwei Wehenanfängen.',
                         'tag': 'Wehen messen',
                         'sub': 'Tippe zu Beginn und am Ende einer Wehe. Die App zeigt die Dauer und den Abstand zwischen zwei Wehenanfängen.',
                         'head': ['Was es ist', 'Dein Wehenverlauf'],
                         'left': 'Elia Contractions hilft dir',
                         'right': 'Was es nicht ist',
                         'yes': ['Wehen mit einem klaren Tippen erfassen.',
                                 'Dauer und Abstände auf einen Blick prüfen.',
                                 'Während einer Wehe fokussiert bleiben.',
                                 'Zwischen den Wehen präsent bleiben.',
                                 'Eine einfache, ehrliche Historie behalten.',
                                 'Bei Bedarf eine klare Zusammenfassung mit dem Betreuungsteam teilen.'],
                         'no': ['Ein Medizinprodukt oder Diagnosewerkzeug.', 'Ein Ersatz für Ärztinnen, Ärzte oder Hebammen.', 'Ein Schwangerschafts- oder Babytracker.', 'Eine Werbefläche.', 'Etwas, das dir sagt, was du tun sollst.'],
                         'story': ['Warum es existiert',
                                   'Aus einer echten Geburt entstanden.',
                                   'Es begann in einem Krankenhauszimmer während der Geburt. Alles ging schnell, und '
                                   'bald blieb zwischen den Wehen kaum noch Pause.',
                                   'Der Partner öffnete eine Wehen-App. Sie reagierte träge. Der Hauptknopf machte '
                                   'nicht klar, ob die Aufzeichnung gestartet oder gestoppt war. Nützliche Funktionen '
                                   'lagen hinter einem Abo. Nach ein paar Wehen sagte die App, man solle ins '
                                   'Krankenhaus fahren — wo die Familie bereits betreut wurde.',
                                   'Die App machte den Moment stressiger. Elia ist die Antwort darauf.',
                                   'Das Baby wurde an diesem Abend geboren. Elia entstand am selben Tag.'],
                         'principles': ['Elia ohne Anmeldung nutzen',
                                        ['Offline kostenlos nutzbar', 'Keine Werbung', 'Keine Nutzungsanalyse'],
                                        'Elia Contractions ist kein Medizinprodukt und gibt keine medizinische '
                                        'Beratung oder Diagnose. Sie sagt dir nie, wann du ins Krankenhaus fahren '
                                        'sollst. Folge immer den Empfehlungen deiner Ärztinnen, Ärzte und Hebammen.']},
        'feeding': {'title': 'Elia Feeding — Mahlzeiten und Windeln protokollieren',
                    'desc': 'Erfasse Stillen, Fläschchen, Windeln und Abpumpen. Auf der Startseite siehst du die letzte Mahlzeit und den letzten Windelwechsel.',
                    'tag': 'Wann hat dein Baby zuletzt getrunken?',
                    'sub': 'Erfasse Stillen, Fläschchen, Windeln und Abpumpen. Auf der Startseite siehst du die letzte Mahlzeit und den letzten Windelwechsel.',
                    'pull': ['Welche Seite war zuletzt dran?',
                             'Der Still-Timer merkt sich die Seite. Wechselst du während des Stillens, bleiben beide Seiten in einem Eintrag.'],
                    'head': ['Was es tut', 'Das kannst du eintragen'],
                    'left': 'In der App',
                    'right': 'Bewusst nicht enthalten',
                    'yes': ['Still-Timer mit linker / rechter Seite.',
                            'Fläschchen-Protokoll mit optionaler Menge.',
                            'Einfaches Windelprotokoll: nass, schmutzig oder beides.',
                            'Abpumpen mit Seite, Dauer und auf Wunsch der abgepumpten Menge.',
                            'Übersicht für einen Tag, 7 Tage oder 30 Tage. Im Verlauf kannst du einzelne Einträge ändern oder löschen.',
                            'Teilen oder Export als Klartext.'],
                    'no': ['Wachstumskurven und Analysen.', 'Fütterungsziele, Serien oder Warnungen.', 'Medizinische Empfehlungen.', 'Schlaf- und Medikamentenprotokolle.'],
                    'principles': ['Elia ohne Anmeldung nutzen',
                                   'Keine Ziele, Warnungen oder Druck. Elia merkt sich, was du einträgst — mehr nicht.',
                                   ['Offline kostenlos nutzbar', 'Keine Werbung', 'Keine Nutzungsanalyse'],
                                   'Elia Feeding ist ein Protokoll für Mahlzeiten und Pflege. Sie '
                                   'gibt keine medizinischen Ratschläge und definiert nicht, was normal ist. Wenn es '
                                   'um die Gesundheit deines Babys geht, sprich mit Kinderarzt, Kinderärztin oder '
                                   'Hebamme.']}},
 'es': {'common': {'overview': 'Vista general',
                   'support': 'Soporte',
                   'privacy': 'Privacidad',
                   'all': 'Todas las apps',
                   'back': '← Todas las apps de Elia',
                   'what': 'Qué es',
                   'does': 'Qué hace',
                   'promise': 'La promesa',
                   'why': 'Por qué existe',
                   'still': '¿Necesitas ayuda?',
                   'read': 'Leemos todos los mensajes.'},
        'contractions': {'title': 'Elia Contractions — cronómetro de contracciones',
                         'desc': 'Toca el botón al empezar una contracción y de nuevo al terminar. La app registra la duración y el intervalo entre inicios.',
                         'tag': 'Cronometra tus contracciones',
                         'sub': 'Toca el botón al empezar una contracción y de nuevo al terminar. La app registra la duración y el intervalo entre inicios.',
                         'head': ['Qué es', 'Tu historial de contracciones'],
                         'left': 'Elia Contractions te ayuda a',
                         'right': 'Qué no es',
                         'yes': ['Registrar contracciones con un toque claro.',
                                 'Ver duración e intervalos de un vistazo.',
                                 'Mantener el foco durante una contracción.',
                                 'Estar presente entre una y otra.',
                                 'Conservar un historial simple y honesto.',
                                 'Compartir un resumen claro con tu equipo de atención, si resulta útil.'],
                         'no': ['Un dispositivo médico o herramienta de diagnóstico.', 'Un reemplazo de profesionales de salud.', 'Un tracker de embarazo o bebé.', 'Un espacio para anuncios.', 'Algo que te diga qué hacer.'],
                         'story': ['Por qué existe',
                                   'Nacida de un parto real.',
                                   'Todo empezó en una habitación de hospital, durante el parto. Las cosas avanzaron '
                                   'rápido y pronto casi no quedaba pausa entre contracciones.',
                                   'La pareja abrió una app de contracciones. La app iba lenta. El botón principal no '
                                   'dejaba claro si el registro había empezado o se había detenido. Las funciones '
                                   'útiles estaban detrás de una suscripción. Tras unas pocas contracciones, dijo a la '
                                   'familia que saliera hacia el hospital, donde ya estaban bajo cuidado.',
                                   'La app añadió estrés. Elia es la respuesta a ese momento.',
                                   'Su bebé nació esa noche. Elia nació el mismo día.'],
                         'principles': ['Usa Elia sin iniciar sesión',
                                        ['Uso sin conexión gratuito', 'Sin anuncios', 'Sin analíticas'],
                                        'Elia Contractions no es un dispositivo médico y no ofrece consejo médico ni '
                                        'diagnóstico. Nunca te dice cuándo ir al hospital. Sigue siempre las '
                                        'indicaciones de tus profesionales de salud.']},
        'feeding': {'title': 'Elia Feeding — registro de tomas y pañales',
                    'desc': 'Registra lactancia, biberones, pañales y extracciones. En la pantalla de inicio verás la última toma y el último cambio de pañal.',
                    'tag': '¿Cuándo fue la última toma?',
                    'sub': 'Registra lactancia, biberones, pañales y extracciones. En la pantalla de inicio verás la última toma y el último cambio de pañal.',
                    'pull': ['¿Qué pecho diste la última vez?',
                             'El temporizador guarda el lado. Si cambias de pecho durante la toma, ambos quedan en el mismo registro.'],
                    'head': ['Qué hace', 'Qué puedes registrar'],
                    'left': 'En la app',
                    'right': 'Deliberadamente no incluido',
                    'yes': ['Temporizador de lactancia con lado izquierdo / derecho.',
                            'Registro de biberón, con cantidad opcional.',
                            'Registro simple de pañales: pis, caca o ambos.',
                            'Extracciones con lado, duración y cantidad opcional.',
                            'Consulta el resumen de un día, de 7 días o de 30 días. Puedes editar o borrar entradas en el historial.',
                            'Compartir o exportar como texto plano.'],
                    'no': ['Gráficas de crecimiento y analíticas.', 'Objetivos de alimentación, rachas o alertas.', 'Recomendaciones médicas.', 'Registros de sueño y medicación.'],
                    'principles': ['Usa Elia sin iniciar sesión',
                                   'Sin objetivos, alertas ni presión. Elia recuerda lo que registras, nada más.',
                                   ['Uso sin conexión gratuito', 'Sin anuncios', 'Sin analíticas'],
                                   'Elia Feeding sirve para registrar tomas y cuidados. No '
                                   'da consejos médicos ni define qué es normal. Para cualquier duda sobre la salud de '
                                   'tu bebé, habla con tu pediatra o profesional de salud.']}}}


SUPPORT = {'en': {'contractions': [('Is my data private?',
                          'Your entries are saved on this device by default. You can use the app without paying or signing in.'),
                         ('Does it work offline?',
                          'Yes. Recording contractions never needs an internet connection. The app is built to be '
                          'reliable in a delivery room, not dependent on a signal.'),
                         ('Does it tell me when to go to the hospital?',
                          'No. Elia does not diagnose or give medical directives. It shows your contractions clearly '
                          'so you can share them with your care team. Always follow the guidance of your doctors and '
                          'midwives.'),
                         ('Can I correct a mistake?',
                          'Yes. You can edit or delete entries in your history.'),
                         ('How do I share a summary with my midwife or doctor?',
                          'Use the share option to send a text summary. You choose the recipient.'),
                         ('Is there a subscription?',
                          'Local use is free and ad-free. Optional Elia Account activation is a one-time purchase. Availability of cloud features depends on the app version.')],
        'feeding': [('Is my data private?',
                     'Your entries are saved on this device by default. You can use the app without paying or signing in.'),
                    ('Does it work offline?',
                     'Yes. Logging a feed, bottle, or diaper never needs an internet connection.'),
                    ('Does it tell me if my baby is feeding enough?',
                     'No. Elia does not set targets, warnings, or judgements, and does not define what is normal. It '
                     "simply remembers what you log. For anything about your baby's health, talk to your pediatrician "
                     'or midwife.'),
                    ('Can I edit or delete an entry?',
                     'Yes. You can edit or delete any entry. Nothing is permanent by accident.'),
                    ('Can two parents share the same log?',
                     'The current public Android version keeps the log on one device. You can send a text summary to another parent.'),
                    ('How do I move my log somewhere else?',
                     'Export a text summary to share, or save a backup file to import on another device. You choose where to save or send it.'),
                    ('Are there ads or subscriptions?',
                     'Local use is free and ad-free. Optional Elia Account activation is a one-time purchase. Availability of cloud features depends on the app version.')]},
 'de': {'contractions': [('Sind meine Daten privat?',
                          'Deine Einträge werden standardmäßig auf diesem Gerät gespeichert. Du kannst die App kostenlos und ohne Anmeldung nutzen.'),
                         ('Funktioniert es offline?',
                          'Ja. Wehen zu erfassen braucht nie eine Internetverbindung. Die App soll im Kreißsaal '
                          'verlässlich sein, nicht vom Empfang abhängen.'),
                         ('Sagt die App mir, wann ich ins Krankenhaus fahren soll?',
                          'Nein. Elia diagnostiziert nicht und gibt keine medizinischen Anweisungen. Sie zeigt deine '
                          'Wehen klar, damit du sie mit deinem Betreuungsteam teilen kannst. Folge immer den '
                          'Empfehlungen deiner Ärztinnen, Ärzte und Hebammen.'),
                         ('Kann ich einen Fehler korrigieren?',
                          'Ja. Du kannst Einträge im Verlauf bearbeiten oder löschen.'),
                         ('Wie teile ich eine Zusammenfassung mit Hebamme oder Arzt?',
                          'Über die Teilen-Funktion kannst du eine Zusammenfassung als Text senden. Du bestimmst den Empfänger.'),
                         ('Gibt es ein Abo?',
                          'Die lokale Nutzung ist kostenlos und werbefrei. Für die optionale Aktivierung des Elia Account zahlst du einmalig. Welche Cloud-Funktionen verfügbar sind, hängt von der App-Version ab.')],
        'feeding': [('Sind meine Daten privat?',
                     'Deine Einträge werden standardmäßig auf diesem Gerät gespeichert. Du kannst die App kostenlos und ohne Anmeldung nutzen.'),
                    ('Funktioniert es offline?',
                     'Ja. Füttern, Fläschchen oder Windeln zu protokollieren braucht nie Internet.'),
                    ('Sagt die App, ob mein Baby genug trinkt?',
                     'Nein. Elia setzt keine Ziele, Warnungen oder Urteile und definiert nicht, was normal ist. Sie '
                     'merkt sich nur, was du einträgst. Wenn es um die Gesundheit deines Babys geht, sprich mit '
                     'Kinderarzt, Kinderärztin oder Hebamme.'),
                    ('Kann ich einen Eintrag bearbeiten oder löschen?',
                     'Ja. Du kannst jeden Eintrag bearbeiten oder löschen. Nichts ist aus Versehen endgültig.'),
                    ('Können zwei Eltern dasselbe Protokoll teilen?',
                     'Die aktuelle öffentliche Android-Version speichert das Protokoll auf einem Gerät. Du kannst dem anderen Elternteil eine Zusammenfassung als Text schicken.'),
                    ('Wie verschiebe ich mein Protokoll woandershin?',
                     'Du kannst eine Zusammenfassung als Text teilen oder eine Sicherungsdatei auf einem anderen Gerät importieren. Du wählst das Ziel.'),
                    ('Gibt es Werbung oder Abos?',
                     'Die lokale Nutzung ist kostenlos und werbefrei. Für die optionale Aktivierung des Elia Account zahlst du einmalig. Welche Cloud-Funktionen verfügbar sind, hängt von der App-Version ab.')]},
 'es': {'contractions': [('¿Mis datos son privados?',
                          'Por defecto, tus registros se guardan en este dispositivo. Puedes usar la app gratis y sin iniciar sesión.'),
                         ('¿Funciona sin conexión?',
                          'Sí. Registrar contracciones nunca necesita conexión a internet. La app está pensada para '
                          'ser fiable en una sala de parto, no para depender de la señal.'),
                         ('¿Me dice cuándo ir al hospital?',
                          'No. Elia no diagnostica ni da instrucciones médicas. Muestra tus contracciones con claridad '
                          'para que puedas compartirlas con tu equipo de atención. Sigue siempre las indicaciones de '
                          'tus profesionales de salud.'),
                         ('¿Puedo corregir un error?',
                          'Sí. Puedes editar o borrar entradas en tu historial.'),
                         ('¿Cómo comparto un resumen con mi equipo de salud?',
                          'Usa la opción de compartir para enviar un resumen de texto. Tú eliges el destinatario.'),
                         ('¿Hay suscripción?',
                          'El uso local es gratuito y sin anuncios. La activación opcional de Elia Account se paga una sola vez. Las funciones en la nube dependen de la versión de la app.')],
        'feeding': [('¿Mis datos son privados?',
                     'Por defecto, tus registros se guardan en este dispositivo. Puedes usar la app gratis y sin iniciar sesión.'),
                    ('¿Funciona sin conexión?',
                     'Sí. Registrar una alimentación, un biberón o un pañal nunca necesita conexión a internet.'),
                    ('¿Me dice si mi bebé está comiendo suficiente?',
                     'No. Elia no establece objetivos, alertas ni juicios, y no define qué es normal. Simplemente '
                     'recuerda lo que registras. Para cualquier duda sobre la salud de tu bebé, habla con tu pediatra '
                     'o profesional de salud.'),
                    ('¿Puedo editar o borrar una entrada?',
                     'Sí. Puedes editar o borrar cualquier entrada. Nada queda permanente por accidente.'),
                    ('¿Pueden dos cuidadores compartir el mismo registro?',
                     'La versión pública actual de Android guarda el registro en un dispositivo. Puedes enviar un resumen de texto a otra persona.'),
                    ('¿Cómo llevo mi registro a otro lugar?',
                     'Puedes compartir un resumen de texto o guardar una copia para importarla en otro dispositivo. Tú eliges el destino.'),
                    ('¿Hay anuncios o suscripciones?',
                     'El uso local es gratuito y sin anuncios. La activación opcional de Elia Account se paga una sola vez. Las funciones en la nube dependen de la versión de la app.')]}}


MOMENTS = {
 'en': {'card': ['Elia Moments',
                 'A journal of childhood photos and notes, organised by date and by child.'],
        'app': {'title': 'Elia Moments — a childhood photo journal',
                'desc': 'A photo journal organised by child and date. You can keep a local archive without signing in.',
                'tag': 'A photo and the story behind it',
                'sub': 'A private family archive for the small firsts and meaningful memories that otherwise '
                       'scatter across notes, chats, and photo libraries.',
                'pull': ['What did they call the dog before they could say his name?',
                         'Write down the word, add a photo and save the date. The entry shows how old your child was.'],
                'head': ['What it does', 'Inside the journal'],
                'left': 'In the app',
                'right': 'Deliberately not included',
                'yes': ['A moment with a title, date, and automatically calculated age.',
                        'Up to five photos, copied into the app’s own storage.',
                        'Categories, a “first” flag, description, and optional place.',
                        'A full archive with year and month grouping, search, and filters.',
                        'A profile for each child, with their own archive.',
                        'Complete, portable backups you create yourself.'],
                'no': ['A milestone checklist or developmental scoring.',
                       'Comparison between siblings or other children.',
                       'Streaks, targets, or anxious reminders.',
                       'A social network or public child profile.',
                       'A required cloud account.',
                       'Ads or a subscription gate for the core archive.'],
                'principles': ['Use Elia without signing in',
                               ['Free offline use', 'No ads', 'No analytics'],
                               'Elia Moments never infers delays, diagnoses, or developmental judgement from what you '
                               'save. Categories and prompts are ways to remember, never obligations.']},
        'support': [('Is my data private?',
                     'Your entries are saved on this device by default. You can use the app without paying or signing in.'),
                    ('Does it work offline?',
                     'You can add and browse local entries offline. Cloud backup, restoring cloud photos and online place suggestions require a connection.'),
                    ('Does it tell me whether my child is on track?',
                     'No. Elia Moments is not a milestone checklist and never judges development. A first step and a '
                     'first taste of sushi can be equally valuable — your family decides what matters.'),
                    ('What happens to the photos I add?',
                     'Photos you pick are copied into the app’s own private storage, so deleting the original from '
                     'your gallery does not break the moment. The app uses the system photo picker and never asks for '
                     'access to your whole gallery.'),
                    ('How do I move everything to a new phone?',
                     'Create a complete backup file in Settings, then restore it on the new device. It contains '
                     'profiles, moments, settings, places, and media.'),
                    ('Will I lose everything if I uninstall?',
                     'Uninstalling removes the archive from your device. Before switching phones, save a complete backup and check where you saved it. Uninstalling does not delete a connected family archive.'),
                    ('Are there ads or subscriptions?',
                     'Local use is free and ad-free. Optional Elia Account activation is a one-time purchase. Availability of cloud features depends on the app version.')]},
 'de': {'card': ['Elia Moments',
                 'Ein Tagebuch für Fotos und Notizen aus der Kindheit, nach Datum und Kind geordnet.'],
        'app': {'title': 'Elia Moments — ein Fototagebuch für die Kindheit',
                'desc': 'Ein Fototagebuch nach Kind und Datum. Das lokale Archiv kannst du ohne Anmeldung nutzen.',
                'tag': 'Ein Foto und die Geschichte dazu',
                'sub': 'Ein privates Familienarchiv für die kleinen ersten Male und bedeutsamen '
                       'Erinnerungen, die sonst zwischen Notizen, Chats und Fotomediatheken verloren gehen.',
                'pull': ['Wie hat dein Kind den Hund genannt, bevor es seinen Namen aussprechen konnte?',
                         'Schreib das Wort auf, füge ein Foto hinzu und speichere das Datum. Im Eintrag steht, wie alt dein Kind damals war.'],
                'head': ['Was sie kann', 'Im Tagebuch'],
                'left': 'In der App',
                'right': 'Bewusst nicht enthalten',
                'yes': ['Ein Moment mit Titel, Datum und automatisch berechnetem Alter.',
                        'Bis zu fünf Fotos, in den eigenen Speicher der App kopiert.',
                        'Kategorien, „Erstes Mal“-Markierung, Beschreibung und optionaler Ort.',
                        'Ein vollständiges Archiv mit Gruppierung nach Jahr und Monat, Suche und Filtern.',
                        'Ein Profil für jedes Kind mit eigenem Archiv.',
                        'Vollständige, portable Backups, die du selbst erstellst.'],
                'no': ['Eine Meilenstein-Checkliste oder Entwicklungsbewertung.',
                       'Vergleiche zwischen Geschwistern oder anderen Kindern.',
                       'Serien, Ziele oder beunruhigende Erinnerungen.',
                       'Ein soziales Netzwerk oder öffentliches Kinderprofil.',
                       'Ein verpflichtendes Cloud-Konto.',
                       'Werbung oder eine Abo-Schranke für das Kernarchiv.'],
                'principles': ['Elia ohne Anmeldung nutzen',
                               ['Offline kostenlos nutzbar', 'Keine Werbung', 'Keine Nutzungsanalyse'],
                               'Elia Moments leitet aus deinen Einträgen niemals Verzögerungen, Diagnosen oder '
                               'Entwicklungsurteile ab. Kategorien und Vorschläge sind Wege zu erinnern, niemals '
                               'Pflichten.']},
        'support': [('Sind meine Daten privat?',
                     'Deine Einträge werden standardmäßig auf diesem Gerät gespeichert. Du kannst die App kostenlos und ohne Anmeldung nutzen.'),
                    ('Funktioniert die App offline?',
                     'Lokale Einträge kannst du offline anlegen und ansehen. Cloud-Backups, das Laden von Fotos aus der Cloud und Online-Ortsvorschläge brauchen eine Verbindung.'),
                    ('Sagt sie mir, ob mein Kind altersgerecht entwickelt ist?',
                     'Nein. Elia Moments ist keine Meilenstein-Checkliste und bewertet Entwicklung nie. Ein erster '
                     'Schritt und der erste Bissen Sushi können gleich wertvoll sein — deine Familie entscheidet, was '
                     'zählt.'),
                    ('Was passiert mit den Fotos, die ich hinzufüge?',
                     'Ausgewählte Fotos werden in den privaten Speicher der App kopiert. Löschst du das Original in '
                     'der Galerie, bleibt der Moment vollständig. Die App nutzt die System-Fotoauswahl und verlangt '
                     'keinen Zugriff auf die gesamte Galerie.'),
                    ('Wie ziehe ich alles auf ein neues Handy um?',
                     'Erstelle in den Einstellungen eine vollständige Backup-Datei und stelle sie auf dem neuen Gerät '
                     'wieder her. Sie enthält Profile, Momente, Einstellungen, Orte und Medien.'),
                    ('Verliere ich alles, wenn ich die App deinstalliere?',
                     'Beim Deinstallieren wird das Archiv vom Gerät entfernt. Sichere vor einem Gerätewechsel das vollständige Archiv und prüfe den Speicherort. Ein verbundenes Familienarchiv wird durch die Deinstallation nicht gelöscht.'),
                    ('Gibt es Werbung oder Abos?',
                     'Die lokale Nutzung ist kostenlos und werbefrei. Für die optionale Aktivierung des Elia Account zahlst du einmalig. Welche Cloud-Funktionen verfügbar sind, hängt von der App-Version ab.')]},
 'es': {'card': ['Elia Moments',
                 'Un diario de fotos y notas de la infancia, organizado por fecha y por hijo.'],
        'app': {'title': 'Elia Moments — un diario de fotos de la infancia',
                'desc': 'Un diario de fotos organizado por hijo y fecha. Puedes usar el archivo local sin iniciar sesión.',
                'tag': 'Una foto y la historia que hay detrás',
                'sub': 'Un archivo familiar privado para las pequeñas primeras veces y los recuerdos '
                       'que, si no, se dispersan entre notas, chats y fototecas.',
                'pull': ['¿Cómo llamaba al perro antes de saber decir su nombre?',
                         'Anota la palabra, añade una foto y guarda la fecha. La entrada muestra la edad que tenía tu hijo en ese momento.'],
                'head': ['Qué hace', 'Dentro del diario'],
                'left': 'En la app',
                'right': 'Deliberadamente no incluido',
                'yes': ['Un momento con título, fecha y edad calculada automáticamente.',
                        'Hasta cinco fotos, copiadas al almacenamiento propio de la app.',
                        'Categorías, marca de «primera vez», descripción y lugar opcional.',
                        'Un archivo completo con agrupación por año y mes, búsqueda y filtros.',
                        'Un perfil para cada niño, con su propio archivo.',
                        'Copias de seguridad completas y portables que creas tú.'],
                'no': ['Una lista de hitos o puntuación del desarrollo.',
                       'Comparaciones entre hermanos u otros niños.',
                       'Rachas, objetivos o recordatorios que generan ansiedad.',
                       'Una red social o un perfil público del niño.',
                       'Una cuenta en la nube obligatoria.',
                       'Anuncios o un muro de suscripción para el archivo principal.'],
                'principles': ['Usa Elia sin iniciar sesión',
                               ['Uso sin conexión gratuito', 'Sin anuncios', 'Sin analíticas'],
                               'Elia Moments nunca deduce retrasos, diagnósticos ni juicios sobre el desarrollo a '
                               'partir de lo que guardas. Las categorías y las sugerencias son formas de recordar, '
                               'nunca obligaciones.']},
        'support': [('¿Mis datos son privados?',
                     'Por defecto, tus registros se guardan en este dispositivo. Puedes usar la app gratis y sin iniciar sesión.'),
                    ('¿Funciona sin conexión?',
                     'Puedes añadir y consultar entradas locales sin conexión. Las copias en la nube, la descarga de fotos de la nube y las sugerencias de lugares en línea requieren conexión.'),
                    ('¿Me dice si mi hijo va bien para su edad?',
                     'No. Elia Moments no es una lista de hitos y nunca juzga el desarrollo. Un primer paso y la '
                     'primera vez que prueba sushi pueden ser igual de valiosos: tu familia decide qué importa.'),
                    ('¿Qué pasa con las fotos que añado?',
                     'Las fotos que eliges se copian al almacenamiento privado de la app, así que borrar el original '
                     'de la galería no rompe el momento. La app usa el selector de fotos del sistema y nunca pide '
                     'acceso a toda la galería.'),
                    ('¿Cómo llevo todo a un teléfono nuevo?',
                     'Crea un archivo de copia de seguridad completo en Ajustes y restáuralo en el nuevo dispositivo. '
                     'Contiene perfiles, momentos, ajustes, lugares y archivos.'),
                    ('¿Pierdo todo si desinstalo la app?',
                     'Al desinstalar se borra el archivo del dispositivo. Antes de cambiar de móvil, guarda una copia completa y comprueba dónde está. Desinstalar no elimina un archivo familiar conectado.'),
                    ('¿Hay anuncios o suscripciones?',
                     'El uso local es gratuito y sin anuncios. La activación opcional de Elia Account se paga una sola vez. Las funciones en la nube dependen de la versión de la app.')]}}

for _lang, _data in MOMENTS.items():
    T[_lang]['home']['moments_card'] = _data['card']
    APP[_lang]['moments'] = _data['app']
    SUPPORT[_lang]['moments'] = _data['support']






def ul(items, cls):
    return f'<ul class="{cls}">' + "".join(f"<li>{escape(x)}</li>" for x in items) + "</ul>"


def chips(items):
    return '<div class="chips">' + "".join(f'<span class="chip">{escape(x)}</span>' for x in items) + "</div>"


def status_badge(lang, app):
    """Card badge. The card is itself a link, so this must never be one."""
    t = T[lang]["home"]
    if "google_play" in STORES.get(app, {}):
        return f'<span class="tag tag--live"><span class="tag__dot"></span>{escape(t["on_play"])}</span>'
    return f'<span class="tag"><span class="tag__dot"></span>{escape(t["coming"])}</span>'


def store_cta(lang, app):
    """Hero call to action: a real link once the app is published."""
    t = T[lang]["home"]
    url = STORES.get(app, {}).get("google_play")
    if url:
        return f'<a class="btn btn--primary" href="{url}" target="_blank" rel="noopener">{escape(t["get_play"])}</a>'
    return f'<span class="tag"><span class="tag__dot"></span>{escape(t["coming"])}</span>'


def app_cards(lang):
    t = T[lang]["home"]
    cards = []
    for app in APPS:
        card = t[CARD_KEYS[app]]
        cards.append(f"""          <a class="app-card" href="{href(lang, f"apps/{app}")}" data-accent="{CARD_ACCENTS[app]}">
            <div class="app-card__top"><span class="app-icon is-image" aria-hidden="true"><img src="{asset(f"assets/img/icon-{app}.png", lang, "")}" alt="" width="256" height="256" loading="lazy" /></span><div><div class="app-card__title">{escape(card[0])}</div>{status_badge(lang, app)}</div></div>
            <p class="app-card__one">{escape(card[1])}</p><div class="app-card__foot"><span class="app-card__cta">{escape(t["learn"])} <span class="arrow">→</span></span></div>
          </a>""")
    return "\n".join(cards)


def home(lang):
    t = T[lang]["home"]
    body = f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
{head(lang, "", t["title"], t["description"])}
<body>
  {header(lang, "", t["nav"], T[lang]["lang"])}

  <main>
    <section class="hero">
      <div class="container">
        <h1 class="hero__wordmark">{escape(t["hero"][0])}</h1>
        <p class="hero__tagline">{escape(t["hero"][1])}</p>
        <p class="hero__sub lead">{escape(t["hero"][2])}</p>
        <div class="btn-row">
          <a class="btn btn--primary" href="#apps">{escape(t["hero"][3])}</a>
          <a class="btn btn--ghost" href="#philosophy">{escape(t["hero"][4])}</a>
        </div>
      </div>
    </section>

    <section id="apps">
      <div class="container">
        <div class="section-head"><span class="eyebrow">{escape(t["apps_head"][0])}</span><h2>{escape(t["apps_head"][1])}</h2><p class="lead">{escape(t["apps_head"][2])}</p></div>
        <div class="apps">
{app_cards(lang)}
        </div>
      </div>
    </section>

    <section id="philosophy" class="tint">
      <div class="container"><div class="section-head"><span class="eyebrow">{escape(t["promise"][0])}</span><h2>{escape(t["promise"][1])}</h2><p class="lead">{escape(t["promise"][2])}</p></div>{chips(t["chips"])}</div>
    </section>

    <section id="story">
      <div class="container"><div class="section-head"><span class="eyebrow">{escape(t["story"][0])}</span><h2>{escape(t["story"][1])}</h2></div><div class="story"><p class="pull">{escape(t["story"][2])}</p><p>{escape(t["story"][3])}</p><p>{escape(t["story"][4])}</p></div></div>
    </section>
  </main>

  {footer(lang, [*[(APP_NAMES[x], f"apps/{x}") for x in APPS], (t["nav"][1][0], "#philosophy"), ({"en": "Contact", "de": "Kontakt", "es": "Contacto"}[lang], "mailto:hello@getelia.app")], T[lang]["note"], "")}
</body>
</html>
"""
    write(lang, "", body)


def bottle_svg():
    return """<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 3h8M13 6h6l-1 2.5c2 1.2 3 3.2 3 5.5v11a3 3 0 0 1-3 3h-6a3 3 0 0 1-3-3V14c0-2.3 1-4.3 3-5.5L13 6z" />
                <path d="M10 15h12M10 20h12" />
              </svg>"""


def app_page(lang, app):
    c = APP[lang]["common"]
    a = APP[lang][app]
    route = f"apps/{app}"
    icon = app if app in APP_ICONS else "svg"
    image = f"{BASE}/assets/img/cover-contractions.jpg" if app == "contractions" else None
    extra = app_style(app)
    icon_html = f'<span class="app-icon is-image" aria-hidden="true" style="margin-top:24px;"><img src="{asset(f"assets/img/icon-{app}.png", lang, route)}" alt="" width="256" height="256" /></span>' if app in APP_ICONS else f'<span class="app-icon" aria-hidden="true" style="margin-top:24px;">{bottle_svg()}</span>'
    pre = ""
    if "pull" in a:
        pre = f"""<section id="promise" class="tint"><div class="container"><div class="story" style="margin-inline:auto; text-align:center;"><p class="pull">{escape(a["pull"][0])}</p><p class="lead">{escape(a["pull"][1])}</p></div></div></section>"""
    others = [(APP_NAMES[x], f"apps/{x}") for x in APPS if x != app]
    # principles is [heading, chips, callout] or [heading, sublead, chips, callout]
    has_sublead = len(a["principles"]) == 4
    sublead = f'<p class="lead">{escape(a["principles"][1])}</p>' if has_sublead else ""
    body = f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
{head(lang, route, a["title"], a["desc"], icon, image, extra)}
<body>
  {header(lang, route, [(c["overview"], "#what"), (c["support"], f"{route}/support"), (c["privacy"], f"{route}/privacy"), (c["all"], "")], T[lang]["lang"])}
  <main>
    <section class="hero app-hero"><div class="container"><a class="backlink" href="{href(lang, "", lang, route)}">{escape(c["back"])}</a>{icon_html}<h1>Elia {app.capitalize()}</h1><p class="hero__tagline">{escape(a["tag"])}</p><p class="hero__sub lead">{escape(a["sub"])}</p><div class="btn-row">{store_cta(lang, app)}</div></div></section>
{pre}
{shots_section(lang, app, route)}
    <section id="what"><div class="container"><div class="section-head"><span class="eyebrow">{escape(a["head"][0])}</span><h2>{escape(a["head"][1])}</h2></div><div class="grid-2"><div class="panel"><h3>{escape(a["left"])}</h3>{ul(a["yes"], "checklist")}</div><div class="panel"><h3>{escape(a["right"])}</h3>{ul(a["no"], "notlist")}</div></div></div></section>
{story_section(a) if app == "contractions" else ""}
    <section id="principles"><div class="container"><div class="section-head"><span class="eyebrow">{escape(c["promise"])}</span><h2>{escape(a["principles"][0])}</h2>{sublead}</div>{chips(a["principles"][2 if has_sublead else 1])}<div class="callout" style="margin-top:32px;">{escape(a["principles"][3 if has_sublead else 2])}</div></div></section>
  </main>
  {footer(lang, [(c["support"], f"{route}/support"), (c["privacy"], f"{route}/privacy"), *others, (c["all"], "")], T[lang]["note"], route)}
</body>
</html>
"""
    write(lang, route, body)


SHOTS = {
    "contractions": ["01-single", "02-main", "03-session", "04-about"],
    "feeding": ["01-feeding", "02-bottle", "03-diaper", "04-main", "05-summary", "06-history"],
}

SHOT_DIMENSIONS = {
    "contractions": (480, 853),
    "feeding": (480, 1029),
}

SHOTS_T = {
    "en": {
        "eyebrow": "A look inside",
        "larger": "View larger",
        "head": "What it looks like.",
        "alt": {
            "contractions": [
                "Track each contraction — start and stop with one tap, then stay focused on the moment.",
                "See the rhythm at a glance — recent contractions, interval, and last duration on one screen.",
                "Review your session history — check start times, durations and intervals, and edit entries when needed.",
                'About screen with information on offline timing and privacy.',
            ],
            "feeding": [
                "Track a breastfeeding session, switch sides with one tap, and see the time for each side.",
                "Log a bottle feed with an optional amount using a simple visual scale.",
                "Log a wet, dirty, or combined diaper change in one tap.",
                "Start a feed or log a bottle, diaper, or pumping session from the home screen.",
                "See a clear daily summary of feeding time, bottle amounts, and care events.",
                "Review and filter the complete history of breastfeeding, bottles, diapers, and pumping.",
            ],
        },
    },
    "de": {
        "eyebrow": "Ein Blick hinein",
        "larger": "Größer ansehen",
        "head": "So sieht es aus.",
        "alt": {
            "contractions": [
                "Jede Wehe erfassen — mit einem Tippen starten und stoppen und im Moment bleiben.",
                "Den Rhythmus auf einen Blick sehen — letzte Wehen, Intervall und Dauer auf einem Bildschirm.",
                "Den Sitzungsverlauf durchsehen — Startzeiten, Dauern und Intervalle prüfen und Einträge bearbeiten.",
                'Infoansicht mit Hinweisen zur Offline-Zeitmessung und zum Datenschutz.',
            ],
            "feeding": [
                "Eine Stillmahlzeit erfassen, mit einem Tippen die Seite wechseln und die Zeit pro Seite sehen.",
                "Eine Flaschenmahlzeit mit optionaler Menge über eine einfache visuelle Skala eintragen.",
                "Eine nasse, volle oder kombinierte Windel mit einem Tippen eintragen.",
                "Auf dem Startbildschirm eine Mahlzeit starten oder Flasche, Windel und Abpumpen eintragen.",
                "Eine klare Tagesübersicht über Stillzeiten, Flaschenmengen und Pflegeereignisse sehen.",
                "Den vollständigen Verlauf von Stillen, Flaschen, Windeln und Abpumpen ansehen und filtern.",
            ],
        },
    },
    "es": {
        "eyebrow": "Un vistazo",
        "larger": "Ver más grande",
        "head": "Así se ve.",
        "alt": {
            "contractions": [
                "Cronometra cada contracción: empieza y para con un toque, y sigue presente en el momento.",
                "Ve el ritmo de un vistazo: contracciones recientes, intervalo y última duración en una sola pantalla.",
                "Revisa el historial de la sesión: horas de inicio, duraciones, intervalos y edición de entradas.",
                'Pantalla de información sobre el cronómetro sin conexión y la privacidad.',
            ],
            "feeding": [
                "Registra una toma de pecho, cambia de lado con un toque y consulta el tiempo de cada lado.",
                "Registra una toma con biberón y una cantidad opcional mediante una sencilla escala visual.",
                "Registra con un toque un pañal mojado, sucio o ambas cosas.",
                "Inicia una toma o registra biberón, pañal o extracción desde la pantalla de inicio.",
                "Consulta un resumen diario claro del tiempo de lactancia, los biberones y los cuidados.",
                "Revisa y filtra el historial completo de lactancia, biberones, pañales y extracciones.",
            ],
        },
    },
}


def shots_section(lang, app, route):
    """Screenshot strip. Falls back to the English image set until a language
    has its own; drop files in shots/<app>/<lang>/ and they are picked up."""
    names = SHOTS.get(app)
    if not names:
        return ""
    t = SHOTS_T[lang]
    width, height = SHOT_DIMENSIONS[app]

    def pick(name):
        rel = f"assets/img/shots/{app}/{lang}/{name}.jpg"
        return rel if (ROOT / rel).exists() else f"assets/img/shots/{app}/en/{name}.jpg"

    imgs = []
    for i, name in enumerate(names):
        img = (
            f'<img src="{asset(pick(name), lang, route)}" alt="{escape(t["alt"][app][i])}" '
            f'width="{width}" height="{height}" loading="lazy" decoding="async" />'
        )
        imgs.append(
            f'<a href="{asset(pick(name + "-full"), lang, route)}" target="_blank" '
            f'rel="noopener" title="{escape(t["larger"])}">{img}</a>'
        )
    return (
        f'<section id="screens"><div class="container">'
        f'<div class="section-head"><span class="eyebrow">{escape(t["eyebrow"])}</span>'
        f'<h2>{escape(t["head"])}</h2></div>'
        f'<div class="shots">{"".join(imgs)}</div></div></section>'
    )


def story_section(a):
    s = a["story"]
    return f"""<section id="story" class="tint"><div class="container"><div class="section-head"><span class="eyebrow">{escape(s[0])}</span><h2>{escape(s[1])}</h2></div><div class="story"><p>{escape(s[2])}</p><p>{escape(s[3])}</p><p class="pull">{escape(s[4])}</p><p>{escape(s[5])}</p></div></div></section>"""


MOMENTS_DELETION_ROUTE = "apps/moments/delete-account"
MOMENTS_DELETION_COPY = {
    "en": (
        "Request account deletion",
        "Request deletion of your Elia Moments account and the data associated with it.",
        "Email your deletion request",
        "Send the request from the email address you use for your Elia Account. Support will reply with the steps to verify the account before processing your request.",
        "Keep passwords, sign-in codes, photos and family details out of the email.",
        "In the app, open Settings → Elia Account → Delete Elia Account to start there.",
        "What happens to your data",
        "Once deletion is scheduled, you have 30 days to cancel. After that, your sign-in and personal cloud data are deleted. Copies on your device and backups you exported stay where you saved them.",
        "Photos and entries stay with the family if the shared archive continues. If you own the archive and other members are active, transfer ownership before deletion. Support can guide you. If you are the only member of an archive you own, that cloud archive is deleted after you confirm.",
    ),
    "de": (
        "Kontolöschung beantragen",
        "Beantrage die Löschung deines Elia Moments-Kontos und der zugehörigen Daten.",
        "Löschanfrage per E-Mail senden",
        "Sende die Anfrage von der E-Mail-Adresse, die du für dein Elia-Konto verwendest. Der Support erklärt dir in seiner Antwort, wie du dein Konto bestätigst, bevor er die Anfrage bearbeitet.",
        "Sende keine Passwörter, Anmeldecodes, Fotos oder Familiendaten per E-Mail.",
        "In der App findest du die Option unter Einstellungen → Elia-Konto → Elia-Konto löschen.",
        "Was mit deinen Daten geschieht",
        "Sobald die Löschung geplant ist, hast du 30 Tage Zeit, sie abzubrechen. Danach werden dein Zugang und deine persönlichen Cloud-Daten gelöscht. Kopien auf deinem Gerät und exportierte Sicherungen bleiben dort, wo du sie gespeichert hast.",
        "Fotos und Einträge bleiben bei der Familie, wenn das gemeinsame Archiv weiterbesteht. Wenn dir das Archiv gehört und andere Mitglieder aktiv sind, übertrage es vor der Löschung. Der Support kann dir dabei helfen. Wenn du das einzige Mitglied eines Archivs bist, das dir gehört, wird dieses Cloud-Archiv nach deiner Bestätigung gelöscht.",
    ),
    "es": (
        "Solicitar la eliminación de la cuenta",
        "Solicita la eliminación de tu cuenta de Elia Moments y de los datos asociados.",
        "Enviar la solicitud por correo",
        "Envía la solicitud desde la dirección de correo que usas para tu cuenta de Elia. El equipo de soporte te responderá con los pasos para verificar la cuenta antes de tramitar la solicitud.",
        "Evita incluir contraseñas, códigos de acceso, fotos o datos familiares en el correo.",
        "En la aplicación, ve a Ajustes → Cuenta de Elia → Eliminar cuenta de Elia.",
        "Qué ocurre con tus datos",
        "Una vez programada la eliminación, tienes 30 días para cancelarla. Después, se eliminan tu acceso y tus datos personales en la nube. Las copias en tu dispositivo y las copias de seguridad que exportaste se quedan donde las guardaste.",
        "Las fotos y las entradas se quedan con la familia si el archivo compartido sigue activo. Si eres la persona propietaria del archivo y hay otros miembros activos, transfiere la propiedad antes de la eliminación. El equipo de soporte puede ayudarte. Si eres la única persona que forma parte de un archivo del que eres propietaria, ese archivo en la nube se elimina tras tu confirmación.",
    ),
}


def moments_deletion_page(lang):
    route = MOMENTS_DELETION_ROUTE
    heading, intro, action, verification, email_safety, in_app, data_heading, data_summary, family = (
        MOMENTS_DELETION_COPY[lang]
    )
    common = APP[lang]["common"]
    nav = [
        ("Elia Moments", "apps/moments"),
        (common["support"], "apps/moments/support"),
        (common["privacy"], "apps/moments/privacy"),
    ]
    mailbox = "hello@getelia.app"
    request_link = f"mailto:{mailbox}?subject=Elia%20Moments%20account%20deletion%20request"
    body = f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
{head(lang, route, f"{heading} — Elia Moments", intro, "moments", extra=app_style("moments"))}
<body>
  {header(lang, route, nav, T[lang]["lang"])}
  <main>
    <section class="hero doc-hero">
      <div class="container prose">
        <h1>{escape(heading)}</h1>
        <p>{escape(intro)}</p>
        <div class="btn-row"><a class="btn btn--primary" href="{request_link}">{escape(action)}</a></div>
        <p><a href="{request_link}">{mailbox}</a></p>
        <p>{escape(verification)}</p>
        <p>{escape(email_safety)}</p>
        <p>{escape(in_app)}</p>
        <h2>{escape(data_heading)}</h2>
        <p>{escape(data_summary)}</p>
        <p>{escape(family)}</p>
      </div>
    </section>
  </main>
  {footer(lang, nav, T[lang]["note"], route)}
</body>
</html>
"""
    write(lang, route, body)


def support_page(lang, app):
    c = APP[lang]["common"]
    route = f"apps/{app}/support"
    app_name = f"Elia {app.capitalize()}"
    title = f"{c['support']} — {app_name}"
    desc = {
        "en": f"Help and answers for {app_name}. Common questions and how to reach us.",
        "de": f"Hilfe und Antworten für {app_name}. Häufige Fragen und Kontakt.",
        "es": f"Ayuda y respuestas para {app_name}. Preguntas frecuentes y contacto.",
    }[lang]
    extra = app_style(app)
    faq = "".join(f'<details{" open" if i == 0 else ""}><summary>{escape(q)}</summary><p>{escape(a).replace("privacy policy", f"<a href=\"{href(lang, f"apps/{app}/privacy", lang, route)}\">privacy policy</a>").replace("Datenschutzerklärung", f"<a href=\"{href(lang, f"apps/{app}/privacy", lang, route)}\">Datenschutzerklärung</a>").replace("política de privacidad", f"<a href=\"{href(lang, f"apps/{app}/privacy", lang, route)}\">política de privacidad</a>")}</p></details>' for i, (q, a) in enumerate(SUPPORT[lang][app]))
    deletion_link = ""
    if app == "moments":
        deletion_href = href(lang, MOMENTS_DELETION_ROUTE)
        deletion_label = MOMENTS_DELETION_COPY[lang][0]
        deletion_link = f'<p><a href="{deletion_href}">{escape(deletion_label)}</a></p>'
    body = f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
{head(lang, route, title, desc, "svg", None, extra)}
<body>
  {header(lang, route, [(app.capitalize(), f"apps/{app}"), (c["privacy"], f"apps/{app}/privacy"), (c["promise"], "home#philosophy")], T[lang]["lang"])}
  <main><section class="hero doc-hero"><div class="container"><a class="backlink" href="{href(lang, f"apps/{app}", lang, route)}">← {app_name}</a><h1>{escape(c["support"])}</h1><p class="updated">{escape({"en": "We keep things simple. Here are the common questions.", "de": "Wir halten es einfach. Hier sind die häufigsten Fragen.", "es": "Lo mantenemos simple. Estas son las preguntas más frecuentes."}[lang])}</p>{deletion_link}</div></section><section><div class="container"><div class="faq">{faq}</div><div class="prose" style="margin-top:40px;"><h2>{escape(c["still"])}</h2><p>{escape({"en": "Write to us at", "de": "Schreib uns an", "es": "Escríbenos a"}[lang])} <a href="mailto:{app}@getelia.app?subject=Elia%20{app.capitalize()}%20support">{app}@getelia.app</a>. {escape(c["read"])}</p></div></div></section></main>
  {footer(lang, [(c["overview"], f"apps/{app}"), (c["privacy"], f"apps/{app}/privacy"), (c["all"], "")], T[lang]["note"], route)}
</body>
</html>
"""
    write(lang, route, body)


def privacy_page(lang, app):
    c = APP[lang]["common"]
    route = f"apps/{app}/privacy"
    app_name = f"Elia {app.capitalize()}"
    title = f"{c['privacy']} — {app_name}"
    text = privacy_text(lang, app)
    desc = text["intro"]
    extra = app_style(app)
    sections = "".join(f"<h2>{escape(h)}</h2><p>{escape(p)}</p>" if isinstance(p, str) else f"<h2>{escape(h)}</h2>{ul(p, '')}" for h, p in text["sections"])
    deletion_link = ""
    if app == "moments":
        deletion_href = href(lang, MOMENTS_DELETION_ROUTE)
        deletion_label = MOMENTS_DELETION_COPY[lang][0]
        deletion_link = f'<p><a href="{deletion_href}">{escape(deletion_label)}</a></p>'
    body = f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
{head(lang, route, title, desc, "svg", None, extra)}
<body>
  {header(lang, route, [(app.capitalize(), f"apps/{app}"), (c["support"], f"apps/{app}/support"), (c["promise"], "home#philosophy")], T[lang]["lang"])}
  <main><section class="hero doc-hero"><div class="container"><a class="backlink" href="{href(lang, f"apps/{app}", lang, route)}">← {app_name}</a><h1>{escape(c["privacy"])}</h1><p class="updated">{app_name} · {escape(text["updated"])}</p></div></section><section><div class="container prose"><p>{escape(text["intro"])}</p>{sections}{deletion_link}<h2>{escape(text["contact"])}</h2><p>{escape(text["question"])} <a href="mailto:{app}@getelia.app">{app}@getelia.app</a>.</p><p class="muted">{escape(STUDIO[lang]["operator"])} <a href="{STUDIO_IMPRINT_URL}" rel="noopener">{escape(STUDIO[lang]["imprint"])}</a>.</p><div class="callout">{escape(text["callout"])}</div></div></section></main>
  {footer(lang, [(c["overview"], f"apps/{app}"), (c["support"], f"apps/{app}/support"), (c["all"], "")], T[lang]["note"], route)}
</body>
</html>
"""
    write(lang, route, body)


def app_style(app):
    if app not in ACCENTS:
        return ""
    accent, dark, light, light_dark = ACCENTS[app]
    return f"""  <style>
    body {{ --accent: {accent}; --accent-dark: {dark}; --accent-light: {light}; }}
    [data-theme="dark"] body {{ --accent-light: {light_dark}; }}
  </style>
"""


def privacy_text(lang, app):
    data = {
        "en": {
            "updated": "Last updated 19 November 2026",
            "intro": "You can use the app offline without an Elia Account. In local use, entries, history and settings are saved on your device.",
            "sharing": "Sharing and cloud storage",
            "contractions": "The current public Android version keeps contraction times and session history on your device. Sharing a summary sends it to the recipient you choose. Your contraction history is personal and is not shared with family members through an invitation.",
            "feeding": "The current public Android version stores feeding, pumping and diaper records on your device. It does not automatically send them to another parent. You can export a summary and choose who receives it.",
            "moments": "In a local archive, notes and selected photos stay on your device. If you connect a family archive, shared entries and supported photos are stored in the cloud. Family members can access them according to their roles. Cloud backup keeps supported photo originals, including embedded metadata such as GPS coordinates if present. Places in entries are labels you add yourself. Moments does not request your device’s location.",
            "backup": "Backups and deletion",
            "backup_note": "You choose where to save a manual backup or export. Clearing the app’s storage removes the local copy. Files you exported, summaries you sent and copies already stored in a connected account or family archive are separate. Contact us below for help with account data.",
            "network": "Permissions and tracking",
            "network_note": "Local recording works without an internet connection. The apps are designed for adults and caregivers. Elia does not sell your entries. The apps contain no ads or third-party tracking SDKs. Cloud features require a connection.",
            "contact": "Contact", "question": "For privacy questions, write to",
        },
        "de": {
            "updated": "Zuletzt aktualisiert am 19. November 2026",
            "intro": "Du kannst die App offline und ohne Elia Account verwenden. Bei lokaler Nutzung werden Einträge, Verlauf und Einstellungen auf deinem Gerät gespeichert.",
            "sharing": "Teilen und Cloud-Speicherung",
            "contractions": "Die aktuelle öffentliche Android-Version speichert Wehenzeiten und Sitzungsverlauf auf deinem Gerät. Beim Teilen einer Zusammenfassung wählst du den Empfänger. Eine Familieneinladung gibt anderen Familienmitgliedern keinen Zugriff auf deinen persönlichen Wehenverlauf.",
            "feeding": "Die aktuelle öffentliche Android-Version speichert Mahlzeiten, Abpumpen und Windelwechsel auf deinem Gerät. Sie sendet diese Einträge nicht automatisch an den anderen Elternteil. Du kannst eine Zusammenfassung exportieren und den Empfänger auswählen.",
            "moments": "Im lokalen Archiv bleiben Notizen und ausgewählte Fotos auf deinem Gerät. Wenn du ein Familienarchiv verbindest, werden geteilte Einträge und unterstützte Fotos in der Cloud gespeichert. Familienmitglieder haben entsprechend ihrer Rolle Zugriff. Die Cloud-Sicherung bewahrt unterstützte Originalfotos mit ihren Metadaten auf. Dazu können GPS-Koordinaten gehören. Ortsnamen in Einträgen gibst du selbst ein. Moments fragt den Standort deines Geräts nicht ab.",
            "backup": "Sicherung und Löschung",
            "backup_note": "Den Speicherort manueller Sicherungen und Exporte wählst du selbst. Wenn du den App-Speicher löschst, entfernst du die lokale Kopie. Exportierte Dateien, versendete Zusammenfassungen und bereits in einem verbundenen Konto oder Familienarchiv gespeicherte Kopien bleiben davon unberührt. Bei Fragen zu Kontodaten erreichst du uns unter der Adresse unten.",
            "network": "Berechtigungen und Tracking",
            "network_note": "Lokale Einträge kannst du ohne Internetverbindung erfassen. Die Apps richten sich an Erwachsene und Betreuungspersonen. Elia verkauft deine Einträge nicht. Die Apps enthalten weder Werbung noch Tracking-SDKs von Drittanbietern. Cloud-Funktionen benötigen eine Verbindung.",
            "contact": "Kontakt", "question": "Bei Datenschutzfragen schreib an",
        },
        "es": {
            "updated": "Actualizado el 19 de noviembre de 2026",
            "intro": "Puedes usar la app sin conexión y sin Elia Account. En el uso local, las entradas, el historial y los ajustes se guardan en tu dispositivo.",
            "sharing": "Datos compartidos y almacenamiento en la nube",
            "contractions": "La versión pública actual de Android guarda los tiempos de las contracciones y el historial en tu dispositivo. Al compartir un resumen, tú eliges el destinatario. Una invitación familiar no da acceso a tu historial personal de contracciones.",
            "feeding": "La versión pública actual de Android guarda las tomas, las extracciones y los cambios de pañal en tu dispositivo. No los envía automáticamente a otro cuidador. Puedes exportar un resumen y elegir quién lo recibe.",
            "moments": "En un archivo local, las notas y las fotos seleccionadas se quedan en tu dispositivo. Si conectas un archivo familiar, las entradas compartidas y las fotos compatibles se guardan en la nube. Los miembros de la familia pueden acceder según su función. La copia en la nube conserva los originales de las fotos compatibles y sus metadatos, incluidas las coordenadas GPS si están presentes. Tú añades el nombre del lugar en cada entrada. Moments no solicita la ubicación de tu dispositivo.",
            "backup": "Copias de seguridad y borrado",
            "backup_note": "Tú eliges dónde guardar una copia manual o una exportación. Borrar los datos de la app elimina la copia local. Los archivos exportados, los resúmenes enviados y las copias ya guardadas en una cuenta o archivo familiar conectado se conservan por separado. Si necesitas ayuda con los datos de tu cuenta, escríbenos a la dirección de abajo.",
            "network": "Permisos y seguimiento",
            "network_note": "Puedes registrar entradas locales sin internet. Las apps están pensadas para adultos y cuidadores. Elia no vende tus registros. Las apps no contienen anuncios ni SDK de seguimiento de terceros. Las funciones en la nube requieren conexión.",
            "contact": "Contacto", "question": "Para consultas sobre privacidad, escribe a",
        },
    }[lang]
    return {
        **data, "sections": [(data["sharing"], data[app]), (data["backup"], data["backup_note"]),
                             (data["network"], data["network_note"])],
        "callout": APP[lang][app]["principles"][-1],
    }


def not_found(lang):
    route = ""
    title = {"en": "Page not found — Elia", "de": "Seite nicht gefunden — Elia", "es": "Página no encontrada — Elia"}[lang]
    text = {"en": "Take a breath. This page doesn't exist — but the rest of Elia does.", "de": "Atme kurz durch. Diese Seite gibt es nicht — der Rest von Elia schon.", "es": "Respira. Esta página no existe, pero el resto de Elia sí."}[lang]
    btn = {"en": "Back to Elia", "de": "Zurück zu Elia", "es": "Volver a Elia"}[lang]
    body = f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
{head(lang, "", title, text, extra='  <meta name="robots" content="noindex" />\n')}
<body><main><section class="hero"><div class="container"><img class="brand__mark" src="{asset("assets/img/logo-elia.png", lang, route)}" alt="" style="width:44px;height:44px;border-radius:50%;margin:0 auto 24px;" /><h1 class="hero__wordmark" style="font-size:clamp(40px,9vw,72px);">{escape(title.split(" — ")[0])}</h1><p class="hero__sub lead">{escape(text)}</p><div class="btn-row"><a class="btn btn--primary" href="{href(lang, "", lang, route)}">{escape(btn)}</a></div></div></section></main></body></html>"""
    if lang == "en":
        (ROOT / "404.html").write_text(body, encoding="utf-8")

def sitemap():
    routes = [""] + [f"apps/{a}" for a in APPS] + [f"apps/{a}/{sub}" for a in APPS for sub in ("privacy", "support")]
    routes.append(MOMENTS_DELETION_ROUTE)
    urls = []
    for route in routes:
        for lang in LANGS:
            urls.append(f"""  <url>
    <loc>{url(lang, route)}</loc>
    <lastmod>{LASTMOD}</lastmod>
    <priority>{"1.0" if route == "" else "0.8" if route.count("/") == 1 else "0.3"}</priority>
  </url>""")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")


def write(lang, route, body):
    path = out_path(lang, route)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


for lang in LANGS:
    home(lang)
    for app in APPS:
        app_page(lang, app)
        privacy_page(lang, app)
        support_page(lang, app)
    moments_deletion_page(lang)
    not_found(lang)
sitemap()
