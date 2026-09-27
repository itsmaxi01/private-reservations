from fastapi import APIRouter, Depends

from app.config import Settings, get_settings


router = APIRouter(prefix="/config", tags=["config"])


@router.get("/public")
def public_config(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    settings.validate_auth_configuration()
    assert settings.supabase_url and settings.supabase_publishable_key
    return {
        "supabaseUrl": settings.supabase_url,
        "supabasePublishableKey": settings.supabase_publishable_key,
    }

