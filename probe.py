"""Probe enrichment endpoints (watch/providers, external_ids) for this week's list."""
import urllib.request, urllib.parse, json, datetime

def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    return env

env = load_env("/Users/jackv/Code/NewMovies/.env")
TOKEN = env["TMDB_TOKEN"]
BASE = "https://api.themoviedb.org/3"
H = {"Authorization": "Bearer " + TOKEN}

def get(path, **params):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req) as r:
        return json.load(r)

GTE, LTE = "2026-06-14", "2026-06-21"
WIN_START, WIN_END = datetime.date(2026, 6, 14), datetime.date(2026, 6, 21)

disc = get("/discover/movie", region="US", with_release_type="4|5",
           **{"release_date.gte": GTE, "release_date.lte": LTE},
           sort_by="popularity.desc", page=1)

def in_window(m):
    rd = m.get("release_date")
    try:
        return rd and WIN_START <= datetime.date.fromisoformat(rd) <= WIN_END
    except ValueError:
        return False

films = sorted([m for m in disc["results"] if in_window(m) and m.get("popularity", 0) >= 10],
               key=lambda m: m.get("popularity", 0), reverse=True)

def names(lst):
    return ", ".join(p["provider_name"] for p in lst) if lst else "-"

for m in films:
    wp = get("/movie/%d/watch/providers" % m["id"]).get("results", {}).get("US", {})
    ext = get("/movie/%d/external_ids" % m["id"])
    print("### %s  (pop=%.0f, %s)" % (m["title"], m.get("popularity", 0), m.get("release_date")))
    print("   imdb:    https://www.imdb.com/title/%s/" % ext.get("imdb_id"))
    print("   stream:  %s" % names(wp.get("flatrate")))
    print("   rent:    %s" % names(wp.get("rent")))
    print("   buy:     %s" % names(wp.get("buy")))
    print("   poster:  https://image.tmdb.org/t/p/w500%s" % m.get("poster_path"))
    print("   genres:  (ids) %s   runtime/cert: need /movie/{id} detail call" % m.get("genre_ids"))
    print()
