from homeassistant.helpers.entity import Entity
from datetime import datetime

DOMAIN = "aggregated_todos"

async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([AggregatedTodosSensor(hass)], True)

class AggregatedTodosSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._state = 0
        self._tasks = []

    @property
    def name(self):
        return "Todos Due Today"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {"tasks": self._tasks}

    async def async_update(self):
        today = datetime.now().date().isoformat()
        todos = [e for e in self.hass.states.all() if e.entity_id.startswith("todo.")]
        due_today = []
        for todo in todos:
            items = todo.attributes.get("items", [])
            for item in items:
                if item.get("status") == "needs_action" and item.get("due") == today:
                    due_today.append(item["summary"])
        self._tasks = due_today
        self._state = len(due_today)

