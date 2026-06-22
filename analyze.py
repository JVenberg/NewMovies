"""Scratch: examine non-English in-window films, popularity vs vote_count,
to judge whether vote_count separates US-relevant foreign films from regional ones.
Run: uv run python analyze.py
"""
from newmovies import filtering, langs
import audit

raw = audit.fetch()
movies = filtering.select(raw, audit.START, audit.TODAY, 0, set())
non_en = [m for m in movies if (m.get("original_language") or "") != "en"]
non_en.sort(key=lambda m: m.get("vote_count", 0), reverse=True)

print("Non-English in-window films: %d of %d total\n" % (len(non_en), len(movies)))
print("%-32s %-10s %7s %6s %6s %6s" % ("title", "lang", "pop", "votes", "rate", "p/v"))
print("-" * 72)
for m in non_en:
    pop = m.get("popularity", 0)
    vc = m.get("vote_count", 0)
    va = m.get("vote_average", 0)
    ratio = (pop / vc) if vc else 999
    print("%-32.32s %-10s %7.1f %6d %6.1f %6.1f" % (
        m.get("title"), langs.name(m.get("original_language")), pop, vc, va, ratio))

for floor in (25, 50, 100):
    keep = [m for m in non_en if m.get("vote_count", 0) >= floor]
    print("\nvote_count >= %d : keeps %d of %d non-English  -> %s"
          % (floor, len(keep), len(non_en), ", ".join(m["title"] for m in keep)))
