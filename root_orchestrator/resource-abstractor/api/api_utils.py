from functools import wraps

from flask import request
from flask.views import MethodView
from services import hook_service


def before_create_hook(entity_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            data = hook_service.before_create(entity_name, data)

            args = list(args)
            args.append(data)

            return fn(*tuple(args), **kwargs)

        return wrapper

    return decorator


def after_create_hook(entity_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            hook_service.after_create(entity_name, result)

            return result

        return wrapper

    return decorator


def before_update_hook(entity_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(app_id, *args, **kwargs):
            data = request.get_json()
            data = hook_service.before_update(entity_name, app_id, data)

            args = list(args)
            args.append(app_id)
            args.append(data)

            return fn(*tuple(args), **kwargs)

        return wrapper

    return decorator


def after_update_hook(entity_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            hook_service.after_update(entity_name, str(result.get("_id")))

            return result

        return wrapper

    return decorator


def after_delete_hook(entity_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            hook_service.after_delete(entity_name, str(result.get("_id")))

            return result

        return wrapper

    return decorator
