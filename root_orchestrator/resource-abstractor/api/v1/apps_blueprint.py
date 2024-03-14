import json

from db import jobs_db as apps_db
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields
from services import mediator

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

    def post(self, *args, **kwargs):
        data = request.get_json()
        return json.dumps(
            mediator.perform_create(apps_db.create_app, data, entity="application"), default=str
        )


@applicationsblp.route("/<appId>")
class ApplicationController(MethodView):
    @applicationsblp.arguments(ApplicationFilterSchema, location="query")
    def get(self, query, **kwargs):
        app_id = kwargs.get("appId")
        return json.dumps(apps_db.find_app_by_id(app_id, query), default=str)

    def delete(self, appId, *args, **kwargs):
        return json.dumps(
            mediator.perform_delete(apps_db.delete_app(appId), entity="application"), default=str
        )

    def patch(self, appId, *args, **kwargs):
        data = request.get_json()
        return json.dumps(
            mediator.perform_update(apps_db.update_app, appId, data, entity="application"),
            default=str,
        )
