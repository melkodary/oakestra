from functools import wraps

from flask import request
from services import hook_service

event_map = {
    "create": (hook_service.before_create, hook_service.after_create),
    "update": (hook_service.before_update, hook_service.after_update),
    "delete": (None, hook_service.after_delete),
}


# doesn't work well with @arguments decorator
def before_after_hook(event, entity_name, with_param_id=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.json

            before_fn = event_map[event][0]
            after_fn = event_map[event][1]

            entity_id = kwargs.get(with_param_id) if with_param_id else None

            if before_fn:
                if entity_id:
                    data = before_fn(entity_name, entity_id, data)
                else:
                    data = before_fn(entity_name, data)

            args = list(args)
            if entity_id:
                args.append(entity_id)

            if data:
                args.append(data)

            result = fn(*tuple(args), **kwargs)

            after_fn(entity_name, result["_id"])

            return result

        return wrapper

    return decorator
