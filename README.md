# CyberTrack — Cyber Crime Location Tracker

> **Authorized law enforcement and licensed cybersecurity use only.**

A 100% free, Python-based tracking system built with FastAPI + Supabase + ip-api.com.

---

## Stack (all free)

| Component | Tool |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Database | Supabase (free tier) |
| IP Geolocation | ip-api.com (no key needed) |
| UA Parsing | `user-agents` Python library |
| Slug Generation | `nanoid` |
| Frontend | Jinja2 + Tailwind CDN |
| Map | Leaflet.js CDN |
| Hosting | Render.com free tier |

---

## Setup

### 1. Clone and install

```bash
git clone <your-repo>
cd cyber-tracker
pip install -r requirements.txt
```

### 2. Supabase setup

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to **SQL Editor** and paste the contents of `database/schema.sql`
4. Run it — this creates the two tables

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your Supabase URL and key
```

Get your keys from Supabase → Settings → API:
- `SUPABASE_URL` = Project URL
- `SUPABASE_KEY` = `service_role` key (not anon — needs write access)

### 4. Run locally

```bash
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000` → redirects to `/dashboard`

---

## Usage

### Generate a tracking link

1. Open `/dashboard`
2. Enter a Case ID and label
3. Click **Generate Link** → copy the URL
4. Send the URL to the suspect via email, SMS, or any channel

### What gets captured when they open it

| Data | Source |
|---|---|
| IP address | Server-side |
| Country, City, Region | ip-api.com (free) |
| ISP / Organisation | ip-api.com |
| Mobile network / Proxy / VPN | ip-api.com |
| GPS coordinates (if granted) | Browser Geolocation API |
| Device brand + model | User-Agent parsing |
| OS + version | User-Agent parsing |
| Browser + version | User-Agent parsing |
| Screen resolution | JavaScript |
| Language + timezone | JavaScript |
| Connection type | JavaScript |

### View results

- `/dashboard` — all links
- `/dashboard/logs/{link_id}` — full data table
- `/dashboard/map/{link_id}` — Leaflet map with pins

---

## Deploy to Render (free)

1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`
6. Deploy — Render gives you a free HTTPS URL

---

## Project Structure

```
cyber-tracker/
├── main.py                    # FastAPI app
├── requirements.txt
├── .env.example
├── database/
│   └── schema.sql             # Supabase tables
├── routers/
│   ├── track.py               # GET /t/{slug}
│   ├── ingest.py              # POST /api/ingest
│   ├── links.py               # POST /api/links/create
│   └── dashboard.py           # GET /dashboard/*
├── services/
│   ├── supabase_client.py
│   ├── ip_lookup.py           # ip-api.com (free)
│   └── link_service.py        # Slug gen + DB ops
├── templates/
│   ├── base.html
│   ├── tracking_page.html     # Silent capture page
│   ├── dashboard.html
│   ├── logs.html
│   └── map.html
└── static/
    └── tracker.js             # Client-side capture
```
