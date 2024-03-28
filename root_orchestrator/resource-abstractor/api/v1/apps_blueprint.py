import json

from db import jobs_db as apps_db
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields
from services import hook_service

applicationsblp = Blueprint(
    "Applications operations",
    "applications",
    url_prefix="/api/v1/applications",
    description="Operations on applications",
)


class ApplicationFilterSchema(Schema):
    application_name = fields.String()
    application_namespace = fields.String()
    userId = fields.String()


@applicationsblp.route("/")
class ApplicationsController(MethodView):
    @applicationsblp.arguments(ApplicationFilterSchema, location="query")
    def get(self, query={}):
        return json.dumps(list(apps_db.find_apps(query)), default=str)

    @hook_service.before_create_hook("application")
    @hook_service.after_create_hook("application")
    def post(self, data, *args, **kwargs):
        result = apps_db.create_app(data)

        return json.dumps(result, default=str)


@applicationsblp.route("/<app_id>")
class ApplicationController(MethodView):
    @applicationsblp.arguments(ApplicationFilterSchema, location="query")
    def get(self, query, **kwargs):
        app_id = kwargs.get("appId")

        return json.dumps(apps_db.find_app_by_id(app_id, query), default=str)

    @hook_service.after_delete_hook("application")
    def delete(self, app_id, *args, **kwargs):
        result = apps_db.delete_app(app_id)

        return json.dumps(result, default=str)

    @hook_service.before_update_hook("application")
    @hook_service.after_update_hook("application")
    def patch(self, app_id, data, *args, **kwargs):
        result = apps_db.update_app(app_id, data)

        return json.dumps(result, default=str)
