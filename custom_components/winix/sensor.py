"""Winix Dehumidifier Sensor."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import (
    ENTITY_ID_FORMAT,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import WinixConfigEntry, WINIX_DOMAIN
from .const import (
    ATTR_HUMIDITY,
    ATTR_TARGET_HUMIDITY,
    LOGGER,
    SENSOR_HUMIDITY,
    SENSOR_TARGET_HUMIDITY,
)
from .device_wrapper import WinixDeviceWrapper
from .manager import WinixEntity, WinixManager


SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
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
    entry: WinixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Winix dehumidifier sensors."""
    manager = entry.runtime_data

    entities = [
        WinixSensor(wrapper, manager, description)
        for description in SENSOR_DESCRIPTIONS
        for wrapper in manager.get_device_wrappers()
    ]
    async_add_entities(entities)
    LOGGER.info("Added %s sensors", len(entities))


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

        self._attr_unique_id = ENTITY_ID_FORMAT.format(
            f"{WINIX_DOMAIN}_{description.key.lower()}_{self._mac}"
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        state = self.device_wrapper.get_state()

        if state is None:
            return None

        if self.entity_description.key == SENSOR_HUMIDITY:
            return state.get(ATTR_HUMIDITY)

        if self.entity_description.key == SENSOR_TARGET_HUMIDITY:
            return state.get(ATTR_TARGET_HUMIDITY)

        return None
