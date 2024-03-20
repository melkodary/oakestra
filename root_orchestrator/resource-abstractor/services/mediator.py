from services import hook_service


def perform_create(fn, data, entity_name):
    data = hook_service.before_create(data, entity_name)
    response = fn(data)
    obj_id = str(response.get("_id"))
    hook_service.after_create(obj_id, entity_name)

    return response


def perform_update(fn, entity_id, data, entity_name):
    data = {**data, "_id": entity_id}
    data = hook_service.before_update(data, entity_name)

    data.pop("_id")
    response = fn(entity_id, data)

    obj_id = str(response.get("_id"))
    hook_service.after_update(obj_id, entity_name)

    return response


def perform_delete(fn, entity_id, entity_name):
    # TODO: need further discussion on what kind of decisions another service could have
    # before deleting an entity.
    # data = hook_service.before_delete(data, entity)
    response = fn(entity_id)
    obj_id = str(response.get("_id"))
    hook_service.after_delete(obj_id, entity_name)

    return response
