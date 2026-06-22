"""Exploration 2: all pages, 'first availability this week' filter, threshold tuning."""
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
WIN_START = datetime.date(2026, 6, 14)
WIN_END = datetime.date(2026, 6, 21)

# Pull all pages
all_results = []
page = 1
while True:
    d = get("/discover/movie", region="US", with_release_type="4|5",
            **{"release_date.gte": GTE, "release_date.lte": LTE},
            sort_by="popularity.desc", page=page)
    all_results.extend(d["results"])
    if page >= d["total_pages"]:
        break
    page += 1

print("raw discover results:", len(all_results))

def in_window(m):
    rd = m.get("release_date")
    if not rd:
        return False
    try:
        return WIN_START <= datetime.date.fromisoformat(rd) <= WIN_END
    except ValueError:
        return False

first_avail = [m for m in all_results if in_window(m)]
print("after 'earliest digital/physical in window' filter:", len(first_avail))
print()

print("vote_count threshold sweep:")
for thr in (0, 1, 5, 10, 25, 50, 100):
    n = sum(1 for m in first_avail if m.get("vote_count", 0) >= thr)
    print("  vote_count  >= %4d  ->  %2d movies" % (thr, n))
print("popularity threshold sweep:")
for thr in (0, 2, 5, 10, 20, 30, 50, 100):
    n = sum(1 for m in first_avail if m.get("popularity", 0) >= thr)
    print("  popularity  >= %4d  ->  %2d movies" % (thr, n))

print()
print("FINAL LIST (first-availability-this-week, popularity>=10, sorted by popularity):")
print("=" * 100)
kept = sorted([m for m in first_avail if m.get("popularity", 0) >= 10],
              key=lambda m: m.get("popularity", 0), reverse=True)
for m in kept:
    print("%-44s %s  pop=%6.0f votes=%-5d avg=%.1f lang=%s" % (
        m["title"][:44], m.get("release_date"), m.get("popularity", 0),
        m.get("vote_count", 0), m.get("vote_average", 0), m.get("original_language")))
