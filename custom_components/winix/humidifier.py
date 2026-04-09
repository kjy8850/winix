"""Winix Dehumidifier Device."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
import logging
from typing import Any

from homeassistant.components.humidifier import (
    DOMAIN as HUMIDIFIER_DOMAIN,
    HumidifierEntity,
    HumidifierDeviceClass,
    HumidifierEntityFeature,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import WinixConfigEntry
from .const import (
    ATTR_MODE,
    ATTR_FAN_SPEED,
    ATTR_HUMIDITY,
    ATTR_TARGET_HUMIDITY,
    ATTR_TIMER,
    ATTR_CHILD_LOCK,
    ATTR_UV_STERILIZATION,
    LOGGER,
    ORDERED_NAMED_FAN_SPEEDS,
    WINIX_DOMAIN,
    PRESET_MODES,
)
from .device_wrapper import WinixDeviceWrapper
from .manager import WinixEntity, WinixManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WinixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Winix dehumidifiers."""
    manager = entry.runtime_data
    entities = [
        WinixDehumidifier(wrapper, manager) for wrapper in manager.get_device_wrappers()
    ]
    async_add_entities(entities)
    LOGGER.info("Added %s Winix dehumidifiers", len(entities))


class WinixDehumidifier(WinixEntity, HumidifierEntity):
    """Representation of a Winix Dehumidifier entity."""

    _attr_supported_features = HumidifierEntityFeature.MODES

    def __init__(self, wrapper: WinixDeviceWrapper, coordinator: WinixManager) -> None:
        """Initialize the entity."""
        super().__init__(wrapper, coordinator)
        self._attr_unique_id = f"{HUMIDIFIER_DOMAIN}.{WINIX_DOMAIN}_{self._mac}"

    @property
    def min_humidity(self) -> int:
        return 35

    @property
    def max_humidity(self) -> int:
        return 70

    @property
    def humidity_step(self) -> int:
        return 5

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return the state attributes."""
        attributes = {}
        state = self.device_wrapper.get_state()

        if state is not None:
            attributes = {key: value for key, value in state.items()}

        return attributes

    @property
    def is_on(self) -> bool:
        """Return true if dehumidifier is on."""
        return self.device_wrapper.is_on

    @property
    def mode(self) -> str | None:
        """Return the current mode."""
        state = self.device_wrapper.get_state()
        return state.get(ATTR_MODE)

    @property
    def available_modes(self) -> list[str]:
        """Return available operation modes."""
        return PRESET_MODES

    @property
    def target_humidity(self) -> int | None:
        """Return the target humidity percentage set by the user."""
        state = self.device_wrapper.get_state()
        return state.get(ATTR_TARGET_HUMIDITY, None)

    async def async_set_mode(self, mode: str) -> None:
        """Set the operation mode."""
        await self.device_wrapper.async_set_mode(mode)
        self.async_write_ha_state()

    async def async_set_humidity(self, humidity: int) -> None:
        """Set the target humidity level."""
        if not (35 <= humidity <= 70):
            LOGGER.warning("Invalid humidity value: %s", humidity)
            return
        if humidity % 5 != 0:
            LOGGER.warning("Humidity must be set in 5%% steps. You passed: %s", humidity)
            return
        await self.device_wrapper.async_set_humidity(humidity)
        self.async_write_ha_state()

    async def async_turn_on(self, mode: str | None = None, humidity: int | None = None, **kwargs: Any) -> None:
        """Turn on the dehumidifier with optional mode and humidity."""
        if mode:
            await self.async_set_mode(mode)
        if humidity:
            await self.async_set_humidity(humidity)
        await self.device_wrapper.async_turn_on()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the dehumidifier."""
        await self.device_wrapper.async_turn_off()
        self.async_write_ha_state()

    async def async_set_fan_speed(self, speed: str) -> None:
        """Set the fan speed."""
        await self.device_wrapper.async_set_fan_speed(speed)
        self.async_write_ha_state()

    async def async_set_timer(self, timer: int) -> None:
        """Set the timer."""
        await self.device_wrapper.async_set_timer(timer)
        self.async_write_ha_state()

    async def async_set_child_lock(self, lock: bool) -> None:
        """Enable or disable child lock."""
        await self.device_wrapper.async_set_child_lock(lock)
        self.async_write_ha_state()

    async def async_set_uv_sterilization(self, uv: bool) -> None:
        """Enable or disable UV sterilization."""
        await self.device_wrapper.async_set_uv_sterilization(uv)
        self.async_write_ha_state()
