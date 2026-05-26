# Jackett Mobile

A lightweight, mobile-friendly web interface for [Jackett](https://github.com/Jackett/Jackett). Search torrents, download directly, or send them to your server's black hole — all from your phone.

## Features

- **Mobile-first** — clean, touch-friendly UI that works great on phones
- **Search & download** — search any Jackett indexer and download torrents
- **Black hole support** — send torrents directly to your server's black hole directory (configured in Jackett)
- **Per-indexer filtering** — use Jackett's filter system to search specific indexers, tags, or types
- **Sorting & filtering** — sort results by seeders, peers, size, or date; filter by title
- **Multiple instances** — run separate containers for different categories (e.g. one for audiobooks, one for TV, one for movies), each with its own title and indexer filter
- **All config via env vars** — no config files, no rebuilds

## Quick Start

```bash
docker run -d \
  --name jackett-mobile \
  -p 9118:9118 \
  -e JACKETT_URL=http://192.168.1.100:9117 \
  -e JACKETT_API_KEY=your_api_key_here \
  -e INDEXERS=all \
  -e APP_TITLE="Jackett Mobile" \
  itsfernn/jackett-mobile:latest
```

Or with Docker Compose:

```yaml
services:
  jackett-mobile:
    image: itsfernn/jackett-mobile:latest
    container_name: jackett-mobile
    ports:
      - "9118:9118"
    environment:
      - JACKETT_URL=http://jackett:9117
      - JACKETT_API_KEY=your_api_key_here
      - INDEXERS=all
      - APP_TITLE=Jackett Mobile
    restart: unless-stopped
```

## Configuration

All configuration is done through environment variables.

| Variable | Default | Description |
|---|---|---|
| `JACKETT_URL` | `http://localhost:9117` | Base URL of your Jackett instance |
| `JACKETT_API_KEY` | — | Jackett API key (required) |
| `INDEXERS` | `all` | [Indexer filter](#indexer-filters) expression |
| `APP_TITLE` | `Jackett Mobile` | Page title shown in the header and browser tab |

### Indexer Filters

The `INDEXERS` variable accepts Jackett's native filter expressions. This gives you full control over which indexers are searched.

| Format | Example | Description |
|---|---|---|
| `all` | `all` | Search all configured indexers |
| Single indexer | `1337x` | Search one specific indexer by ID |
| Multiple (OR) | `1337x,audiobookbay` | Search either indexer |
| By tag | `tag:group1` | Search all indexers tagged with `group1` |
| By type | `!type:private` | Exclude private indexers |
| Combined (AND) | `tag:group1+lang:en` | Indexers matching all conditions |
| JSON array | `["1337x","abooks"]` | Alternative multiple-indexer syntax |

### Running Multiple Instances

A common setup is running separate containers for different content types, each pointed at different indexers:

```yaml
services:
  jackett-movies:
    image: itsfernn/jackett-mobile:latest
    container_name: jackett-movies
    ports:
      - "9119:9118"
    environment:
      - JACKETT_URL=http://jackett:9117
      - JACKETT_API_KEY=your_api_key_here
      - INDEXERS=1337x,rarbg
      - APP_TITLE=Movie Search

  jackett-audiobooks:
    image: itsfernn/jackett-mobile:latest
    container_name: jackett-audiobooks
    ports:
      - "9120:9118"
    environment:
      - JACKETT_URL=http://jackett:9117
      - JACKETT_API_KEY=your_api_key_here
      - INDEXERS=audiobookbay
      - APP_TITLE=Audiobook Search
```

## Building from Source

```bash
git clone https://github.com/itsfernn/jackett-mobile.git
cd jackett-mobile
docker build -t jackett-mobile .
```

## Publishing to Docker Hub

1. **Build and tag the image:**

   ```bash
   docker build -t itsfernn/jackett-mobile:latest .
   docker tag itsfernn/jackett-mobile:latest itsfernn/jackett-mobile:1.0.0
   ```

2. **Log in and push:**

   ```bash
   docker login
   docker push itsfernn/jackett-mobile:latest
   docker push itsfernn/jackett-mobile:1.0.0
   ```

3. **Set up automated builds (optional):**

   Connect your GitHub repo to Docker Hub under **Builds** → link repository → set build rules for `main` → `latest`.

### Using GitHub Container Registry

```bash
docker build -t ghcr.io/itsfernn/jackett-mobile:latest .
docker push ghcr.io/itsfernn/jackett-mobile:latest
```

## Unraid / Community Apps Release

To make this available on Unraid's Community Apps:

1. **Create a template repository.** Create a repo at `https://github.com/itsfernn/unraid-templates` following the [Unraid template spec](https://forums.unraid.net/topic/57181-docker-faq-the-docker-faq/).

2. **Copy the template XML.** The [`jackett-mobile.xml`](jackett-mobile.xml) file is already included in this project. Place it at `templates/jackett-mobile.xml` in your `unraid-templates` repo.

3. **Submit to Community Apps.** Open a PR at [unraid.net/communityapps](https://unraid.net/communityapps) linking to your template repo at `https://raw.githubusercontent.com/itsfernn/unraid-templates/main/templates/jackett-mobile.xml`.

## Tech Stack

- **Backend:** Python, FastAPI, httpx
- **Frontend:** Vanilla HTML/CSS/JS (no framework)
- **Container:** Python 3.11-slim
