from enum import Enum

from db import mongodb_client as db


class HookEventsEnum(Enum):
    AFTER_CREATE = "afterCreate"
    BEFORE_CREATE = "beforeCreate"

    AFTER_UPDATE = "afterUpdate"
    BEFORE_UPDATE = "beforeUpdate"

    AFTER_DELETE = "afterDelete"


def mongo_get_hooks(filter={}):
    return db.mongo_hooks.find(filter)


def mongo_get_hook_by_id(hook_id):
    hooks = mongo_get_hooks({"_id": hook_id})
    return hooks[0] if hooks else None


def mongo_create_hook(data):
    hook_name = data["hook_name"]

    return db.mongo_hooks.find_one_and_update(
        {"hook_name", hook_name}, data, upsert=True, return_document=True
    )


def mongo_delete_hook(hook_id):
    return db.mongo_hooks.delete_one({"_id": hook_id})
