import logging
import os
import threading

from db import hooks_db
from requests import exceptions, post

RESPONSE_TIMEOUT = os.environ.get("HOOK_REQUEST_TIMEOUT", 5)
CONNECT_TIMEOUT = os.environ.get("HOOK_CONNECT_TIMEOUT", 10)


def call_webhook(url, data):
    try:
        response = post(url, json=data, timeout=(CONNECT_TIMEOUT, RESPONSE_TIMEOUT))
        response.raise_for_status()
        data = response.json()
    except exceptions.ConnectTimeout:
        logging.warning(f"Request timed out while trying to connect to {url}")
    except exceptions.ReadTimeout:
        logging.warning(f"{url} failed to return response in the allotted amount of time")
    except exceptions.RequestException:
        logging.warning(f"Hook failed to send request to {url}")

    # if request fails the original data is returned
    return data


def process_async_hook(entity_name, event, entity_id):
    async_hooks = hooks_db.find_hooks({"entity": entity_name, "async_events": {"$in": [event]}})

    for hook in async_hooks:
        data = {
            "entity": entity_name,
            "entity_id": entity_id,
            "event": event,
        }
        threading.Thread(target=call_webhook, args=(hook["webhook_url"], data)).start()


def after_create(entity_name, entity_id):
    process_async_hook(entity_name, hooks_db.HookEventsEnum.AFTER_CREATE.value, entity_id)


def after_update(entity_name, entity_id):
    process_async_hook(entity_id, entity_name, hooks_db.HookEventsEnum.AFTER_UPDATE.value)


def after_delete(entity_name, entity_id):
    process_async_hook(entity_id, entity_name, hooks_db.HookEventsEnum.AFTER_DELETE.value)


def process_sync_hook(entity_name, event, data):
    sync_hooks = hooks_db.find_hooks({"entity": entity_name, "sync_events": {"$in": [event]}})

    for hook in sync_hooks:
        data = call_webhook(hook, data)

    return data


def before_create(entity_name, data):
    return process_sync_hook(entity_name, hooks_db.HookEventsEnum.BEFORE_CREATE.value, data)


def before_update(entity_name, entity_id, data):
    data["_id"] = entity_id
    return process_sync_hook(entity_name, hooks_db.HookEventsEnum.BEFORE_UPDATE.value, data)
