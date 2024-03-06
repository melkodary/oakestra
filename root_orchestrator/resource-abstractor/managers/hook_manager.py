from db import hooks_db
from requests import exceptions, post


def before_create_decorator(func):
    def wrapper(data, type):
        data = hook_before_creation(data, type)
        return func(data, type)

    return wrapper


def hook_before_creation(data, type):
    hooks = hooks_db.find_hooks(
        {"entity": type, "events": {"$in": [hooks_db.HookEventsEnum.BEFORE_CREATE]}}
    )
    for hook in hooks:
        try:
            response = post(hook["webhook_url"], json=data)
            data = response.json()
        except exceptions.RequestException:
            # TODO log the issue
            pass

    return data
