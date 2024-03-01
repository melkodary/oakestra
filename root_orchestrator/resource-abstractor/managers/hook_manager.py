from db import hooks_db
from requests import exceptions, post


def before_create_decorator(func):
    def wrapper(data, type):
        data = beforeObjectCreation(data, type)
        return func(data, type)

    return wrapper


def beforeObjectCreation(data, type):
    hooks = hooks_db.mongo_get_hooks({"entity": type, "events": "beforeCreate"})
    for hook in hooks:
        try:
            response = post(hook["webhook_url"], json=data)
            data = response.json()
        except exceptions.RequestException:
            # TODO log the issue
            pass

    return data
