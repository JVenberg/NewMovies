import html

POSTER_BASE = "https://image.tmdb.org/t/p/w185"
POSTER_W = 100

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
INK = "#18181b"
MUTED = "#71717a"
FAINT = "#a1a1aa"
BODY = "#3f3f46"
LINK = "#2563eb"
RULE = "#ececef"


def _shell(inner):
    return (
        '<div style="background:#f4f4f5;margin:0;padding:24px 12px;">'
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center"'
        ' width="600" style="width:600px;max-width:600px;margin:0 auto;">'
        '<tr><td style="background:#ffffff;border-radius:14px;padding:4px 28px 20px;">%s</td></tr>'
        '<tr><td style="padding:16px 12px 0;font-family:%s;color:%s;font-size:11px;'
        'line-height:1.6;text-align:center;">'
        'NewMovies weekly digest. This product uses the TMDB API but is not endorsed '
        'or certified by TMDB.</td></tr>'
        '</table></div>' % (inner, FONT, FAINT))


def _chips(label, names):
    if not names:
        return ""
    return ('<div style="margin-top:4px;font-size:13px;color:%s;line-height:1.5;">'
            '<span style="color:%s;">%s:</span> %s</div>'
            % (BODY, MUTED, label, html.escape(", ".join(names))))


def _card(r, is_last):
    if r.get("poster_path"):
        poster = ('<img src="%s%s" width="%d" alt="" style="width:%dpx;border-radius:8px;'
                  'display:block;background:%s;">'
                  % (POSTER_BASE, r["poster_path"], POSTER_W, POSTER_W, RULE))
    else:
        poster = ('<div style="width:%dpx;height:%dpx;border-radius:8px;background:%s;"></div>'
                  % (POSTER_W, int(POSTER_W * 1.5), RULE))

    meta = []
    if r.get("vote_average"):
        meta.append('<span style="color:#f5a623;">&#9733;</span> %.1f' % r["vote_average"])
    if r.get("runtime"):
        meta.append("%d min" % r["runtime"])
    if r.get("language"):
        meta.append(html.escape(r["language"]))
    if r.get("genres"):
        meta.append(html.escape(", ".join(r["genres"])))
    meta_line = " &middot; ".join(meta)

    tmdb_url = "https://www.themoviedb.org/movie/%d" % r["id"]
    links = []
    if r.get("imdb_id"):
        links.append('<a href="https://www.imdb.com/title/%s/" style="color:%s;'
                     'text-decoration:none;">IMDb</a>' % (r["imdb_id"], LINK))
    links.append('<a href="%s" style="color:%s;text-decoration:none;">TMDB</a>' % (tmdb_url, LINK))
    if r.get("providers", {}).get("link"):
        links.append('<a href="%s" style="color:%s;text-decoration:none;">JustWatch</a>'
                     % (html.escape(r["providers"]["link"]), LINK))

    p = r.get("providers", {})
    watch = (_chips("Stream", p.get("stream"))
             + _chips("Rent", p.get("rent"))
             + _chips("Buy", p.get("buy")))

    date_line = ""
    if r.get("home_date"):
        date_line = ('<div style="color:%s;font-size:12px;margin-top:10px;">Available %s</div>'
                     % (FAINT, r["home_date"]))

    border = "" if is_last else "border-bottom:1px solid %s;" % RULE

    return """
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%%"
           style="%spadding:20px 0;">
      <tr>
        <td valign="top" width="%d" style="padding-right:16px;">%s</td>
        <td valign="top" style="font-family:%s;color:%s;">
          <div style="font-size:17px;font-weight:700;line-height:1.25;">
            <a href="%s" style="color:%s;text-decoration:none;">%s</a></div>
          <div style="color:%s;font-size:13px;margin-top:5px;">%s</div>
          <div style="font-size:13px;line-height:1.55;color:%s;margin-top:9px;">%s</div>
          %s%s
          <div style="margin-top:12px;font-size:13px;">%s</div>
        </td>
      </tr>
    </table>""" % (
        border, POSTER_W, poster, FONT, INK,
        tmdb_url, INK, html.escape(r["title"]),
        MUTED, meta_line,
        BODY, html.escape(r.get("overview") or ""),
        watch, date_line,
        (' <span style="color:%s;">&middot;</span> ' % FAINT).join(links),
    )


def _header(line, sub):
    return (
        '<div style="font-family:%s;padding-top:22px;padding-bottom:18px;'
        'border-bottom:1px solid %s;">'
        '<div style="font-size:12px;font-weight:600;letter-spacing:0.09em;'
        'text-transform:uppercase;color:%s;">New this week</div>'
        '<h1 style="font-size:24px;font-weight:800;color:%s;margin:8px 0 0;line-height:1.2;">%s</h1>'
        '<div style="color:%s;font-size:13px;margin-top:7px;">%s</div>'
        '</div>' % (FONT, RULE, MUTED, INK, line, FAINT, sub))


def render_html(records, win_start, win_end):
    n = len(records)
    header = _header(
        "%d new film%s now available" % (n, "" if n == 1 else "s"),
        "Newly on digital or disc &middot; %s to %s" % (win_start, win_end))
    links = "".join(_card(r, i == n - 1) for i, r in enumerate(records))
    return _shell(header + links)


def render_empty(win_start, win_end):
    body = (
        '<div style="font-family:%s;font-size:14px;line-height:1.6;color:%s;'
        'padding:18px 0 6px;">No movies became available on digital or disc between '
        '%s and %s. You will hear from me next week.</div>'
        % (FONT, BODY, win_start, win_end))
    return _shell(_header("Nothing new this week", "Quiet week &middot; %s to %s"
                          % (win_start, win_end)) + body)


def render_text(records, win_start, win_end):
    if not records:
        return "No new home releases for %s to %s." % (win_start, win_end)
    lines = ["New this week (%s to %s):" % (win_start, win_end), ""]
    for r in records:
        rating = r.get("vote_average")
        lines.append("- %s (%s)%s%s" % (
            r["title"], r.get("home_date") or "?",
            ("  %.1f/10" % rating) if rating else "",
            ("  [%s]" % r["language"]) if r.get("language") else ""))
        p = r.get("providers", {})
        if p.get("stream"):
            lines.append("    Stream: " + ", ".join(p["stream"]))
        if p.get("rent"):
            lines.append("    Rent: " + ", ".join(p["rent"]))
        if r.get("imdb_id"):
            lines.append("    https://www.imdb.com/title/%s/" % r["imdb_id"])
    return "\n".join(lines)
