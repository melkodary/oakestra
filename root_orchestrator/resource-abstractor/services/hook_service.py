import json
import logging
import os
import threading
from functools import wraps

from db import hooks_db
from flask import request
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
    async_hooks = hooks_db.find_hooks({"entity": entity_name, "events": {"$in": [event]}})

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
    sync_hooks = hooks_db.find_hooks({"entity": entity_name, "events": {"$in": [event]}})

    for hook in sync_hooks:
        data = call_webhook(hook["webhook_url"], data)

    return data


def before_create(entity_name, data):
    return process_sync_hook(entity_name, hooks_db.HookEventsEnum.BEFORE_CREATE.value, data)


def before_update(entity_name, data):
    return process_sync_hook(entity_name, hooks_db.HookEventsEnum.BEFORE_UPDATE.value, data)


def perform_create(entity_name, fn, *args):
    data = args[-1]
    data = before_create(entity_name, data)

    args = list(args)
    args[-1] = data

    result = fn(*tuple(args))
    after_create(entity_name, str(result.get("_id")))

    return result


def perform_update(entity_name, fn, *args):
    data = args[-1]
    data = before_update(entity_name, data)

    # Update the last argument with the new data
    args = list(args)
    args[-1] = data

    result = fn(*tuple(args))
    after_update(entity_name, str(result.get("_id")))

    return result


# put currently is not supported
api_hooks_map = {
    "post": (before_create, after_create),
    "patch": (before_update, after_update),
    "delete": (None, after_delete),
}


# doesn't work well with @arguments decorator
# this decorator has to be the closest to the method
def before_after_hook(entity_name, with_param_id=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            method_name = fn.__name__
            if method_name not in api_hooks_map.keys():
                raise ValueError(f"Method {method_name} not supported")

            # incase this was wrapped by @arguments
            data = args[1] if len(args) > 1 else request.json

            before_fn = api_hooks_map[method_name][0]
            after_fn = api_hooks_map[method_name][1]

            entity_id = kwargs.get(with_param_id) if with_param_id else None

            if before_fn:
                if entity_id:
                    data["_id"] = entity_id

                data = before_fn(entity_name, data)

            args = list(args)
            if data and len(args) > 1:
                args[1] = data
            elif data:
                args.append(data)

            result = fn(*tuple(args), **kwargs)
            result_id = result["_id"] if isinstance(result, dict) else None

            if result_id is None:
                try:
                    result_id = json.loads(result).get("_id")
                except json.JSONDecodeError:
                    pass

            after_fn(entity_name, result_id)

            return result

        return wrapper

    return decorator
