from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any, Final

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import WINIX_DOMAIN
from .const import (
    ATTR_HUMIDITY,
    ATTR_TARGET_HUMIDITY,
    SENSOR_HUMIDITY,
    SENSOR_TARGET_HUMIDITY,
    WINIX_DATA_COORDINATOR,
)
from .device_wrapper import WinixDeviceWrapper
from .manager import WinixEntity, WinixManager

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=SENSOR_HUMIDITY,
        icon="mdi:water-percent",
        name="Current Humidity",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=SENSOR_TARGET_HUMIDITY,
        icon="mdi:target",
        name="Target Humidity",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Winix dehumidifier sensors."""
    data = hass.data[WINIX_DOMAIN][entry.entry_id]
    manager: WinixManager = data[WINIX_DATA_COORDINATOR]

    entities = [
        WinixSensor(wrapper, manager, description)
        for description in SENSOR_TYPES
        for wrapper in manager.get_device_wrappers()
    ]
    async_add_entities(entities)
    _LOGGER.info("Added %s sensors", len(entities))


class WinixSensor(WinixEntity, SensorEntity):
    """Representation of a Winix Dehumidifier sensor."""

    def __init__(
        self,
        wrapper: WinixDeviceWrapper,
        coordinator: WinixManager,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(wrapper, coordinator)
        self.entity_description = description

        self._attr_unique_id = (
            f"{SENSOR_DOMAIN}.{WINIX_DOMAIN}_{description.key.lower()}_{self._mac}"
        )
        
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        state = self._wrapper.get_state()
        _LOGGER.debug("Sensor State Data: %s", state)  # 현재 상태 전체 로그 출력

        if state is None:
            _LOGGER.warning("State is None for sensor: %s", self.entity_description.key)
            return None

        if self.entity_description.key == SENSOR_HUMIDITY:
            humidity = state.get(ATTR_HUMIDITY)
            _LOGGER.debug("    ├── Current Humidity Value: %s", humidity)  # 현재 습도 값 로그 출력
            return humidity

        if self.entity_description.key == SENSOR_TARGET_HUMIDITY:
            target_humidity = state.get(ATTR_TARGET_HUMIDITY)
            _LOGGER.debug("    ├── Target Humidity Value: %s", target_humidity)  # 목표 습도 값 로그 출력
            return target_humidity

        _LOGGER.error("    └── Unhandled sensor '%s' encountered", self.entity_description.key)
        return None

