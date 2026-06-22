"""Backtest the two non-English relevance heuristics over the last 6 months:
  (1) vote-count floor   : keep if vote_count >= FLOOR
  (2) pop/votes ratio cap: keep if vote_count>0 and popularity/vote_count <= RATIO
Both act only on non-English films that already pass MIN_POPULARITY (the digest's
first gate), so that's the universe we compare. Writes a markdown report.
Run: uv run python backtest.py
"""
import datetime

from newmovies import config, filtering, langs, tmdb

TODAY = datetime.date(2026, 6, 21)
_m, _y = TODAY.month - 6, TODAY.year
if _m <= 0:
    _m += 12
    _y -= 1
START = datetime.date(_y, _m, TODAY.day)

FLOOR = 50      # heuristic 1
RATIO = 3.0     # heuristic 2
OUT = "backtest-foreign-6mo.md"


def fetch():
    results, page = [], 1
    while True:
        data = tmdb._get(
            "/discover/movie", region=config.REGION, with_release_type="4|5",
            sort_by="popularity.desc", page=page,
            **{"release_date.gte": START.isoformat(), "release_date.lte": TODAY.isoformat()})
        rows = data.get("results", [])
        results.extend(rows)
        low = min((r.get("popularity", 0) for r in rows), default=0)
        if page >= data.get("total_pages", 1) or page >= 100 or low < config.MIN_POPULARITY:
            return results
        page += 1


def trim(text, n=260):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def metrics(m):
    pop = m.get("popularity", 0) or 0
    votes = m.get("vote_count", 0) or 0
    ratio = (pop / votes) if votes else float("inf")
    return pop, votes, ratio


def floor_keep(m):
    return (m.get("vote_count", 0) or 0) >= FLOOR


def ratio_keep(m):
    _, votes, ratio = metrics(m)
    return votes > 0 and ratio <= RATIO


def block(m):
    pop, votes, ratio = metrics(m)
    rstr = "inf" if ratio == float("inf") else "%.1f" % ratio
    return ("- **%s** (%s) - pop %.1f, votes %d, ratio %s, rating %.1f  \n  %s"
            % (m.get("title"), langs.name(m.get("original_language")) or "?",
               pop, votes, rstr, m.get("vote_average", 0), trim(m.get("overview"))))


def main():
    raw = fetch()
    movies = filtering.select(raw, START, TODAY, config.MIN_POPULARITY, set())  # pop>=10, in-window
    non_en = [m for m in movies if (m.get("original_language") or "") != "en"]
    non_en.sort(key=lambda m: metrics(m)[2], reverse=True)  # worst ratio first

    both_keep, both_drop, floor_only, ratio_only = [], [], [], []
    for m in non_en:
        f, r = floor_keep(m), ratio_keep(m)
        if f and r:
            both_keep.append(m)
        elif not f and not r:
            both_drop.append(m)
        elif f and not r:
            floor_only.append(m)   # floor keeps, ratio drops
        else:
            ratio_only.append(m)   # ratio keeps, floor drops

    rows = []
    for m in non_en:
        pop, votes, ratio = metrics(m)
        rstr = "inf" if ratio == float("inf") else "%.1f" % ratio
        f, r = floor_keep(m), ratio_keep(m)
        flag = "" if f == r else " **DIFF**"
        rows.append("| %s | %s | %.1f | %d | %s | %.1f | %s | %s |%s" % (
            (m.get("title") or "").replace("|", "\\|"),
            langs.name(m.get("original_language")) or "?",
            pop, votes, rstr, m.get("vote_average", 0),
            "keep" if f else "drop", "keep" if r else "drop", flag))

    lines = [
        "# Backtest: non-English relevance heuristics, %s to %s" % (START, TODAY),
        "",
        "Universe: non-English films with an in-window US digital/physical release that "
        "**already pass `MIN_POPULARITY=%g`** (the digest's first gate). Both heuristics only "
        "act on this set." % config.MIN_POPULARITY,
        "",
        "- **Heuristic 1 - vote-count floor:** keep if `vote_count >= %d`" % FLOOR,
        "- **Heuristic 2 - pop/votes ratio cap:** keep if `vote_count > 0` and "
        "`popularity/vote_count <= %g`  (this is the one currently wired in)" % RATIO,
        "",
        "Non-English films in scope: **%d**. Floor keeps **%d**, ratio keeps **%d**. "
        "They disagree on **%d**." % (len(non_en), len(both_keep) + len(floor_only),
                                      len(both_keep) + len(ratio_only),
                                      len(floor_only) + len(ratio_only)),
        "",
        "| Title | Lang | Pop | Votes | Ratio | Rating | Floor>=%d | Ratio<=%g |" % (FLOOR, RATIO),
        "|---|---|--:|--:|--:|--:|:--:|:--:|",
        *rows,
        "",
        "## Where they disagree (the cases that matter)",
        "",
        "### Floor KEEPS, ratio DROPS  (%d)" % len(floor_only),
        "_Films with few votes but a *low* pop/votes ratio (not regionally spiked). "
        "Ratio lets these through; the floor cuts them._",
        "",
        *([block(m) for m in floor_only] or ["_none_"]),
        "",
        "### Ratio KEEPS, floor DROPS  (%d)" % len(ratio_only),
        "_Films the floor would cut for low votes, but ratio keeps because popularity is "
        "proportionate (watched, just niche)._",
        "",
        *([block(m) for m in ratio_only] or ["_none_"]),
        "",
        "## Both DROP  (%d) - the regional spikes we want gone" % len(both_drop),
        "",
        *([block(m) for m in both_drop] or ["_none_"]),
        "",
        "## Both KEEP  (%d) - the foreign films we want to surface" % len(both_keep),
        "",
        *([block(m) for m in both_keep] or ["_none_"]),
        "",
    ]
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print("Wrote %s" % OUT)
    print("scope=%d  floor_keep=%d  ratio_keep=%d  disagree=%d (floor_only=%d, ratio_only=%d)"
          % (len(non_en), len(both_keep) + len(floor_only), len(both_keep) + len(ratio_only),
             len(floor_only) + len(ratio_only), len(floor_only), len(ratio_only)))


if __name__ == "__main__":
    main()
