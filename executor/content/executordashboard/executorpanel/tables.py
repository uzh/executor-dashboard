import io
import os
import zipfile

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from gc3libs.session import Session
from gc3utils.commands import cmd_gsession

from horizon import tables
from openstack_dashboard import api
from openstack_dashboard import settings
from openstack_dashboard.dashboards.executordashboard.executorpanel.utils import inject_nova_client_auth_params


class DeleteJobAction(tables.DeleteAction):
    def action_present(self, number):
        return "Delete"

    def action_past(self, number):
        return "Delete"

    def delete(self, request, obj_id):
        # Add data to the context here...
        auth_params = api.nova.get_auth_params_from_request(request)
        inject_nova_client_auth_params(auth_params)
        gsession = cmd_gsession()
        os.chdir(settings.JOBS_BASE_PATH)
        for jobPath in os.listdir(settings.JOBS_BASE_PATH):
            gsession.params.session = jobPath
            gsession.session = Session(jobPath, create=False)
            for task_key in gsession.session.tasks:
                if gsession.session.tasks[task_key].persistent_id == obj_id:
                    os.removedirs(jobPath)
        super(DeleteJobAction, self).delete(request, obj_id)


class DownloadOutputJobAction(tables.Action):
    name = "Output Download"

    def handle(self, data_table, request, object_ids):
        zip_io = io.BytesIO()
        auth_params = api.nova.get_auth_params_from_request(request)
        inject_nova_client_auth_params(auth_params)
        gsession = cmd_gsession()
        os.chdir(settings.JOBS_BASE_PATH)
        for jobPath in os.listdir(settings.JOBS_BASE_PATH):
            gsession.params.session = jobPath
            gsession.session = Session(jobPath, create=False)
            for task_key in gsession.session.tasks:
                if gsession.session.tasks[task_key].persistent_id in object_ids:
                    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
                        backup_zip.write("{}/run_{}".format(settings.OUTPUT_BASE_PATH,jobPath))  # u can also make use of list of filename location
                        # and do some iteration over it
        response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=%s' % 'output' + ".zip"
        response['Content-Length'] = zip_io.tell()
        return response


class JobsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_("ID"))
    name = tables.Column('jobname', verbose_name=_("Job Name"))
    status = tables.Column('status', verbose_name=_("Status"))

    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = "jobs"
        verbose_name = _("Jobs")
        table_actions = (DeleteJobAction,)
        row_actions = (DownloadOutputJobAction,)
