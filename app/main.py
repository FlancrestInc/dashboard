from __future__ import annotations

import secrets

import httpx
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import AppConfig, get_config
from app.db import SettingsStore
from app.services.cache import TTLCache
from app.services.calendar import CalendarService
from app.services.frigate import FrigateService
from app.services.photos import PhotoService
from app.services.weather import WeatherService
from app.settings import admin_block_instances, layout_for_display, settings_from_form

templates = Jinja2Templates(directory="app/templates")
cache = TTLCache()


def create_app() -> FastAPI:
    config = get_config()
    app = FastAPI(title=config.app_name)
    app.add_middleware(SessionMiddleware, secret_key=config.session_secret, same_site="lax")
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.mount("/photos", StaticFiles(directory=config.photo_dir), name="photos")
    store = SettingsStore(config.database_path)
    calendar_service = CalendarService(cache, config.calendar_refresh_seconds)
    weather_service = WeatherService(cache, config.weather_refresh_seconds)
    photo_service = PhotoService(config.photo_dir, config.photo_max_images)
    frigate_service = FrigateService()

    async def display_payload() -> dict:
        settings = store.get_settings()
        return {
            "settings": settings,
            "layout": layout_for_display(settings),
            "calendar": await calendar_service.agenda(settings),
            "weather": await weather_service.current_and_forecast(settings),
            "photos": photo_service.payload(settings),
            "frigate": frigate_service.status(settings),
        }

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    async def root() -> RedirectResponse:
        return RedirectResponse("/display", status_code=302)

    @app.get("/display", response_class=HTMLResponse)
    async def display(request: Request):
        if not config.display_public and not _is_authenticated(request):
            return RedirectResponse("/admin/login", status_code=302)
        payload = await display_payload()
        return templates.TemplateResponse("display.html", {"request": request, **payload})

    @app.get("/api/display-data")
    async def api_display_data(request: Request):
        if not config.display_public and not _is_authenticated(request):
            raise HTTPException(status_code=401, detail="Authentication required")
        return await display_payload()

    @app.get("/api/frigate/snapshot")
    async def frigate_snapshot(camera: str):
        settings = store.get_settings()
        url = frigate_service.snapshot_url(settings, camera)
        if not url:
            raise HTTPException(status_code=404, detail="Frigate snapshot is not configured")
        try:
            async with httpx.AsyncClient(timeout=config.frigate_timeout_seconds, follow_redirects=True) as client:
                upstream = await client.get(url)
                upstream.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Could not fetch Frigate snapshot: {exc}") from exc
        content_type = upstream.headers.get("content-type", "image/jpeg")
        return Response(content=upstream.content, media_type=content_type)

    @app.get("/admin/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        return templates.TemplateResponse("login.html", {"request": request, "error": None})

    @app.post("/admin/login")
    async def login(request: Request, password: str = Form(...)):
        if secrets.compare_digest(password.strip(), config.admin_password.strip()):
            request.session["admin"] = True
            return RedirectResponse("/admin", status_code=303)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Password did not match."},
            status_code=401,
        )

    @app.post("/admin/logout")
    async def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/admin/login", status_code=303)

    @app.get("/admin", response_class=HTMLResponse)
    async def admin(request: Request, authenticated: bool = Depends(_require_admin)):
        settings = store.get_settings()
        admin_blocks = admin_block_instances(settings)
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "settings": settings,
                "admin_blocks": admin_blocks,
                "photo_blocks": [block for block in admin_blocks if block["type"] == "photos"],
                "camera_blocks": [block for block in admin_blocks if block["type"] == "frigate"],
                "saved": request.query_params.get("saved") == "1",
            },
        )

    @app.post("/admin")
    async def save_admin(request: Request, authenticated: bool = Depends(_require_admin)):
        form = dict(await request.form())
        store.save_settings(settings_from_form(form))
        return RedirectResponse("/admin?saved=1", status_code=303)

    return app


def _is_authenticated(request: Request) -> bool:
    return bool(request.session.get("admin"))


def _require_admin(request: Request) -> bool:
    if not _is_authenticated(request):
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return True


app = create_app()
