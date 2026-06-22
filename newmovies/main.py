import datetime
import sys

from . import config, filtering, langs, render, sender, state, tmdb


def _build_record(movie, det):
    providers = det.get("watch/providers", {}).get("results", {}).get(config.REGION, {})

    def names(key):
        return [p["provider_name"] for p in providers.get(key, [])]

    credits = det.get("credits", {})
    directors = [c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"]
    cast = [c["name"] for c in
            sorted(credits.get("cast", []), key=lambda c: c.get("order", 999))[:3]]

    return {
        "id": movie["id"],
        "title": det.get("title") or movie.get("title"),
        "home_date": movie.get("release_date"),
        "popularity": movie.get("popularity", 0),
        "overview": det.get("overview") or movie.get("overview"),
        "vote_average": det.get("vote_average"),
        "runtime": det.get("runtime"),
        "language": langs.name(det.get("original_language") or movie.get("original_language")),
        "genres": [g["name"] for g in det.get("genres", [])],
        "directors": directors,
        "cast": cast,
        "poster_path": det.get("poster_path") or movie.get("poster_path"),
        "imdb_id": (det.get("external_ids") or {}).get("imdb_id"),
        "providers": {
            "stream": names("flatrate"),
            "rent": names("rent"),
            "buy": names("buy"),
            "link": providers.get("link"),
        },
    }


def run(dry_run=False):
    today = datetime.date.fromisoformat(config.TODAY) if config.TODAY else datetime.date.today()
    win_start = today - datetime.timedelta(days=config.WINDOW_DAYS)

    sent = state.load()
    movies = tmdb.discover(config.REGION, win_start.isoformat(), today.isoformat())
    selected = filtering.select(movies, win_start, today, config.MIN_POPULARITY, set(sent),
                                config.MIN_FOREIGN_VOTES)
    records = [_build_record(m, tmdb.detail(m["id"])) for m in selected]

    if records:
        subject = ("New this week: %d movie%s now available"
                   % (len(records), "" if len(records) == 1 else "s"))
        html_body = render.render_html(records, win_start, today)
    elif config.SEND_WHEN_EMPTY:
        subject = "New this week: nothing new"
        html_body = render.render_empty(win_start, today)
    else:
        print("No new releases; SEND_WHEN_EMPTY is off. Skipping.")
        return
    text_body = render.render_text(records, win_start, today)

    if dry_run:
        print(subject)
        print(text_body)
        print("\n[dry-run] %d film(s) selected; not sending, state untouched." % len(records))
        return

    sender.send(subject, html_body, text_body)
    stamp = today.isoformat()
    for r in records:
        sent[str(r["id"])] = stamp
    state.save(sent)
    print("Sent to %s - %d film(s); state updated." % (", ".join(config.EMAIL_TO), len(records)))


def main():
    run(dry_run="--dry-run" in sys.argv)
