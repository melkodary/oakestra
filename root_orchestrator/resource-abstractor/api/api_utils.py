import json
from functools import wraps

from flask import request
from services import hook_service

# put currently is not supported
event_map = {
    "post": (hook_service.before_create, hook_service.after_create),
    "patch": (hook_service.before_update, hook_service.after_update),
    "delete": (None, hook_service.after_delete),
}


# doesn't work well with @arguments decorator
# this decorator has to be the closest to the method
def before_after_hook(entity_name, with_param_id=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            method_name = fn.__name__
            if method_name not in event_map.keys():
                raise ValueError(f"Method {method_name} not supported")

            # incase this was wrapped by @arguments
            data = args[1] if len(args) > 1 else request.json

            before_fn = event_map[method_name][0]
            after_fn = event_map[method_name][1]

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

            try:
                result_id = json.loads(result).get("_id")
            except json.JSONDecodeError:
                pass

            after_fn(entity_name, result_id)

            return result

        return wrapper

    return decorator
