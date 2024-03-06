from services.hook_service import hook_service


def perform_create(fn, data, *args, **kwargs):
    entity_name = kwargs.get("entity")
    data = hook_service.before_create(data, entity_name)
    response = fn(data, *args, **kwargs)
    obj_id = str(response.get("_id"))
    hook_service.after_create(obj_id, entity_name)

    return response


def perform_update(fn, entity_id, data, *args, **kwargs):
    entity_name = kwargs.get("entity")
    data = hook_service.after_create(entity_id, entity_name)
    response = fn(entity_id, data, *args, **kwargs)
    obj_id = str(response.get("_id"))
    hook_service.after_create(obj_id, entity_name)

    return response


def perform_delete(fn, entity_id, *args, **kwargs):
    entity_name = kwargs.get("entity")
    # TODO: need further discussion on what kind of decisions another service could have
    # before deleting an entity.
    # data = hook_service.before_delete(data, entity)
    response = fn(entity_id, *args, **kwargs)
    obj_id = str(response.get("_id"))
    hook_service.after_delete(obj_id, entity_name)

    return response
