"""Vestel & Toshiba TV Remote Control integration."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["media_player"]

CARD_FILENAME = "vestel_toshiba_tv-card.js"
_REGISTERED = False


async def _register_card(hass: HomeAssistant) -> None:
    """JS kartını config/www/ altına kopyala, Lovelace resource olarak ekle."""
    src = Path(__file__).parent / "www" / CARD_FILENAME

    www_dir = Path(hass.config.config_dir) / "www"
    www_dir.mkdir(exist_ok=True)
    dst = www_dir / CARD_FILENAME

    # Dosyayı kopyala (her güncellemede üzerine yaz)
    await hass.async_add_executor_job(shutil.copy2, str(src), str(dst))
    _LOGGER.debug("Kart kopyalandı: %s", dst)

    # Lovelace resource olarak kaydet
    url = f"/local/{CARD_FILENAME}"
    try:
        lovelace = hass.data.get("lovelace")
        if lovelace and hasattr(lovelace, "resources"):
            resources = lovelace.resources
            await resources.async_load()
            existing = [r["url"] for r in resources.async_items()]
            if url not in existing:
                await resources.async_create_item({"res_type": "module", "url": url})
                _LOGGER.info("Lovelace resource eklendi: %s", url)
    except Exception as err:
        _LOGGER.warning(
            "Lovelace resource otomatik eklenemedi (%s). "
            "Ayarlar → Dashboard → Kaynaklar → Ekle → %s",
            err, url,
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vestel & Toshiba TV from a config entry."""
    global _REGISTERED

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    if not _REGISTERED:
        await _register_card(hass)
        _REGISTERED = True

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_send_key(call: ServiceCall) -> None:
        key = call.data.get("key", "")
        component = hass.data.get("entity_components", {}).get("media_player")
        
        if not component:
            return
            
        for entity in component.entities:
            # entity_id parametresi uyuşmazlıklarını önlemek için kontrolü kaldırdık.
            # Sadece bu entegrasyona ait olan fonksiyona sahip cihazı bul ve komutu ateşle.
            if hasattr(entity, "async_send_key"):
                await entity.async_send_key(key)

    hass.services.async_register(DOMAIN, "send_key", handle_send_key)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
