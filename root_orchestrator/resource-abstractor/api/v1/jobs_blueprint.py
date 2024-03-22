import json

from bson.objectid import ObjectId
from db import jobs_db
from db.jobs_helper import build_filter
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields
from services import mediator
from werkzeug import exceptions

jobsblp = Blueprint("Jobs Api", "jobs_api", url_prefix="/api/v1/jobs")


class JobFilterSchema(Schema):
    instance_number = fields.Integer()


@jobsblp.route("/")
class AllJobsController(MethodView):
    def get(self):
        return json.dumps(list(jobs_db.find_jobs()), default=str)

    def post(self, *args, **kwargs):
        data = request.json
        return json.dumps(mediator.perform_create("job", jobs_db.create_job, data), default=str)

    def put(self, *args, **kwargs):
        job_data = request.json
        job_name = job_data.get("job_name")
        job = jobs_db.find_job_by_name(job_name)

        res = None
        if job:
            res = mediator.perform_update("job", jobs_db.update_job, str(job.get("_id")), job_data)
        else:
            res = mediator.perform_create("job", jobs_db.create_job, job_data)

        return json.dumps(res, default=str)


@jobsblp.route("/<jobId>")
class JobController(MethodView):
    @jobsblp.arguments(JobFilterSchema, location="query")
    def get(self, query, **kwargs):
        job_id = kwargs.get("jobId")
        if ObjectId.is_valid(job_id) is False:
            raise exceptions.BadRequest()

        filter = build_filter(query)
        job = jobs_db.find_job_by_id(job_id, filter)
        if job is None:
            raise exceptions.NotFound()

        return json.dumps(job, default=str)

    def patch(self, *args, **kwargs):
        data = request.json
        job_id = kwargs.get("jobId")

        if ObjectId.is_valid(job_id) is False:
            raise exceptions.BadRequest()

        data["_id"] = job_id
        return json.dumps(
            mediator.perform_update("job", jobs_db.update_job, job_id, data),
            default=str,
        )

    def delete(self, *args, **kwargs):
        job_id = kwargs.get("jobId")
        if ObjectId.is_valid(job_id) is False:
            raise exceptions.BadRequest()

        return json.dumps(mediator.perform_delete("job", jobs_db.delete_job, job_id), default=str)


@jobsblp.route("/<jobId>/<instanceId>")
class JobInstanceController(MethodView):
    def patch(self, *args, **kwargs):
        data = request.json
        job_id = kwargs.get("jobId")
        instance_id = kwargs.get("instanceId")
        if ObjectId.is_valid(job_id) is False:
            raise exceptions.BadRequest()

        return json.dumps(
            mediator.perform_update("job", jobs_db.update_job_instance, job_id, instance_id, data),
            default=str,
        )
