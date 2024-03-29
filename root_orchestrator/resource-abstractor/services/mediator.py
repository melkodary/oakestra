from services import hook_service


def perform_create(entity_name, fn, *args):
    data = args[-1]
    data = hook_service.before_create(entity_name, data)

    args[-1] = (data,)

    result = fn(*args)
    hook_service.after_create(entity_name, str(result.get("_id")))

    return result


def perform_update(entity_name, fn, *args):
    data = args[-1]
    data = hook_service.before_update(entity_name, data)

    # Update the last argument with the new data
    args[-1] = (data,)

    result = fn(*args)
    hook_service.after_update(entity_name, str(result.get("_id")))

    return result
