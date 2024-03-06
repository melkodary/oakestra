from db import hooks_db
from mqtt.mqtt_client import HOOKS_TOPIC, MqttClient
from requests import exceptions, post


class HookService:
    def __init__(self):
        self.mqtt_client = MqttClient()
        self.mqtt_client.connect()

    def process_async_hook(self, entity_id, entity_name, event):
        async_hooks = hooks_db.find_hooks({"entity": entity_name, "async_events": {"$in": [event]}})

        for hook in async_hooks:
            # TODO: check response of publishing
            self.mqtt_client.publish_message(
                HOOKS_TOPIC,
                {
                    "entity": entity_name,
                    "entity_id": entity_id,
                    "event": event.value,
                },
            )

    def after_create(self, entity_id, entity_name):
        self.process_async_hook(entity_id, entity_name, hooks_db.HookEventsEnum.AFTER_CREATE)

    def after_update(self, entity_id, entity_name):
        self.process_async_hook(entity_id, entity_name, hooks_db.HookEventsEnum.AFTER_UPDATE)

    def after_delete(self, entity_id, entity_name):
        self.process_async_hook(entity_id, entity_name, hooks_db.HookEventsEnum.AFTER_DELETE)

    def process_sync_hook(self, data, entity_name, event):
        sync_hooks = hooks_db.find_hooks({"entity": entity_name, "sync_events": {"$in": [event]}})

        for hook in sync_hooks:
            try:
                response = post(hook["webhook_url"], json={**data, "event": event.value})
                data = response.json()
            except exceptions.RequestException:
                print(f"Failed to send request to {hook['webhook_url']}")
                continue

        return data

    def before_create(self, data, entity_name):
        return self.process_sync_hook(data, entity_name, hooks_db.HookEventsEnum.BEFORE_CREATE)

    def before_update(self, data, entity_name):
        return self.process_sync_hook(data, entity_name, hooks_db.HookEventsEnum.BEFORE_UPDATE)

    def before_delete(self, data, entity_name):
        return self.process_sync_hook(data, entity_name, hooks_db.HookEventsEnum.BEFORE_DELETE)


hook_service = HookService()
