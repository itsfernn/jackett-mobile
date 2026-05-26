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
  -p 5000:5000 \
  -e JACKETT_URL=http://192.168.1.100:9117 \
  -e JACKETT_API_KEY=your_api_key_here \
  -e INDEXERS=all \
  -e APP_TITLE="Jackett Mobile" \
  ghcr.io/youruser/jackett-mobile:latest
```

Or with Docker Compose:

```yaml
services:
  jackett-mobile:
    image: ghcr.io/youruser/jackett-mobile:latest
    container_name: jackett-mobile
    ports:
      - "5000:5000"
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
    image: youruser/jackett-mobile:latest
    container_name: jackett-movies
    ports:
      - "5001:5000"
    environment:
      - JACKETT_URL=http://jackett:9117
      - JACKETT_API_KEY=your_api_key_here
      - INDEXERS=1337x,rarbg
      - APP_TITLE=Movie Search

  jackett-audiobooks:
    image: youruser/jackett-mobile:latest
    container_name: jackett-audiobooks
    ports:
      - "5002:5000"
    environment:
      - JACKETT_URL=http://jackett:9117
      - JACKETT_API_KEY=your_api_key_here
      - INDEXERS=audiobookbay
      - APP_TITLE=Audiobook Search
```

## Building from Source

```bash
git clone https://github.com/youruser/jackett-mobile.git
cd jackett-mobile
docker build -t jackett-mobile .
```

## Publishing to Docker Hub

1. **Build and tag the image:**

   ```bash
   docker build -t youruser/jackett-mobile:latest .
   docker tag youruser/jackett-mobile:latest youruser/jackett-mobile:1.0.0
   ```

2. **Log in and push:**

   ```bash
   docker login
   docker push youruser/jackett-mobile:latest
   docker push youruser/jackett-mobile:1.0.0
   ```

3. **Set up automated builds (optional):**

   Connect your GitHub repo to Docker Hub under **Builds** → link repository → set build rules for `main` → `latest`.

### Using GitHub Container Registry

```bash
docker build -t ghcr.io/youruser/jackett-mobile:latest .
docker push ghcr.io/youruser/jackett-mobile:latest
```

## Unraid / Community Apps Release

To make this available on Unraid's Community Apps:

1. **Create a template repository.** Fork or create a repo at `https://github.com/youruser/unraid-templates` following the [Unraid template spec](https://forums.unraid.net/topic/57181-docker-faq-the-docker-faq/).

2. **Add a template XML** at `templates/jackett-mobile.xml`:

   ```xml
   <?xml version="1.0"?>
   <Container version="2">
     <Name>jackett-mobile</Name>
     <Repository>youruser/jackett-mobile:latest</Repository>
     <Registry>https://hub.docker.com/r/youruser/jackett-mobile</Registry>
     <Network>bridge</Network>
     <MyIP/>
     <Shell>sh</Shell>
     <Privileged>false</Privileged>
     <Support>https://github.com/youruser/jackett-mobile/issues</Support>
     <Project>https://github.com/youruser/jackett-mobile</Project>
     <Overview>A lightweight mobile-friendly web interface for Jackett.</Overview>
     <Category>MediaApp:Video MediaApp:Audio</Category>
     <WebUI>http://[IP]:[PORT:5000]</WebUI>
     <TemplateURL>https://raw.githubusercontent.com/youruser/unraid-templates/main/templates/jackett-mobile.xml</TemplateURL>
     <Icon>https://raw.githubusercontent.com/youruser/jackett-mobile/main/icon.png</Icon>
     <ExtraParams/>
     <PostArgs/>
     <CPUset/>
     <DateInstalled/>
     <DonateText/>
     <DonateLink/>
     <Description>A lightweight mobile-friendly web interface for Jackett that lets you search torrents, download directly, or send them to your server's black hole.</Description>
     <Requires>
       <Requires>jackett</Requires>
     </Requires>
     <Config Name="Port" Target="5000" Default="5000" Mode="tcp" Description="Web UI port" Type="Port" Display="always" Required="true" Mask="false">5000</Config>
     <Config Name="Jackett URL" Target="JACKETT_URL" Default="http://192.168.1.100:9117" Mode="" Description="Base URL of your Jackett instance" Type="Variable" Display="always" Required="true" Mask="false">http://192.168.1.100:9117</Config>
     <Config Name="Jackett API Key" Target="JACKETT_API_KEY" Default="" Mode="" Description="Your Jackett API key" Type="Variable" Display="always" Required="true" Mask="true"/>
     <Config Name="Indexers" Target="INDEXERS" Default="all" Mode="" Description="Indexer filter expression (all, name, tag:group, etc.)" Type="Variable" Display="always" Required="false" Mask="false">all</Config>
     <Config Name="App Title" Target="APP_TITLE" Default="Jackett Mobile" Mode="" Description="Page title shown in header and browser tab" Type="Variable" Display="always" Required="false" Mask="false">Jackett Mobile</Config>
   </Container>
   ```

3. **Submit to Community Apps.** Open a PR at [unraid.net/communityapps](https://unraid.net/communityapps) linking to your template repo.

## Tech Stack

- **Backend:** Python, FastAPI, httpx
- **Frontend:** Vanilla HTML/CSS/JS (no framework)
- **Container:** Python 3.11-slim
