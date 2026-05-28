# Household Dashboard

A self-hosted DAKboard-style household dashboard for a Raspberry Pi wall display. The app serves a read-only kiosk display at `/display`, a password-protected admin page at `/admin`, and a health endpoint at `/health`.

The MVP uses FastAPI, server-rendered HTML, SQLite, local photo folders, Open-Meteo weather, ICS calendar feeds, and a minimal Frigate integration.

## Quick Start

1. Copy the environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and change at least `ADMIN_PASSWORD` and `SESSION_SECRET`.

3. Start the app:

   ```bash
   docker compose up -d
   ```

4. Open:

   - Display: `http://localhost:8000/display`
   - Admin: `http://localhost:8000/admin`
   - Health: `http://localhost:8000/health`

Settings are stored in SQLite at `./data/dashboard.sqlite3` by default and persist across container restarts.

## Configuration

Important environment variables:

- `DATABASE_PATH`: SQLite path inside the container. Default: `/data/dashboard.sqlite3`
- `PHOTO_DIR`: local photo folder inside the container. Default: `/photos`
- `PHOTO_MAX_IMAGES`: maximum image paths to scan from the mounted photo folder. Default: `500`
- `ADMIN_PASSWORD`: password for `/admin`
- `SESSION_SECRET`: long random string used to sign admin sessions
- `DISPLAY_PUBLIC`: set to `false` if `/display` should also require login
- `CALENDAR_REFRESH_SECONDS`: ICS cache interval
- `WEATHER_REFRESH_SECONDS`: weather cache interval
- `FRIGATE_TIMEOUT_SECONDS`: snapshot proxy timeout

The included `docker-compose.yml` mounts:

- `./data` to `/data`
- `./photos` to `/photos`

Add `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, or `.avif` files to `./photos` for rotating backgrounds. The app scans nested folders, skips hidden folders and common recycle folders, and caps the scan with `PHOTO_MAX_IMAGES` so a large photo archive does not block the dashboard.

## Admin Settings

Use `/admin` to configure:

- Board title
- Weather latitude, longitude, label, and units
- ICS calendar URL, event count, and display timezone
- Photo rotation interval, background treatment, and photo frame behavior
- Frigate base URL, camera name, display mode, and live URL
- Block visibility
- Layout preset, display size, orientation, and custom block placement

The admin page is split into tabs for board, layout, photos, and data sources. The Layout tab includes block visibility, presets for common fullscreen displays, including landscape and portrait orientations, plus a custom drag-and-drop builder that saves block positions as percentages so layouts scale across display sizes.

Built-in layout presets include Classic, Focus, Camera first, Portrait, Photo frame, and Dense. The default target remains a 1920 x 1080 fullscreen monitor, with common alternatives such as 1080 x 1920, 2560 x 1440, 3840 x 2160, 1280 x 800, and custom dimensions.

Photos can be shown as the dashboard background, in a photo frame block, or both. Background options include fit mode and overlay strength; frame options include fit mode and optional captions.

## Calendar

Calendar support uses public or private ICS/iCal feed URLs. The display shows upcoming agenda items with title, date, start time, and optional end time. Set the calendar timezone in `/admin` using an IANA timezone name such as `America/Denver`, `America/New_York`, or `Europe/London`.

Examples of supported sources include Google Calendar secret iCal links, Apple Calendar published calendars, Outlook ICS links, and many calendar server feeds. If the feed is unavailable, the display keeps working and shows an error placeholder for the calendar block.

## Weather

Weather uses the Open-Meteo forecast API, which works with latitude and longitude and does not require an API key. Configure latitude and longitude in `/admin`; otherwise the display shows a setup placeholder.

## Frigate

Snapshot mode proxies:

```text
{FRIGATE_BASE_URL}/api/{camera_name}/latest.jpg
```

For example, with `Frigate base URL = http://frigate:5000` and `Camera name = front_door`, the app requests:

```text
http://frigate:5000/api/front_door/latest.jpg
```

Live mode expects a browser-playable URL, typically from Frigate/go2rtc using MSE or WebRTC. The app does not attempt to play RTSP directly in the browser. If live mode fails or no live URL is configured, switch back to snapshot mode.

## Raspberry Pi Kiosk Usage

With FullPageOS, set the configured page URL to:

```text
http://YOUR_SERVER_IP:8000/display
```

For a plain Chromium kiosk setup, a common launch command is:

```bash
chromium-browser --kiosk --disable-infobars http://YOUR_SERVER_IP:8000/display
```

Run the dashboard on another machine, on the Pi itself, or on a small home server. The wall display only needs a browser pointed at `/display`.

## Security Notes

- Change `ADMIN_PASSWORD` before exposing the app.
- Use a strong random `SESSION_SECRET`.
- Keep `/display` public only on trusted networks if using kiosk mode.
- For remote access, place the app behind a reverse proxy, VPN, Tailscale, or Cloudflare Access.
- If exposing through a reverse proxy, terminate HTTPS there and restrict `/admin` to trusted users or networks where possible.

## Development

Run locally without Docker:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```

## Future Improvements

- More robust recurring calendar expansion and timezone controls
- go2rtc-specific live view helpers
- Optional basic auth or OIDC behind a proxy
- Per-block refresh controls
- Portrait-optimized layout presets
- Weather icons and severe weather notices
- Admin-side preview of display layout
