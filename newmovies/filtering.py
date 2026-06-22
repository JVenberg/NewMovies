import datetime


def _earliest_home_release(movie):
    # discover() with region+release_type returns the earliest matching (digital/physical)
    # US date in `release_date`; if that falls in-window the film became torrentable this week.
    raw = movie.get("release_date")
    if not raw:
        return None
    try:
        return datetime.date.fromisoformat(raw)
    except ValueError:
        return None


def _underwatched_foreign(movie, min_votes):
    # Non-English films are kept only if enough of TMDB's (US/English-skewed) audience
    # has actually rated them. A low vote count reads as "not culturally present here"
    # even when regional traffic makes the film popular. English films are never filtered.
    if (movie.get("original_language") or "") == "en":
        return False
    return (movie.get("vote_count", 0) or 0) < min_votes


def select(movies, win_start, win_end, min_popularity, already_sent, min_foreign_votes=None):
    picked = []
    seen = set()
    for movie in movies:
        mid = str(movie.get("id"))
        if mid in already_sent or mid in seen:
            continue
        if movie.get("popularity", 0) < min_popularity:
            continue
        if min_foreign_votes and _underwatched_foreign(movie, min_foreign_votes):
            continue
        home = _earliest_home_release(movie)
        if home is None or not (win_start <= home <= win_end):
            continue
        seen.add(mid)
        picked.append(movie)
    picked.sort(key=lambda m: m.get("popularity", 0), reverse=True)
    return picked
