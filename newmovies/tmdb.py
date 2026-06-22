import json
import urllib.parse
import urllib.request

from . import config

BASE = "https://api.themoviedb.org/3"


def _get(path, **params):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + config.TMDB_TOKEN})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def discover(region, gte, lte, max_pages=20):
    """All movies with a digital (4) or physical (5) US release in [gte, lte]."""
    results = []
    page = 1
    while True:
        data = _get(
            "/discover/movie",
            region=region,
            with_release_type="4|5",
            sort_by="popularity.desc",
            page=page,
            **{"release_date.gte": gte, "release_date.lte": lte},
        )
        results.extend(data.get("results", []))
        if page >= data.get("total_pages", 1) or page >= max_pages:
            return results
        page += 1


def detail(movie_id):
    return _get("/movie/%d" % movie_id,
                append_to_response="watch/providers,external_ids,credits")
