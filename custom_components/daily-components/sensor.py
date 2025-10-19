"""
A sensor that finds all tasks from all To-do lists that are due today.
"""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.util import dt as dt_util

# Since the `todo` component is a dependency, these should be available.
# We add a fallback just in case of timing issues during startup.
try:
    from homeassistant.components.todo import TodoEntity, TodoItemStatus
except ImportError:
    # Handle cases where `todo` might not be fully loaded.
    TodoEntity = None
    TodoItemStatus = None


_LOGGER = logging.getLogger(__name__)

DOMAIN = "daily_tasks"
DEFAULT_NAME = "Tasks Due Today"
SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Daily Tasks sensor platform."""
    if TodoEntity is None:
        _LOGGER.error("Could not import TodoEntity. Is the 'todo' integration enabled?")
        return

    name = config.get(CONF_NAME, DEFAULT_NAME)
    sensor = DailyTasksSensor(hass, name)
    async_add_entities([sensor], True)


class DailyTasksSensor(SensorEntity):
    """Representation of a sensor that counts tasks due today."""

    def __init__(self, hass: HomeAssistant, name: str) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._attr_name = name
        # Create a unique ID based on the sensor's name
        self._attr_unique_id = f"daily_tasks_{name.lower().replace(' ', '_')}"
        self._attr_icon = "mdi:calendar-check"
        self._tasks = []

    @property
    def native_value(self) -> int:
        """Return the state of the sensor (the count of tasks)."""
        return len(self._tasks)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes of the sensor."""
        return {"tasks": self._tasks}

    async def async_update(self) -> None:
        """Fetch new state data for the sensor by polling todo entities."""
        today = dt_util.now().date()
        tasks_due_today = []

        todo_component = self.hass.data.get("todo")
        if not todo_component:
            _LOGGER.debug("Todo component not yet loaded.")
            return

        for entity in todo_component.entities:
            if not isinstance(entity, TodoEntity):
                continue

            if not hasattr(entity, "todo_items") or entity.todo_items is None:
                continue

            list_name = entity.name
            try:
                items = entity.todo_items
                for item in items:
                    # Check for items that are not completed and have a due date
                    if item.due and item.status == TodoItemStatus.NEEDS_ACTION:
                        due_date = item.due
                        # Convert datetime to date for comparison if necessary
                        if isinstance(due_date, dt_util.datetime):
                            due_date = due_date.date()

                        if due_date == today:
                            tasks_due_today.append(
                                {
                                    "list": list_name,
                                    "task": item.summary,
                                    "due": item.due.isoformat(),
                                    "description": item.description,
                                }
                            )
            except Exception as e:
                _LOGGER.error(f"Error processing todo list '{list_name}': {e}")

        # Sort tasks by list name and then by summary
        self._tasks = sorted(tasks_due_today, key=lambda t: (t['list'], t['task']))

