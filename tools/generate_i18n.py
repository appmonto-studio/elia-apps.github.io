from pathlib import Path
from html import escape
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://getelia.app"
LANGS = ["en", "de", "es"]
LOCALES = {"en": "en_US", "de": "de_DE", "es": "es_ES"}
LANG_LABELS = {"en": "EN", "de": "DE", "es": "ES"}
URL_PREFIXES = {"en": "", "de": "de", "es": "es"}
APPS = ["contractions", "feeding", "moments"]
APP_ICONS = ["contractions", "feeding", "moments"]
APP_NAMES = {"contractions": "Contractions", "feeding": "Feeding", "moments": "Moments"}
CARD_ACCENTS = {"contractions": "rose", "feeding": "honey", "moments": "sage"}
CARD_KEYS = {"contractions": "contr_card", "feeding": "feed_card", "moments": "moments_card"}
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
    icon_link = f'  <link rel="icon" href="{asset("assets/img/favicon.svg", lang, route)}" type="image/svg+xml" />'
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
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}" />
  <meta name="theme-color" content="#FBF9F8" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#271F25" media="(prefers-color-scheme: dark)" />
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
    return f"""<header class="site-header">
    <div class="container">
      <a class="brand" href="{href(lang, "", lang, route)}" aria-label="Elia home">
        <img class="brand__mark" src="{asset("assets/img/favicon.svg", lang, route)}" alt="" />
        <span class="brand__name">Elia</span>
      </a>
      <nav class="nav" aria-label="Primary">
        {nav_html}
      </nav>
      {lang_switch(lang, route, aria)}
    </div>
  </header>"""


def footer(lang, links, note, route=""):
    links_html = "\n        ".join(f'<a href="{href(lang, link, lang, route)}">{escape(text)}</a>' if not link.startswith("mailto:") and not link.startswith("#") else f'<a href="{link}">{escape(text)}</a>' for text, link in links)
    return f"""<footer class="site-footer">
    <div class="container">
      <a class="brand" href="{href(lang, "", lang, route)}" aria-label="Elia home">
        <img class="brand__mark" src="{asset("assets/img/favicon.svg", lang, route)}" alt="" />
        <span class="brand__name">Elia</span>
      </a>
      <div class="foot-links">
        {links_html}
      </div>
      <small>{escape(note)} © <span id="year">2026</span> Elia.</small>
    </div>
  </footer>

  <script>document.getElementById('year').textContent = new Date().getFullYear();</script>"""


T = {'en': {'lang': 'Language',
        'note': 'Not a medical device.',
        'home': {'title': "Elia — calm, private apps for birth and the years that follow",
                 'description': 'Elia is a small family of calm, private, offline-first apps for birth, the early days '
                                'with your baby, and the childhood years that follow. No account. No ads. No cloud.',
                 'nav': [('Apps', '#apps'), ('Philosophy', '#philosophy'), ('Story', '#story')],
                 'hero': ['Elia',
                          'Calm companions for birth and beyond.',
                          'A small family of private, offline-first apps for birth, the early days with your baby, and '
                          'the childhood years that follow. No account. No ads. No cloud.',
                          'See the apps',
                          'Why Elia'],
                 'apps_head': ['The apps',
                               'Three apps for three chapters.',
                               'Each does one thing calmly, and gets out of your way.'],
                 'coming': 'Coming soon',
                 'learn': 'Learn more',
                 'contr_card': ['Elia Contractions',
                                'A calm companion for birth. Time contractions clearly, stay present, and share a '
                                'simple summary with your care team.'],
                 'feed_card': ['Elia Feeding',
                               'A calm, private feeding log for the first days with your baby. Tap what just happened '
                               '— Elia remembers the rest.'],
                 'promise': ['The promise',
                             'The interface should reduce stress, not add to it.',
                             'Elia is warm, quiet, and trustworthy — like a calm midwife and a supportive partner, not '
                             'like hospital software. Every Elia app follows the same principles.'],
                 'chips': ['No account',
                           'No ads',
                           'No subscriptions',
                           'No cloud sync',
                           'No analytics',
                           'Offline-first',
                           'Local-only by default',
                           'No judgement'],
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
        'home': {'title': 'Elia — ruhige, private Apps für Geburt und Kindheit',
                 'description': 'Elia ist eine kleine Familie ruhiger, privater Offline-first-Apps für die '
                                'Geburt, die ersten Tage mit deinem Baby und die Kindheitsjahre danach. Kein Konto. '
                                'Keine Werbung. Keine Cloud.',
                 'nav': [('Apps', '#apps'), ('Philosophie', '#philosophy'), ('Geschichte', '#story')],
                 'hero': ['Elia',
                          'Ruhige Begleiter für Geburt und die Zeit danach.',
                          'Eine kleine Familie privater Offline-first-Apps für die Geburt, die ersten Tage mit deinem '
                          'Baby und die Kindheitsjahre danach. Kein Konto. Keine Werbung. Keine Cloud.',
                          'Apps ansehen',
                          'Warum Elia'],
                 'apps_head': ['Die Apps',
                               'Drei Apps für drei Kapitel.',
                               'Jede tut ruhig eine Sache und tritt dann in den Hintergrund.'],
                 'coming': 'Demnächst',
                 'learn': 'Mehr erfahren',
                 'contr_card': ['Elia Contractions',
                                'Ein ruhiger Begleiter für die Geburt. Wehen klar erfassen, präsent bleiben und bei '
                                'Bedarf eine einfache Zusammenfassung teilen.'],
                 'feed_card': ['Elia Feeding',
                               'Ein ruhiges, privates Still- und Fütterungsprotokoll für die ersten Tage mit deinem '
                               'Baby. Tippe, was gerade passiert ist — Elia merkt sich den Rest.'],
                 'promise': ['Das Versprechen',
                             'Die Oberfläche soll Stress reduzieren, nicht erhöhen.',
                             'Elia ist warm, leise und vertrauenswürdig — eher wie eine ruhige Hebamme und ein '
                             'unterstützender Partner als wie Krankenhaussoftware. Jede Elia-App folgt denselben '
                             'Prinzipien.'],
                 'chips': ['Kein Konto',
                           'Keine Werbung',
                           'Keine Abos',
                           'Keine Cloud-Synchronisierung',
                           'Keine Analyse',
                           'Offline-first',
                           'Standardmäßig lokal',
                           'Kein Urteil'],
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
        'home': {'title': 'Elia — apps tranquilas y privadas para el parto y la infancia',
                 'description': 'Elia es una pequeña familia de apps tranquilas, privadas y offline-first para el '
                                'parto, los primeros días con tu bebé y los años de infancia que siguen. Sin cuenta. '
                                'Sin anuncios. Sin sincronización en la nube.',
                 'nav': [('Apps', '#apps'), ('Filosofía', '#philosophy'), ('Historia', '#story')],
                 'hero': ['Elia',
                          'Compañeras tranquilas para el parto y lo que viene después.',
                          'Una pequeña familia de apps privadas y offline-first para el parto, los primeros días con '
                          'tu bebé y los años de infancia que siguen. Sin cuenta. Sin anuncios. Sin sincronización '
                          'en la nube.',
                          'Ver las apps',
                          'Por qué Elia'],
                 'apps_head': ['Las apps',
                               'Tres apps para tres capítulos.',
                               'Cada una hace una cosa con calma y no se interpone.'],
                 'coming': 'Próximamente',
                 'learn': 'Más información',
                 'contr_card': ['Elia Contractions',
                                'Una compañera tranquila para el parto. Registra las contracciones con claridad, '
                                'mantente presente y comparte un resumen sencillo con tu equipo de atención.'],
                 'feed_card': ['Elia Feeding',
                               'Un registro tranquilo y privado de alimentación para los primeros días con tu bebé. Toca lo '
                               'que acaba de pasar; Elia recuerda el resto.'],
                 'promise': ['La promesa',
                             'La interfaz debería reducir el estrés, no añadirlo.',
                             'Elia es cálida, discreta y confiable: más parecida a una presencia tranquila y una pareja '
                             'que acompaña que a un software de hospital. Todas las apps de Elia siguen los mismos '
                             'principios.'],
                 'chips': ['Sin cuenta',
                           'Sin anuncios',
                           'Sin suscripciones',
                           'Sin sincronización en la nube',
                           'Sin analíticas',
                           'Offline-first',
                           'Local por defecto',
                           'Sin juicio'],
                 'story': ['Nuestra historia',
                           'Elia nació en una sala de parto.',
                           'Durante el parto, una pareja abrió una app de contracciones. Iba lenta. El botón principal '
                           'nunca dejaba claro si el registro había empezado. Las funciones útiles estaban detrás de '
                           'una suscripción. Tras tres contracciones dijo que fueran al hospital, donde la familia ya '
                           'estaba.',
                           'La app añadió estrés. Elia es la respuesta a ese momento: la compañera que nos habría '
                           'gustado tener.',
                           'Su bebé nació esa noche. Elia nació el mismo día y creció hasta convertirse en una pequeña '
                           'familia de apps para los días tranquilos, cansados e importantes que vienen después.']}}}


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
        'contractions': {'title': 'Elia Contractions — a calm companion for birth',
                         'desc': 'Elia Contractions is a calm, offline-first contraction companion for families during '
                                 'labor. Time contractions clearly, stay present, and share a simple summary.',
                         'tag': 'A calm companion for birth.',
                         'sub': 'A contraction companion for families during labor, built around one belief: during '
                                'labor, the interface should reduce stress, not add to it.',
                         'head': ['What it is', 'Just enough, exactly when it matters.'],
                         'left': 'Elia Contractions helps you',
                         'right': 'What it is not',
                         'yes': ['Record contractions with one clear tap.',
                                 'Review timing and intervals at a glance.',
                                 'Stay focused during a contraction.',
                                 'Stay present between them.',
                                 'Keep a simple, honest history.',
                                 'Share a clear summary with your care team, if useful.'],
                         'no': ['A medical device or diagnostic tool.',
                                'A replacement for doctors or midwives.',
                                'A pregnancy or baby tracker.',
                                'A subscription trap.',
                                'An advertising surface.',
                                'Something that tells you what to do.'],
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
                         'principles': ['Calm, private, and yours.',
                                        ['Offline-first',
                                         'Local-only',
                                         'No account',
                                         'No ads',
                                         'No subscription for core',
                                         'No analytics'],
                                        'Elia Contractions is not a medical device and does not provide medical advice '
                                        'or diagnosis. It never tells you when to go to the hospital. Always follow '
                                        'the guidance of your doctors and midwives.']},
        'feeding': {'title': 'Elia Feeding — a calm feeding log for the first days',
                    'desc': 'Elia Feeding is a calm, private newborn feeding and care log for the first days with your '
                            'baby. No account. No cloud. No judgement.',
                    'tag': 'Remember just enough.',
                    'sub': 'A calm, private feeding log for the first days with your baby. No account. No cloud. No '
                           'judgement. Just the last feed, the next action, and a simple history.',
                    'pull': ['Open the app. Tap the thing that just happened. Elia remembers.',
                             'Most baby trackers help you measure everything. Elia helps you remember just enough.'],
                    'head': ['What it does', 'Fast, obvious logging — one hand, low attention.'],
                    'left': 'In the app',
                    'right': 'Deliberately not included',
                    'yes': ['Breastfeeding timer with Left / Right side.',
                            'Bottle feeding log, with optional amount.',
                            'Simple diaper log: wet, dirty, or both.',
                            'A home screen showing the current state and last useful context.',
                            'A quiet history you can edit or delete.',
                            'Share or export as plain text.'],
                    'no': ['Accounts, cloud, or multi-parent sync.',
                           'Growth charts and analytics.',
                           'Feeding targets, streaks, or warnings.',
                           'Medical recommendations.',
                           'Sleep, medication, or pumping inventory.',
                           'Ads or billing.'],
                    'principles': ['Calm, private, and yours.',
                                   'No goals, warnings, or pressure. Elia remembers what you log — nothing more.',
                                   ['No account',
                                    'No ads',
                                    'No subscriptions',
                                    'No backend',
                                    'No cloud sync',
                                    'No analytics',
                                    'Offline-first',
                                    'No judgement'],
                                   'Elia Feeding is a calm memory aid, not a medical tool. It does not give medical '
                                   "advice and does not define what is normal. For anything about your baby's health, "
                                   'talk to your pediatrician or midwife.']}},
 'de': {'common': {'overview': 'Überblick',
                   'support': 'Support',
                   'privacy': 'Datenschutz',
                   'all': 'Alle Apps',
                   'back': '← Alle Elia-Apps',
                   'what': 'Was es ist',
                   'does': 'Was es tut',
                   'promise': 'Versprechen',
                   'why': 'Warum es existiert',
                   'still': 'Brauchst du Hilfe?',
                   'read': 'Wir lesen jede Nachricht.'},
        'contractions': {'title': 'Elia Contractions — ein ruhiger Begleiter für die Geburt',
                         'desc': 'Elia Contractions ist ein ruhiger Offline-first-Begleiter für Familien während der '
                                 'Geburt. Wehen klar erfassen, präsent bleiben und eine einfache Zusammenfassung '
                                 'teilen.',
                         'tag': 'Ein ruhiger Begleiter für die Geburt.',
                         'sub': 'Ein Wehenbegleiter für Familien während der Geburt, gebaut um eine Überzeugung: '
                                'Während der Geburt soll die Oberfläche Stress reduzieren, nicht erhöhen.',
                         'head': ['Was es ist', 'Gerade genug, genau dann, wenn es zählt.'],
                         'left': 'Elia Contractions hilft dir',
                         'right': 'Was es nicht ist',
                         'yes': ['Wehen mit einem klaren Tippen erfassen.',
                                 'Dauer und Abstände auf einen Blick prüfen.',
                                 'Während einer Wehe fokussiert bleiben.',
                                 'Zwischen den Wehen präsent bleiben.',
                                 'Eine einfache, ehrliche Historie behalten.',
                                 'Bei Bedarf eine klare Zusammenfassung mit dem Betreuungsteam teilen.'],
                         'no': ['Ein Medizinprodukt oder Diagnosewerkzeug.',
                                'Ein Ersatz für Ärztinnen, Ärzte oder Hebammen.',
                                'Ein Schwangerschafts- oder Babytracker.',
                                'Eine Abo-Falle.',
                                'Eine Werbefläche.',
                                'Etwas, das dir sagt, was du tun sollst.'],
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
                         'principles': ['Ruhig, privat und dein.',
                                        ['Offline-first',
                                         'Nur lokal',
                                         'Kein Konto',
                                         'Keine Werbung',
                                         'Kernfunktionen ohne Abo',
                                         'Keine Analyse'],
                                        'Elia Contractions ist kein Medizinprodukt und gibt keine medizinische '
                                        'Beratung oder Diagnose. Sie sagt dir nie, wann du ins Krankenhaus fahren '
                                        'sollst. Folge immer den Empfehlungen deiner Ärztinnen, Ärzte und Hebammen.']},
        'feeding': {'title': 'Elia Feeding — ein ruhiges Fütterungsprotokoll für die ersten Tage',
                    'desc': 'Elia Feeding ist ein ruhiges, privates Protokoll für Füttern und Pflege in den ersten '
                            'Tagen mit deinem Baby. Kein Konto. Keine Cloud. Kein Urteil.',
                    'tag': 'Gerade genug merken.',
                    'sub': 'Ein ruhiges, privates Fütterungsprotokoll für die ersten Tage mit deinem Baby. Kein Konto. '
                           'Keine Cloud. Kein Urteil. Nur die letzte Mahlzeit, die nächste Aktion und eine einfache '
                           'Historie.',
                    'pull': ['App öffnen. Antippen, was gerade passiert ist. Elia merkt es sich.',
                             'Die meisten Babytracker helfen, alles zu messen. Elia hilft, gerade genug im Kopf zu '
                             'behalten.'],
                    'head': ['Was es tut', 'Schnelles, klares Protokollieren — mit einer Hand, wenig Aufmerksamkeit.'],
                    'left': 'In der App',
                    'right': 'Bewusst nicht enthalten',
                    'yes': ['Still-Timer mit linker / rechter Seite.',
                            'Fläschchen-Protokoll mit optionaler Menge.',
                            'Einfaches Windelprotokoll: nass, schmutzig oder beides.',
                            'Startseite mit aktuellem Zustand und dem letzten nützlichen Kontext.',
                            'Eine ruhige Historie, die du bearbeiten oder löschen kannst.',
                            'Teilen oder Export als Klartext.'],
                    'no': ['Konten, Cloud oder Synchronisierung zwischen Eltern.',
                           'Wachstumskurven und Analysen.',
                           'Fütterungsziele, Serien oder Warnungen.',
                           'Medizinische Empfehlungen.',
                           'Schlaf, Medikamente oder Pumpvorräte.',
                           'Werbung oder Bezahlung.'],
                    'principles': ['Ruhig, privat und dein.',
                                   'Keine Ziele, Warnungen oder Druck. Elia merkt sich, was du einträgst — mehr nicht.',
                                   ['Kein Konto',
                                    'Keine Werbung',
                                    'Keine Abos',
                                    'Kein Backend',
                                    'Keine Cloud-Synchronisierung',
                                    'Keine Analyse',
                                    'Offline-first',
                                    'Kein Urteil'],
                                   'Elia Feeding ist eine ruhige Gedächtnisstütze, kein medizinisches Werkzeug. Sie '
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
        'contractions': {'title': 'Elia Contractions — una compañera tranquila para el parto',
                         'desc': 'Elia Contractions es una compañera tranquila y offline-first para familias durante '
                                 'el parto. Registra contracciones con claridad, mantente presente y comparte un '
                                 'resumen sencillo.',
                         'tag': 'Una compañera tranquila para el parto.',
                         'sub': 'Una compañera de contracciones para familias durante el parto, creada alrededor de '
                                'una idea: durante el parto, la interfaz debería reducir el estrés, no añadirlo.',
                         'head': ['Qué es', 'Lo justo, justo cuando importa.'],
                         'left': 'Elia Contractions te ayuda a',
                         'right': 'Qué no es',
                         'yes': ['Registrar contracciones con un toque claro.',
                                 'Ver duración e intervalos de un vistazo.',
                                 'Mantener el foco durante una contracción.',
                                 'Estar presente entre una y otra.',
                                 'Conservar un historial simple y honesto.',
                                 'Compartir un resumen claro con tu equipo de atención, si resulta útil.'],
                         'no': ['Un dispositivo médico o herramienta de diagnóstico.',
                                'Un reemplazo de profesionales de salud.',
                                'Un tracker de embarazo o bebé.',
                                'Una trampa de suscripción.',
                                'Un espacio para anuncios.',
                                'Algo que te diga qué hacer.'],
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
                         'principles': ['Tranquila, privada y tuya.',
                                        ['Offline-first',
                                         'Solo local',
                                         'Sin cuenta',
                                         'Sin anuncios',
                                         'Funciones esenciales sin suscripción',
                                         'Sin analíticas'],
                                        'Elia Contractions no es un dispositivo médico y no ofrece consejo médico ni '
                                        'diagnóstico. Nunca te dice cuándo ir al hospital. Sigue siempre las '
                                        'indicaciones de tus profesionales de salud.']},
        'feeding': {'title': 'Elia Feeding — un registro tranquilo de alimentación para los primeros días',
                    'desc': 'Elia Feeding es un registro tranquilo y privado de alimentación y cuidados del recién nacido '
                            'para los primeros días con tu bebé. Sin cuenta. Sin sincronización en la nube. Sin juicio.',
                    'tag': 'Recordar justo lo necesario.',
                    'sub': 'Un registro tranquilo y privado de alimentación para los primeros días con tu bebé. Sin cuenta. '
                           'Sin sincronización en la nube. Sin juicio. Solo la última alimentación, la siguiente acción y un historial sencillo.',
                    'pull': ['Abre la app. Toca lo que acaba de pasar. Elia lo recuerda.',
                             'La mayoría de apps para bebés ayudan a medirlo todo. Elia te ayuda a recordar justo lo '
                             'necesario.'],
                    'head': ['Qué hace', 'Registro rápido y obvio: una mano, poca atención.'],
                    'left': 'En la app',
                    'right': 'Deliberadamente no incluido',
                    'yes': ['Temporizador de lactancia con lado izquierdo / derecho.',
                            'Registro de biberón, con cantidad opcional.',
                            'Registro simple de pañales: pis, caca o ambos.',
                            'Pantalla principal con el estado actual y el último contexto útil.',
                            'Un historial tranquilo que puedes editar o borrar.',
                            'Compartir o exportar como texto plano.'],
                    'no': ['Cuentas o sincronización en la nube entre cuidadores.',
                           'Gráficas de crecimiento y analíticas.',
                           'Objetivos de alimentación, rachas o alertas.',
                           'Recomendaciones médicas.',
                           'Sueño, medicación o inventario de extracción.',
                           'Anuncios o pagos.'],
                    'principles': ['Tranquila, privada y tuya.',
                                   'Sin objetivos, alertas ni presión. Elia recuerda lo que registras, nada más.',
                                   ['Sin cuenta',
                                    'Sin anuncios',
                                    'Sin suscripciones',
                                    'Sin backend',
                                    'Sin sincronización en la nube',
                                    'Sin analíticas',
                                    'Offline-first',
                                    'Sin juicio'],
                                   'Elia Feeding es una ayuda tranquila para la memoria, no una herramienta médica. No '
                                   'da consejos médicos ni define qué es normal. Para cualquier duda sobre la salud de '
                                   'tu bebé, habla con tu pediatra o profesional de salud.']}}}


SUPPORT = {'en': {'contractions': [('Is my data private?',
                          'Yes. Elia Contractions has no account and no backend. Your contraction times, history, and '
                          'settings stay on your device. See the privacy policy for details.'),
                         ('Does it work offline?',
                          'Yes. Recording contractions never needs an internet connection. The app is built to be '
                          'reliable in a delivery room, not dependent on a signal.'),
                         ('Does it tell me when to go to the hospital?',
                          'No. Elia does not diagnose or give medical directives. It shows your contractions clearly '
                          'so you can share them with your care team. Always follow the guidance of your doctors and '
                          'midwives.'),
                         ('Can I correct a mistake?',
                          'Yes. You can edit or delete entries calmly. Nothing is permanent by accident.'),
                         ('How do I share a summary with my midwife or doctor?',
                          "You can export or share your session as plain text using your device's share options. You "
                          'choose where it goes; Elia never sends it anywhere on its own.'),
                         ('Is there a subscription?',
                          'The core experience is not a subscription trap. Elia will never lock essential labor '
                          'features behind a paywall or show ads.')],
        'feeding': [('Is my data private?',
                     'Yes. Elia Feeding has no account, no backend, and no cloud. Your entries and settings stay on '
                     'your device. See the privacy policy for details.'),
                    ('Does it work offline?',
                     'Yes. Logging a feed, bottle, or diaper never needs an internet connection.'),
                    ('Does it tell me if my baby is feeding enough?',
                     'No. Elia does not set targets, warnings, or judgements, and does not define what is normal. It '
                     "simply remembers what you log. For anything about your baby's health, talk to your pediatrician "
                     'or midwife.'),
                    ('Can I edit or delete an entry?',
                     'Yes. You can edit or delete any entry. Nothing is permanent by accident.'),
                    ('Can two parents share the same log?',
                     'Not in the current version. Elia Feeding is local-only by design, so there is no cloud sync '
                     'between devices. Everything lives on the one device you log on.'),
                    ('How do I move my log somewhere else?',
                     "You can export or share it as plain text using your device's share options. You choose the "
                     'destination; Elia never sends it anywhere on its own.'),
                    ('Are there ads or subscriptions?',
                     'No ads, no subscriptions, no billing. Elia Feeding is a calm memory aid, not a monetization '
                     'funnel.')]},
 'de': {'contractions': [('Sind meine Daten privat?',
                          'Ja. Elia Contractions hat kein Konto und kein Backend. Wehenzeiten, Historie und '
                          'Einstellungen bleiben auf deinem Gerät. Details stehen in der Datenschutzerklärung.'),
                         ('Funktioniert es offline?',
                          'Ja. Wehen zu erfassen braucht nie eine Internetverbindung. Die App soll im Kreißsaal '
                          'verlässlich sein, nicht vom Empfang abhängen.'),
                         ('Sagt die App mir, wann ich ins Krankenhaus fahren soll?',
                          'Nein. Elia diagnostiziert nicht und gibt keine medizinischen Anweisungen. Sie zeigt deine '
                          'Wehen klar, damit du sie mit deinem Betreuungsteam teilen kannst. Folge immer den '
                          'Empfehlungen deiner Ärztinnen, Ärzte und Hebammen.'),
                         ('Kann ich einen Fehler korrigieren?',
                          'Ja. Du kannst Einträge ruhig bearbeiten oder löschen. Nichts ist aus Versehen endgültig.'),
                         ('Wie teile ich eine Zusammenfassung mit Hebamme oder Arzt?',
                          'Du kannst deine Sitzung als Klartext über die Teilen-Funktionen deines Geräts exportieren. '
                          'Du wählst das Ziel; Elia sendet nie von selbst etwas.'),
                         ('Gibt es ein Abo?',
                          'Die Kernfunktionen sind keine Abo-Falle. Elia wird wichtige Geburtsfunktionen nie hinter '
                          'einer Paywall verstecken oder Werbung zeigen.')],
        'feeding': [('Sind meine Daten privat?',
                     'Ja. Elia Feeding hat kein Konto, kein Backend und keine Cloud. Deine Einträge und Einstellungen '
                     'bleiben auf deinem Gerät. Details stehen in der Datenschutzerklärung.'),
                    ('Funktioniert es offline?',
                     'Ja. Füttern, Fläschchen oder Windeln zu protokollieren braucht nie Internet.'),
                    ('Sagt die App, ob mein Baby genug trinkt?',
                     'Nein. Elia setzt keine Ziele, Warnungen oder Urteile und definiert nicht, was normal ist. Sie '
                     'merkt sich nur, was du einträgst. Wenn es um die Gesundheit deines Babys geht, sprich mit '
                     'Kinderarzt, Kinderärztin oder Hebamme.'),
                    ('Kann ich einen Eintrag bearbeiten oder löschen?',
                     'Ja. Du kannst jeden Eintrag bearbeiten oder löschen. Nichts ist aus Versehen endgültig.'),
                    ('Können zwei Eltern dasselbe Protokoll teilen?',
                     'In der aktuellen Version nicht. Elia Feeding ist bewusst lokal, daher gibt es keine '
                     'Cloud-Synchronisierung zwischen Geräten. Alles bleibt auf dem Gerät, auf dem du protokollierst.'),
                    ('Wie verschiebe ich mein Protokoll woandershin?',
                     'Du kannst es als Klartext über die Teilen-Funktionen deines Geräts exportieren. Du wählst das '
                     'Ziel; Elia sendet nie von selbst etwas.'),
                    ('Gibt es Werbung oder Abos?',
                     'Keine Werbung, keine Abos, keine Bezahlung. Elia Feeding ist eine ruhige Gedächtnisstütze, kein '
                     'Monetarisierungstrichter.')]},
 'es': {'contractions': [('¿Mis datos son privados?',
                          'Sí. Elia Contractions no tiene cuenta ni backend. Tus tiempos de contracciones, historial y '
                          'ajustes se quedan en tu dispositivo. Consulta la política de privacidad para más detalles.'),
                         ('¿Funciona sin conexión?',
                          'Sí. Registrar contracciones nunca necesita conexión a internet. La app está pensada para '
                          'ser fiable en una sala de parto, no para depender de la señal.'),
                         ('¿Me dice cuándo ir al hospital?',
                          'No. Elia no diagnostica ni da instrucciones médicas. Muestra tus contracciones con claridad '
                          'para que puedas compartirlas con tu equipo de atención. Sigue siempre las indicaciones de '
                          'tus profesionales de salud.'),
                         ('¿Puedo corregir un error?',
                          'Sí. Puedes editar o borrar entradas con calma. Nada queda permanente por accidente.'),
                         ('¿Cómo comparto un resumen con mi equipo de salud?',
                          'Puedes exportar o compartir tu sesión como texto plano usando las opciones de compartir de '
                          'tu dispositivo. Tú eliges el destino; Elia nunca envía nada por su cuenta.'),
                         ('¿Hay suscripción?',
                          'La experiencia principal no es una trampa de suscripción. Elia nunca bloqueará funciones '
                          'esenciales del parto detrás de un pago ni mostrará anuncios.')],
        'feeding': [('¿Mis datos son privados?',
                     'Sí. Elia Feeding no tiene cuenta, backend ni sincronización en la nube. Tus entradas y ajustes se quedan en tu '
                     'dispositivo. Consulta la política de privacidad para más detalles.'),
                    ('¿Funciona sin conexión?',
                     'Sí. Registrar una alimentación, un biberón o un pañal nunca necesita conexión a internet.'),
                    ('¿Me dice si mi bebé está comiendo suficiente?',
                     'No. Elia no establece objetivos, alertas ni juicios, y no define qué es normal. Simplemente '
                     'recuerda lo que registras. Para cualquier duda sobre la salud de tu bebé, habla con tu pediatra '
                     'o profesional de salud.'),
                    ('¿Puedo editar o borrar una entrada?',
                     'Sí. Puedes editar o borrar cualquier entrada. Nada queda permanente por accidente.'),
                    ('¿Pueden dos cuidadores compartir el mismo registro?',
                     'No en la versión actual. Elia Feeding es local por diseño, así que no hay sincronización en la '
                     'nube entre dispositivos. Todo vive en el dispositivo en el que registras.'),
                    ('¿Cómo llevo mi registro a otro lugar?',
                     'Puedes exportarlo o compartirlo como texto plano usando las opciones de compartir de tu '
                     'dispositivo. Tú eliges el destino; Elia nunca envía nada por su cuenta.'),
                    ('¿Hay anuncios o suscripciones?',
                     'No hay anuncios, suscripciones ni pagos. Elia Feeding es una ayuda tranquila para la memoria, no '
                     'un embudo de monetización.')]}}


MOMENTS = {
 'en': {'card': ['Elia Moments',
                 'A private home for the little firsts. Capture a memory in seconds today, and enjoy it with your '
                 'family years later.'],
        'app': {'title': 'Elia Moments — a private home for the little firsts',
                'desc': 'Elia Moments is a calm, private family archive for the small firsts and meaningful memories '
                        'of childhood. No account. No cloud. Local-first.',
                'tag': 'Remember the little firsts.',
                'sub': 'A calm, private family archive for the small firsts and meaningful memories that otherwise '
                       'scatter across notes, chats, and photo libraries.',
                'pull': ['Capture it in seconds today. Enjoy it with your family years later.',
                         'The result is a child’s story, not a dashboard.'],
                'head': ['What it does', 'One durable home for the memories that matter.'],
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
                'principles': ['Calm, private, and yours.',
                               ['No account', 'No ads', 'No analytics', 'Local-first', 'Works offline',
                                'Portable backups'],
                               'Elia Moments never infers delays, diagnoses, or developmental judgement from what you '
                               'save. Categories and prompts are ways to remember, never obligations.']},
        'support': [('Is my data private?',
                     'Yes. Elia Moments has no account and no hidden upload. Your moments, photos, and settings stay '
                     'in the app’s private storage on your device. See the privacy policy for details.'),
                    ('Does it work offline?',
                     'Yes. Capturing, browsing, search, backup, and restore all work without a network. Optional '
                     'place suggestions are the only online extra, and they have a manual fallback.'),
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
                     'Uninstalling the app or clearing its storage removes the local data, and automatic cloud backup '
                     'is deliberately disabled. Create a backup before uninstalling, resetting, or switching devices.'),
                    ('Are there ads or subscriptions?',
                     'No ads, and no subscription gate for the core archive.')]},
 'de': {'card': ['Elia Moments',
                 'Ein privates Zuhause für die kleinen ersten Male. Heute in Sekunden festhalten, Jahre später '
                 'gemeinsam genießen.'],
        'app': {'title': 'Elia Moments — ein privates Zuhause für die kleinen ersten Male',
                'desc': 'Elia Moments ist ein ruhiges, privates Familienarchiv für die kleinen ersten Male und '
                        'bedeutsamen Erinnerungen der Kindheit. Kein Konto. Keine Cloud. Local-first.',
                'tag': 'Die kleinen ersten Male festhalten.',
                'sub': 'Ein ruhiges, privates Familienarchiv für die kleinen ersten Male und bedeutsamen '
                       'Erinnerungen, die sonst zwischen Notizen, Chats und Fotomediatheken verloren gehen.',
                'pull': ['Heute in Sekunden festhalten. Jahre später gemeinsam genießen.',
                         'Das Ergebnis ist die Geschichte eines Kindes, kein Dashboard.'],
                'head': ['Was sie kann', 'Ein dauerhaftes Zuhause für die Erinnerungen, die zählen.'],
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
                'principles': ['Ruhig, privat und deins.',
                               ['Kein Konto', 'Keine Werbung', 'Keine Analyse', 'Local-first', 'Funktioniert offline',
                                'Portable Backups'],
                               'Elia Moments leitet aus deinen Einträgen niemals Verzögerungen, Diagnosen oder '
                               'Entwicklungsurteile ab. Kategorien und Vorschläge sind Wege zu erinnern, niemals '
                               'Pflichten.']},
        'support': [('Sind meine Daten privat?',
                     'Ja. Elia Moments hat kein Konto und lädt nichts heimlich hoch. Deine Momente, Fotos und '
                     'Einstellungen bleiben im privaten Speicher der App auf deinem Gerät. Details stehen in der '
                     'Datenschutzerklärung.'),
                    ('Funktioniert die App offline?',
                     'Ja. Erfassen, Durchsuchen, Suche, Backup und Wiederherstellung funktionieren ohne Netz. '
                     'Optionale Ortsvorschläge sind die einzige Online-Ergänzung und haben eine manuelle Alternative.'),
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
                     'Deinstallieren oder das Löschen des App-Speichers entfernt die lokalen Daten, und automatische '
                     'Cloud-Backups sind bewusst deaktiviert. Erstelle ein Backup, bevor du deinstallierst, '
                     'zurücksetzt oder das Gerät wechselst.'),
                    ('Gibt es Werbung oder Abos?',
                     'Keine Werbung und keine Abo-Schranke für das Kernarchiv.')]},
 'es': {'card': ['Elia Moments',
                 'Un hogar privado para las pequeñas primeras veces. Guárdalo en segundos hoy y disfrútalo en familia '
                 'años después.'],
        'app': {'title': 'Elia Moments — un hogar privado para las pequeñas primeras veces',
                'desc': 'Elia Moments es un archivo familiar tranquilo y privado para las pequeñas primeras veces y '
                        'los recuerdos importantes de la infancia. Sin cuenta. Sin nube. Local-first.',
                'tag': 'Recuerda las pequeñas primeras veces.',
                'sub': 'Un archivo familiar tranquilo y privado para las pequeñas primeras veces y los recuerdos '
                       'que, si no, se dispersan entre notas, chats y fototecas.',
                'pull': ['Guárdalo en segundos hoy. Disfrútalo en familia años después.',
                         'El resultado es la historia de un niño, no un panel de métricas.'],
                'head': ['Qué hace', 'Un hogar duradero para los recuerdos que importan.'],
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
                'principles': ['Tranquila, privada y tuya.',
                               ['Sin cuenta', 'Sin anuncios', 'Sin analíticas', 'Local-first', 'Funciona sin conexión',
                                'Copias portables'],
                               'Elia Moments nunca deduce retrasos, diagnósticos ni juicios sobre el desarrollo a '
                               'partir de lo que guardas. Las categorías y las sugerencias son formas de recordar, '
                               'nunca obligaciones.']},
        'support': [('¿Mis datos son privados?',
                     'Sí. Elia Moments no tiene cuenta ni sube nada de forma oculta. Tus momentos, fotos y ajustes se '
                     'quedan en el almacenamiento privado de la app en tu dispositivo. Consulta la política de '
                     'privacidad para más detalles.'),
                    ('¿Funciona sin conexión?',
                     'Sí. Guardar, explorar, buscar, crear copias y restaurar funcionan sin red. Las sugerencias de '
                     'lugar son el único extra en línea y tienen alternativa manual.'),
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
                     'Desinstalar la app o borrar su almacenamiento elimina los datos locales, y la copia automática '
                     'en la nube está desactivada a propósito. Crea una copia antes de desinstalar, restablecer o '
                     'cambiar de dispositivo.'),
                    ('¿Hay anuncios o suscripciones?',
                     'No hay anuncios ni muro de suscripción para el archivo principal.')]}}

for _lang, _data in MOMENTS.items():
    T[_lang]['home']['moments_card'] = _data['card']
    APP[_lang]['moments'] = _data['app']
    SUPPORT[_lang]['moments'] = _data['support']






def ul(items, cls):
    return f'<ul class="{cls}">' + "".join(f"<li>{escape(x)}</li>" for x in items) + "</ul>"


def chips(items):
    return '<div class="chips">' + "".join(f'<span class="chip">{escape(x)}</span>' for x in items) + "</div>"


def app_cards(lang):
    t = T[lang]["home"]
    cards = []
    for app in APPS:
        card = t[CARD_KEYS[app]]
        cards.append(f"""          <a class="app-card" href="{href(lang, f"apps/{app}")}" data-accent="{CARD_ACCENTS[app]}">
            <div class="app-card__top"><span class="app-icon is-image" aria-hidden="true"><img src="{asset(f"assets/img/icon-{app}.png", lang, "")}" alt="" width="256" height="256" loading="lazy" /></span><div><div class="app-card__title">{escape(card[0])}</div><span class="tag"><span class="tag__dot"></span>{escape(t["coming"])}</span></div></div>
            <p class="app-card__one">{escape(card[1])}</p><div class="app-card__foot"><span class="app-card__cta">{escape(t["learn"])} <span class="arrow">→</span></span></div>
          </a>""")
    return "\n".join(cards)


def home(lang):
    t = T[lang]["home"]
    body = f"""<!DOCTYPE html>
<html lang="{lang}">
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
<html lang="{lang}">
{head(lang, route, a["title"], a["desc"], icon, image, extra)}
<body>
  {header(lang, route, [(c["overview"], "#what"), (c["support"], f"{route}/support"), (c["privacy"], f"{route}/privacy"), (c["all"], "")], T[lang]["lang"])}
  <main>
    <section class="hero app-hero"><div class="container"><a class="backlink" href="{href(lang, "", lang, route)}">{escape(c["back"])}</a>{icon_html}<h1>Elia {app.capitalize()}</h1><p class="hero__tagline">{escape(a["tag"])}</p><p class="hero__sub lead">{escape(a["sub"])}</p><div class="btn-row"><span class="tag"><span class="tag__dot"></span>{escape(T[lang]["home"]["coming"])}</span></div></div></section>
{pre}
    <section id="what"><div class="container"><div class="section-head"><span class="eyebrow">{escape(a["head"][0])}</span><h2>{escape(a["head"][1])}</h2></div><div class="grid-2"><div class="panel"><h3>{escape(a["left"])}</h3>{ul(a["yes"], "checklist")}</div><div class="panel"><h3>{escape(a["right"])}</h3>{ul(a["no"], "notlist")}</div></div></div></section>
{story_section(a) if app == "contractions" else ""}
    <section id="principles"><div class="container"><div class="section-head"><span class="eyebrow">{escape(c["promise"])}</span><h2>{escape(a["principles"][0])}</h2>{sublead}</div>{chips(a["principles"][2 if has_sublead else 1])}<div class="callout" style="margin-top:32px;">{escape(a["principles"][3 if has_sublead else 2])}</div></div></section>
  </main>
  {footer(lang, [(c["support"], f"{route}/support"), (c["privacy"], f"{route}/privacy"), *others, (c["all"], "")], T[lang]["note"], route)}
</body>
</html>
"""
    write(lang, route, body)


def story_section(a):
    s = a["story"]
    return f"""<section id="story" class="tint"><div class="container"><div class="section-head"><span class="eyebrow">{escape(s[0])}</span><h2>{escape(s[1])}</h2></div><div class="story"><p>{escape(s[2])}</p><p>{escape(s[3])}</p><p class="pull">{escape(s[4])}</p><p>{escape(s[5])}</p></div></div></section>"""


def support_page(lang, app):
    c = APP[lang]["common"]
    route = f"apps/{app}/support"
    app_name = f"Elia {app.capitalize()}"
    title = f"{c['support']} — {app_name}"
    desc = {
        "en": f"Help and answers for {app_name} — a calm, private app. Common questions and how to reach us.",
        "de": f"Hilfe und Antworten für {app_name} — eine ruhige, private App. Häufige Fragen und Kontakt.",
        "es": f"Ayuda y respuestas para {app_name}, una app tranquila y privada. Preguntas frecuentes y contacto.",
    }[lang]
    extra = app_style(app)
    faq = "".join(f'<details{" open" if i == 0 else ""}><summary>{escape(q)}</summary><p>{escape(a).replace("privacy policy", f"<a href=\"{href(lang, f"apps/{app}/privacy", lang, route)}\">privacy policy</a>").replace("Datenschutzerklärung", f"<a href=\"{href(lang, f"apps/{app}/privacy", lang, route)}\">Datenschutzerklärung</a>").replace("política de privacidad", f"<a href=\"{href(lang, f"apps/{app}/privacy", lang, route)}\">política de privacidad</a>")}</p></details>' for i, (q, a) in enumerate(SUPPORT[lang][app]))
    body = f"""<!DOCTYPE html>
<html lang="{lang}">
{head(lang, route, title, desc, "svg", None, extra)}
<body>
  {header(lang, route, [(app.capitalize(), f"apps/{app}"), (c["privacy"], f"apps/{app}/privacy"), (c["promise"], "home#philosophy")], T[lang]["lang"])}
  <main><section class="hero doc-hero"><div class="container"><a class="backlink" href="{href(lang, f"apps/{app}", lang, route)}">← {app_name}</a><h1>{escape(c["support"])}</h1><p class="updated">{escape({"en": "We keep things simple. Here are the common questions.", "de": "Wir halten es einfach. Hier sind die häufigsten Fragen.", "es": "Lo mantenemos simple. Estas son las preguntas más frecuentes."}[lang])}</p></div></section><section><div class="container"><div class="faq">{faq}</div><div class="prose" style="margin-top:40px;"><h2>{escape(c["still"])}</h2><p>{escape({"en": "Write to us at", "de": "Schreib uns an", "es": "Escríbenos a"}[lang])} <a href="mailto:{app}@getelia.app?subject=Elia%20{app.capitalize()}%20support">{app}@getelia.app</a>. {escape(c["read"])}</p></div></div></section></main>
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
    desc = {
        "en": f"Privacy policy for {app_name}. No account, no backend, no tracking — your data stays on your device.",
        "de": f"Datenschutzerklärung für {app_name}. Kein Konto, kein Backend, kein Tracking — deine Daten bleiben auf deinem Gerät.",
        "es": f"Política de privacidad de {app_name}. Sin cuenta, sin backend, sin seguimiento: tus datos se quedan en tu dispositivo.",
    }[lang]
    extra = app_style(app)
    text = privacy_text(lang, app)
    sections = "".join(f"<h2>{escape(h)}</h2><p>{escape(p)}</p>" if isinstance(p, str) else f"<h2>{escape(h)}</h2>{ul(p, '')}" for h, p in text["sections"])
    body = f"""<!DOCTYPE html>
<html lang="{lang}">
{head(lang, route, title, desc, "svg", None, extra)}
<body>
  {header(lang, route, [(app.capitalize(), f"apps/{app}"), (c["support"], f"apps/{app}/support"), (c["promise"], "home#philosophy")], T[lang]["lang"])}
  <main><section class="hero doc-hero"><div class="container"><a class="backlink" href="{href(lang, f"apps/{app}", lang, route)}">← {app_name}</a><h1>{escape(c["privacy"])}</h1><p class="updated">{app_name} · {escape(text["updated"])}</p></div></section><section><div class="container prose"><p>{escape(text["intro"])}</p>{sections}<h2>{escape(text["contact"])}</h2><p>{escape(text["question"])} <a href="mailto:{app}@getelia.app">{app}@getelia.app</a>.</p><div class="callout">{escape(text["callout"])}</div></div></section></main>
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
    @media (prefers-color-scheme: dark) {{ body {{ --accent-light: {light_dark}; }} }}
  </style>
"""


def privacy_text(lang, app):
    if lang == "en":
        intro = "Elia is built to be private by design. It has no account, no backend, and no tracking. This policy explains, in plain language, what that means."
        return {"updated": "Last updated 13 July 2026", "intro": intro, "contact": "Contact", "question": "Questions about privacy? Reach us at", "callout": APP[lang][app]["principles"][-1], "sections": [
            ("The short version", ["No account and no sign-in.", "No data is collected by Elia.", "Your data is never sold or shared.", "Everything is stored locally on your device.", "Nothing is uploaded to any Elia server."]),
            ("What the app stores", "Stored locally on your device only: your entries, history derived from them, and settings."),
            ("Data leaving your device", "Data leaves your device only when you choose to export or share it, using your device's own share options. You pick the destination. Elia does not upload your log to any service of its own."),
            ("Backups", "Automatic cloud backup and device-to-device transfer of app data are disabled. Your log moves only through an export you start yourself."),
            ("Network and permissions", "Core use does not require registration or a connection. The app avoids unnecessary permissions and contains no advertising, analytics, or third-party tracking SDKs."),
            ("Deleting your data", "Deleting the app's data, or uninstalling the app, removes the local data from your device. Because nothing is stored elsewhere, that is all it takes."),
            ("Children", "Elia is intended as a tool for adults and caregivers. It does not knowingly collect data from anyone."),
        ]}
    data = {
      "de": ("Zuletzt aktualisiert am 13. Juli 2026", "Elia ist von Anfang an privat gedacht. Es gibt kein Konto, kein Backend und kein Tracking. Diese Richtlinie erklärt in einfacher Sprache, was das bedeutet.", "Kontakt", "Fragen zum Datenschutz? Schreib uns an", [
        ("Kurzfassung", ["Kein Konto und keine Anmeldung.", "Elia sammelt keine Daten.", "Deine Daten werden nie verkauft oder geteilt.", "Alles wird lokal auf deinem Gerät gespeichert.", "Nichts wird auf Elia-Server hochgeladen."]),
        ("Was die App speichert", "Nur lokal auf deinem Gerät: deine Einträge, daraus abgeleitete Historie und Einstellungen."),
        ("Wenn Daten dein Gerät verlassen", "Daten verlassen dein Gerät nur, wenn du sie selbst über die Teilen-Funktionen deines Geräts exportierst oder teilst. Du wählst das Ziel."),
        ("Backups", "Automatische Cloud-Backups und Geräteübertragung von App-Daten sind deaktiviert. Dein Protokoll bewegt sich nur durch einen Export, den du selbst startest."),
        ("Netzwerk und Berechtigungen", "Die Kernnutzung braucht keine Registrierung und keine Verbindung. Die App vermeidet unnötige Berechtigungen und enthält keine Werbung, Analyse oder Tracking-SDKs."),
        ("Daten löschen", "Wenn du App-Daten löschst oder die App deinstallierst, werden die lokalen Daten vom Gerät entfernt. Da nichts anderswo gespeichert wird, reicht das aus."),
        ("Kinder", "Elia ist als Werkzeug für Erwachsene und Betreuungspersonen gedacht. Sie sammelt wissentlich keine Daten von irgendwem."),
      ]),
      "es": ("Última actualización: 13 de julio de 2026", "Elia está diseñada para ser privada desde el principio. No tiene cuenta, backend ni seguimiento. Esta política explica en lenguaje sencillo qué significa eso.", "Contacto", "¿Preguntas sobre privacidad? Escríbenos a", [
        ("La versión corta", ["Sin cuenta ni inicio de sesión.", "Elia no recoge datos.", "Tus datos nunca se venden ni se comparten.", "Todo se guarda localmente en tu dispositivo.", "Nada se sube a servidores de Elia."]),
        ("Qué guarda la app", "Solo localmente en tu dispositivo: tus entradas, el historial derivado de ellas y tus ajustes."),
        ("Cuando los datos salen de tu dispositivo", "Los datos salen de tu dispositivo solo cuando decides exportarlos o compartirlos usando las opciones de compartir del propio dispositivo. Tú eliges el destino."),
        ("Copias de seguridad", "Las copias de seguridad automáticas en la nube y la transferencia de datos entre dispositivos están desactivadas. Tu registro se mueve solo mediante una exportación que tú inicias."),
        ("Red y permisos", "El uso principal no requiere registro ni conexión. La app evita permisos innecesarios y no contiene publicidad, analíticas ni SDKs de seguimiento de terceros."),
        ("Borrar tus datos", "Borrar los datos de la app o desinstalarla elimina los datos locales del dispositivo. Como no se guardan en ningún otro lugar, eso es suficiente."),
        ("Menores", "Elia está pensada como herramienta para adultos y cuidadores. No recoge datos de nadie de forma consciente."),
      ]),
    }
    updated, intro, contact, question, sections = data[lang]
    return {"updated": updated, "intro": intro, "contact": contact, "question": question, "sections": sections, "callout": APP[lang][app]["principles"][-1]}

def not_found(lang):
    route = ""
    title = {"en": "Page not found — Elia", "de": "Seite nicht gefunden — Elia", "es": "Página no encontrada — Elia"}[lang]
    text = {"en": "Take a breath. This page doesn't exist — but the rest of Elia does.", "de": "Atme kurz durch. Diese Seite gibt es nicht — der Rest von Elia schon.", "es": "Respira. Esta página no existe, pero el resto de Elia sí."}[lang]
    btn = {"en": "Back to Elia", "de": "Zurück zu Elia", "es": "Volver a Elia"}[lang]
    body = f"""<!DOCTYPE html>
<html lang="{lang}">
{head(lang, "", title, text, extra='  <meta name="robots" content="noindex" />\n')}
<body><main><section class="hero"><div class="container"><img class="brand__mark" src="{asset("assets/img/favicon.svg", lang, route)}" alt="" style="width:40px;height:40px;border-radius:12px;margin:0 auto 24px;" /><h1 class="hero__wordmark" style="font-size:clamp(40px,9vw,72px);">{escape(title.split(" — ")[0])}</h1><p class="hero__sub lead">{escape(text)}</p><div class="btn-row"><a class="btn btn--primary" href="{href(lang, "", lang, route)}">{escape(btn)}</a></div></div></section></main></body></html>"""
    if lang == "en":
        (ROOT / "404.html").write_text(body, encoding="utf-8")

def sitemap():
    routes = [""] + [f"apps/{a}" for a in APPS] + [f"apps/{a}/{sub}" for a in APPS for sub in ("privacy", "support")]
    urls = []
    for route in routes:
        for lang in LANGS:
            urls.append(f"""  <url>
    <loc>{url(lang, route)}</loc>
    <lastmod>2026-07-19</lastmod>
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
    not_found(lang)
sitemap()
