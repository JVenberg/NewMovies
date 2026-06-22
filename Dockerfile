# syntax=docker/dockerfile:1
# The app has zero third-party dependencies, so the runtime image is just
# Alpine Python + our package. uv governs local dev (pyproject/uv.lock); it
# would add nothing but weight to a no-dependency image, so it's omitted here.
FROM python:3.13-alpine

WORKDIR /app
COPY newmovies/ ./newmovies/

ENV PYTHONUNBUFFERED=1 \
    STATE_BACKEND=gcs

ENTRYPOINT ["python", "-m", "newmovies"]
