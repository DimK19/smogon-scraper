## Decides which published stats files belong to each format, and which line of the chart they count towards.
## The database stores every candidate file, so these rules can change without downloading anything again.

import re

GUI_FORMATS = ("vgc", "ou", "uu", "ubers")
TITLES = {"vgc" : "VGC", "ou" : "OU", "uu" : "UU", "ubers" : "Ubers", "bdspdoubles" : "BDSP Doubles"}

SINGLE_GAMES = "Single games"
BEST_OF_THREE = "Best of three"
MAIN_LADDER = "Main ladder"

## Files worth downloading for each format. "source" is a file name without its "-0.txt" ending.
_CANDIDATES = {
    "vgc" : re.compile(r"^.*vgc[0-9]{4}.*$|^.*battle(spot|stadium)doubles.*$"),
    "ou" : re.compile(r"^(gen[0-9]*)*(?:(poke|pre)bank)?ou.*$"), ## poke|prebank is only necessary for a few months in 2017
    "uu" : re.compile(r"^(gen[0-9]*)*(?:(poke|pre)bank)?uu.*$"),
    "ubers" : re.compile(r"^(gen[0-9]*)*(?:(poke|pre)bank)?ubers.*$"),
    "bdspdoubles" : re.compile(r"^gen8bdspbattlefestivaldoubles$"), ## not in the gui yet
}

## The main ladder of a tier: an optional generation, an optional Pokemon Bank marker, and the exact tier name.
## alpha and beta count because new generations launch their main ladder under those names (e.g. gen7uubeta in 2017-01).
## Suspect tests, Blitz, rule variants and neighbouring tiers (UUBL, Ubers UU) are stored but not plotted.
_MAIN_LADDER = {
    tier : re.compile(rf"^(?:gen[0-9]+)?(?:(?:poke|pre)bank)?{tier}(?:prebank|alpha|beta)?$")
    for tier in ("ou", "uu", "ubers")
}

def isCandidate(formatName, source):
    return bool(_CANDIDATES[formatName].match(source))

def isKnownFormat(formatName):
    return formatName in _CANDIDATES

def formatTitle(formatName):
    return TITLES.get(formatName, formatName)

## Returns the chart line a file counts towards, or None if it is stored but not plotted
def seriesFor(formatName, source):
    if(formatName == "vgc"):
        return BEST_OF_THREE if source.endswith("bo3") else SINGLE_GAMES
    if(formatName in _MAIN_LADDER):
        return MAIN_LADDER if _MAIN_LADDER[formatName].match(source) else None
    return SINGLE_GAMES

## rows are (month, source, battles). Returns {seriesName : {month : battles}}
def groupSeries(formatName, rows):
    series = {}
    for month, source, battles in rows:
        name = seriesFor(formatName, source)
        if(name is None):
            continue
        byMonth = series.setdefault(name, {})
        byMonth[month] = byMonth.get(month, 0) + battles
    ## keeps colours stable: single games always comes first
    order = [SINGLE_GAMES, MAIN_LADDER, BEST_OF_THREE]
    return {name : series[name] for name in order if name in series}
