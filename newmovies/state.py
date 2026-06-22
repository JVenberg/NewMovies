import datetime
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from . import config


def _safe_date(value):
    try:
        return datetime.date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _prune(sent):
    cutoff = datetime.date.today() - datetime.timedelta(days=config.STATE_RETENTION_DAYS)
    return {k: v for k, v in sent.items() if (_safe_date(v) or cutoff) >= cutoff}


def _load_file():
    if not os.path.exists(config.STATE_FILE):
        return {}
    with open(config.STATE_FILE) as f:
        return json.load(f).get("sent", {})


def _save_file(sent):
    with open(config.STATE_FILE, "w") as f:
        json.dump({"sent": sent}, f, indent=2)


def _metadata_token():
    req = urllib.request.Request(
        "http://metadata.google.internal/computeMetadata/v1/instance/"
        "service-accounts/default/token",
        headers={"Metadata-Flavor": "Google"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)["access_token"]


def _gcs_url(upload=False):
    bucket = config.STATE_GCS_BUCKET
    obj = urllib.parse.quote(config.STATE_GCS_OBJECT, safe="")
    if upload:
        return ("https://storage.googleapis.com/upload/storage/v1/b/%s/o"
                "?uploadType=media&name=%s" % (bucket, obj))
    return "https://storage.googleapis.com/storage/v1/b/%s/o/%s?alt=media" % (bucket, obj)


def _load_gcs():
    req = urllib.request.Request(
        _gcs_url(), headers={"Authorization": "Bearer " + _metadata_token()})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp).get("sent", {})
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {}
        raise


def _save_gcs(sent):
    body = json.dumps({"sent": sent}).encode()
    req = urllib.request.Request(
        _gcs_url(upload=True),
        data=body,
        method="POST",
        headers={
            "Authorization": "Bearer " + _metadata_token(),
            "Content-Type": "application/json",
        },
    )
    urllib.request.urlopen(req, timeout=30).read()


def load():
    return _load_gcs() if config.STATE_BACKEND == "gcs" else _load_file()


def save(sent):
    sent = _prune(sent)
    if config.STATE_BACKEND == "gcs":
        _save_gcs(sent)
    else:
        _save_file(sent)
