from __future__ import annotations

import asyncio
from collections.abc import Mapping
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.humidifier import (
    DOMAIN as HUMIDIFIER_DOMAIN,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .const import (
    ATTR_FAN_SPEED,
    ATTR_HUMIDITY,
    ATTR_TARGET_HUMIDITY,
    ATTR_TIMER,
    ATTR_CHILD_LOCK,
    ATTR_UV_STERILIZATION,
    ORDERED_NAMED_FAN_SPEEDS,
    WINIX_DATA_COORDINATOR,
    WINIX_DATA_KEY,
    WINIX_DOMAIN,
)
from .device_wrapper import WinixDeviceWrapper
from .manager import WinixEntity, WinixManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Winix dehumidifiers."""
    data = hass.data[WINIX_DOMAIN][entry.entry_id]
    manager: WinixManager = data[WINIX_DATA_COORDINATOR]
    entities = [
        WinixDehumidifier(wrapper, manager) for wrapper in manager.get_device_wrappers()
    ]
    data[WINIX_DATA_KEY] = entities
    async_add_entities(entities)

    async def async_service_handler(service_call):
        """Service handler."""
        method = "async_" + service_call.service
        _LOGGER.debug("Service '%s' invoked", service_call.service)

        params = {}
        entity_ids = service_call.data.get(ATTR_ENTITY_ID)
        if entity_ids:
            devices = [
                entity
                for entity in data[WINIX_DATA_KEY]
                if entity.entity_id in entity_ids
            ]
        else:
            devices = data[WINIX_DATA_KEY]

        state_update_tasks = []
        for device in devices:
            if not hasattr(device, method):
                continue

            await getattr(device, method)(**params)
            state_update_tasks.append(
                asyncio.create_task(device.async_update_ha_state(True))
            )

        if state_update_tasks:
            await asyncio.wait(state_update_tasks)

    _LOGGER.info("Added %s Winix dehumidifiers", len(entities))


class WinixDehumidifier(WinixEntity, FanEntity):
    """Representation of a Winix Dehumidifier entity."""

    _attr_supported_features = (
        HumidifierEntityFeature.SET_SPEED
        | HumidifierEntityFeature.TURN_ON
        | HumidifierEntityFeature.TURN_OFF
    )

    def __init__(self, wrapper: WinixDeviceWrapper, coordinator: WinixManager) -> None:
        """Initialize the entity."""
        super().__init__(wrapper, coordinator)
        self._attr_unique_id = f"{HUMIDIFIER_DOMAIN}.{WINIX_DOMAIN}_{self._mac}"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return the state attributes."""
        attributes = {}
        state = self._wrapper.get_state()
        
        if state is not None:
            attributes = {
                key: value for key, value in state.items()
            }

        return attributes

    @property
    def is_on(self) -> bool:
        """Return true if dehumidifier is on."""
        return self._wrapper.is_on

    @property
    def percentage(self) -> int | None:
        """Return the current fan speed percentage."""
        state = self._wrapper.get_state()
        if state is None:
            return None
        if state.get(ATTR_FAN_SPEED) is None:
            return None
        return ordered_list_item_to_percentage(
            ORDERED_NAMED_FAN_SPEEDS, state.get(ATTR_FAN_SPEED)
        )

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan speed percentage."""
        if percentage == 0:
            await self.async_turn_off()
        else:
            await self._wrapper.async_set_fan_speed(
                percentage_to_ordered_list_item(ORDERED_NAMED_FAN_SPEEDS, percentage)
            )
        self.async_write_ha_state()

    async def async_turn_on(self, mode: str | None = None, humidity: int | None = None, **kwargs: Any) -> None:
        """Turn on the dehumidifier with optional mode and humidity."""
        if mode:
            await self.async_set_mode(mode)
        if humidity:
            await self.async_set_humidity(humidity)

        await self._wrapper.async_turn_on()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the dehumidifier."""
        await self._wrapper.async_turn_off()
        self.async_write_ha_state()

    async def async_set_fan_speed(self, speed: str) -> None:
        """Set the fan speed."""
        await self._wrapper.async_set_fan_speed(speed)
        self.async_write_ha_state()

    async def async_set_target_humidity(self, humidity: int) -> None:
        """Set the target humidity level."""
        await self._wrapper.async_set_humidity(humidity)
        self.async_write_ha_state()

    async def async_set_timer(self, timer: int) -> None:
        """Set the timer."""
        await self._wrapper.async_set_timer(timer)
        self.async_write_ha_state()

    async def async_set_child_lock(self, lock: bool) -> None:
        """Enable or disable child lock."""
        await self._wrapper.async_set_child_lock(lock)
        self.async_write_ha_state()

    async def async_set_uv_sterilization(self, uv: bool) -> None:
        """Enable or disable UV sterilization."""
        await self._wrapper.async_set_uv_sterilization(uv)
        self.async_write_ha_state()
