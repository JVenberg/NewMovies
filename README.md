# NewMovies digest

Weekly email of movies that **newly became available on digital or disc in the US** within the last 14 days (a strong signal a high-quality torrent now exists). Data from TMDB; emailed from your Gmail over SMTP. Runs as a **Cloud Run Job** triggered by **Cloud Scheduler** (Fri 17:00 `America/Los_Angeles`).

## Selection logic
1. `GET /discover/movie?region=US&with_release_type=4|5&release_date.gte=…&release_date.lte=…` over the last 14 days (`4` = Digital, `5` = Physical).
2. Keep films whose **earliest** US digital/physical date is inside the window (this drops catalog re-releases, e.g. an old title getting a fresh Blu-ray) and `popularity >= 10`.
3. For **non-English** films, additionally require `vote_count >= 50`. TMDB's rating base is US/English-skewed, so this keeps culturally-relevant foreign films (festival/Netflix titles) while dropping regionally-popular-but-unwatched-here releases. English films are never filtered this way.
4. Drop anything already emailed (dedup state).
5. Enrich each kept film with one `GET /movie/{id}?append_to_response=watch/providers,external_ids` call.
6. Render rich HTML (poster, rating, runtime, language, genres, overview, where-to-watch, IMDb/TMDB/JustWatch links) and send.

## Local development
```bash
uv run python -m newmovies --dry-run                   # print selection, send nothing
uv run python -m newmovies                             # send for real (file-backed state.json)
TODAY=2026-06-21 uv run python -m newmovies --dry-run  # pin the window for reproducible testing
```
Config is read from `.env` (gitignored).

## Configuration (env vars)
| Var | Default | Purpose |
|---|---|---|
| `TMDB_TOKEN` | _(required)_ | TMDB v4 read access token |
| `GMAIL_ADDRESS` | _(required)_ | sender Gmail address |
| `GMAIL_APP_PASSWORD` | _(required)_ | Gmail app password (needs 2FA) |
| `EMAIL_TO` | = `GMAIL_ADDRESS` | comma-separated recipients |
| `REGION` | `US` | TMDB region |
| `WINDOW_DAYS` | `14` | lookback window |
| `MIN_POPULARITY` | `10` | noise threshold |
| `MIN_FOREIGN_VOTES` | `50` | non-English only: require at least this many TMDB votes (proxy for US viewership); `0` disables |
| `SEND_WHEN_EMPTY` | `true` | send a "nothing new" note on quiet weeks |
| `STATE_BACKEND` | `file` | `file` locally, `gcs` in Cloud Run |
| `STATE_GCS_BUCKET` | _(empty)_ | GCS bucket for dedup state (cloud) |
| `STATE_GCS_OBJECT` | `state.json` | state object name |
| `STATE_RETENTION_DAYS` | `30` | how long to remember sent IDs |
| `TODAY` | _(empty)_ | ISO date override for testing |

## Deploy to GCP
```bash
./deploy.sh
gcloud run jobs execute newmovies-digest --region=us-west1 --project=newmovies-digest
```
- Project `newmovies-digest`, region `us-west1`.
- Image: Alpine + Python 3.13, **zero third-party deps** (~60MB). Artifact Registry repo `newmovies` with a keep-latest-only cleanup policy (`cleanup-policy.json`).
- Secrets (`tmdb-token`, `gmail-app-password`) in Secret Manager; non-secret config as job env vars; dedup state in `gs://newmovies-digest-state`.

## Cost
Cloud Run / Scheduler / Secret Manager / GCS usage all sit inside GCP Always Free → expected **~$0/month**, guarded by a $2 budget alert (50/90/100%).
