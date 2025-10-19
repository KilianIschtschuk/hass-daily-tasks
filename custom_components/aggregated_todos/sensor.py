from homeassistant.components.sensor import SensorEntity
from datetime import date
DOMAIN = "aggregated_todos"

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([AggregatedTodosSensor(hass)], True)

class AggregatedTodosSensor(SensorEntity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "Todos Due Today"
        self._attr_unique_id = "todos_due_today"
        self._attr_extra_state_attributes = {}
        self._attr_native_value = 0

    async def async_update(self):
        all_todos = [e for e in self.hass.states.async_all() if e.entity_id.startswith("todo.")]
        today_str = str(date.today())
        due_today = []
        for todo in all_todos:
            items = todo.attributes.get("items", [])
            for item in items:
                if item.get("status") == "needs_action" and item.get("due") == today_str:
                    due_today.append(item["summary"])
        self._attr_extra_state_attributes = {"tasks": due_today}
        self._attr_native_value = len(due_today)
