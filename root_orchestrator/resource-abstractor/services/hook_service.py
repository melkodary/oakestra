import threading

from db import hooks_db
from requests import exceptions, post


def call_webhook(hook, data):
    try:
        response = post(hook["webhook_url"], json=data)
        response.raise_for_status()
        data = response.json()
    except exceptions.RequestException:
        print(f"Failed to send request to {hook['webhook_url']}")

    # if request fails the original data is returned
    return data


def process_async_hook(entity_id, entity_name, event):
    async_hooks = hooks_db.find_hooks({"entity": entity_name, "async_events": {"$in": [event]}})

    for hook in async_hooks:
        body = {
            "entity": entity_name,
            "entity_id": entity_id,
            "event": event,
        }
        threading.Thread(target=call_webhook, args=(hook["webhook_url"], body)).start()


def after_create(entity_id, entity_name):
    process_async_hook(entity_id, entity_name, hooks_db.HookEventsEnum.AFTER_CREATE.value)


def after_update(entity_id, entity_name):
    process_async_hook(entity_id, entity_name, hooks_db.HookEventsEnum.AFTER_UPDATE.value)


def after_delete(entity_id, entity_name):
    process_async_hook(entity_id, entity_name, hooks_db.HookEventsEnum.AFTER_DELETE.value)


def process_sync_hook(data, entity_name, event):
    sync_hooks = hooks_db.find_hooks({"entity": entity_name, "sync_events": {"$in": [event]}})

    for hook in sync_hooks:
        data = call_webhook(hook, data)

    return data


def before_create(data, entity_name):
    return process_sync_hook(data, entity_name, hooks_db.HookEventsEnum.BEFORE_CREATE.value)


def before_update(data, entity_name):
    return process_sync_hook(data, entity_name, hooks_db.HookEventsEnum.BEFORE_UPDATE.value)


def before_delete(data, entity_name):
    return process_sync_hook(data, entity_name, hooks_db.HookEventsEnum.BEFORE_DELETE.value)
