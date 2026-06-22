import os


def _load_dotenv(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ.setdefault(key, val)


_load_dotenv()


def _get(name, default=None, required=False):
    val = os.environ.get(name, default)
    if required and not val:
        raise RuntimeError("Missing required env var: " + name)
    return val


TMDB_TOKEN = _get("TMDB_TOKEN", required=True)
GMAIL_ADDRESS = _get("GMAIL_ADDRESS", required=True)
GMAIL_APP_PASSWORD = _get("GMAIL_APP_PASSWORD", required=True)
EMAIL_TO = [a.strip() for a in _get("EMAIL_TO", GMAIL_ADDRESS).split(",") if a.strip()]

REGION = _get("REGION", "US")
WINDOW_DAYS = int(_get("WINDOW_DAYS", "14"))
MIN_POPULARITY = float(_get("MIN_POPULARITY", "10"))
SEND_WHEN_EMPTY = _get("SEND_WHEN_EMPTY", "true").lower() in ("1", "true", "yes")
# For non-English films only: require at least this many TMDB votes, a proxy for real
# US/English viewership. Filters out regionally-popular-but-unwatched-here films.
# Set 0 to disable.
MIN_FOREIGN_VOTES = int(_get("MIN_FOREIGN_VOTES", "50"))
TODAY = _get("TODAY")  # ISO date override for testing; otherwise date.today()

STATE_BACKEND = _get("STATE_BACKEND", "file")  # "file" | "gcs"
STATE_FILE = _get("STATE_FILE", "state.json")
STATE_GCS_BUCKET = _get("STATE_GCS_BUCKET", "")
STATE_GCS_OBJECT = _get("STATE_GCS_OBJECT", "state.json")
STATE_RETENTION_DAYS = int(_get("STATE_RETENTION_DAYS", "30"))
