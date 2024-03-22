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


def perform_delete(entity_name, fn, *args):
    # TODO: need further discussion on what kind of decisions another service could have
    # before deleting an entity.
    # data = hook_service.before_delete(data, entity)
    result = fn(*args)
    hook_service.after_delete(entity_name, str(result.get("_id")))

    return result
