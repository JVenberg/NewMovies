"""One-off: dump the last 3 months of US home releases, sorted by popularity,
so the popularity metric (and the MIN_POPULARITY cutoff) can be eyeballed.
Run: uv run python audit.py
"""
import datetime

from newmovies import config, filtering, langs, tmdb

TODAY = datetime.date(2026, 6, 21)
START = TODAY.replace(month=TODAY.month - 3)
POP_FLOOR = 2.0          # stop paginating once popularity drops below this
HARD_PAGE_CAP = 100
OUT = "audit-popularity-3mo.md"


def genre_map():
    data = tmdb._get("/genre/movie/list", language="en-US")
    return {g["id"]: g["name"] for g in data.get("genres", [])}


def fetch():
    results, page = [], 1
    while True:
        data = tmdb._get(
            "/discover/movie",
            region=config.REGION,
            with_release_type="4|5",
            sort_by="popularity.desc",
            page=page,
            **{"release_date.gte": START.isoformat(), "release_date.lte": TODAY.isoformat()},
        )
        rows = data.get("results", [])
        results.extend(rows)
        low = min((r.get("popularity", 0) for r in rows), default=0)
        if page >= data.get("total_pages", 1) or page >= HARD_PAGE_CAP or low < POP_FLOOR:
            return results
        page += 1


def esc(text):
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def row(rank, m, genres):
    g = ", ".join(genres.get(i, "") for i in m.get("genre_ids", []) if i in genres)
    return "| %d | %s | %s | %.1f | %s | %d | %s | %s |" % (
        rank,
        esc(m.get("title")),
        m.get("release_date") or "?",
        m.get("popularity", 0),
        ("%.1f" % m["vote_average"]) if m.get("vote_average") else "-",
        m.get("vote_count", 0),
        esc(langs.name(m.get("original_language")) or "-"),
        esc(g),
    )


def table(rows, genres):
    head = ["| # | Title | Home release | Popularity | Rating | Votes | Language | Genres |",
            "|--:|---|---|--:|--:|--:|---|---|"]
    return "\n".join(head + [row(i + 1, m, genres) for i, m in enumerate(rows)])


def main():
    genres = genre_map()
    raw = fetch()
    movies = filtering.select(raw, START, TODAY, 0, set())  # in-window, sorted by popularity desc
    cut = config.MIN_POPULARITY
    above = [m for m in movies if m.get("popularity", 0) >= cut]
    below = [m for m in movies if m.get("popularity", 0) < cut]

    lines = [
        "# Popularity audit: US home releases, %s to %s" % (START, TODAY),
        "",
        "Source: TMDB `/discover/movie` (`with_release_type=4|5`, region `%s`), "
        "filtered to films whose earliest digital/physical date falls in-window, "
        "sorted by `popularity` descending." % config.REGION,
        "",
        "- Total in-window releases listed: **%d** (popularity floor while fetching: %.0f)" % (len(movies), POP_FLOOR),
        "- Current digest cutoff `MIN_POPULARITY = %.0f` -> **%d kept**, **%d dropped**"
        % (cut, len(above), len(below)),
        "- `Rating` = `vote_average` (mean user score); `Votes` = `vote_count`. "
        "New titles accumulate votes slowly, so rating is noisy early.",
        "",
        "## Above cutoff (popularity >= %.0f) - these would be emailed" % cut,
        "",
        table(above, genres),
        "",
        "## Below cutoff (popularity < %.0f) - these are filtered out" % cut,
        "",
        table(below, genres),
        "",
    ]
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print("Wrote %s (%d above cutoff, %d below)" % (OUT, len(above), len(below)))


if __name__ == "__main__":
    main()
