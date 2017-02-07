import io
import os
import zipfile

import gc3libs
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from gc3libs.session import Session
from gc3utils.commands import cmd_gsession
from horizon import tables
from openstack_dashboard import api

from executor.content.executordashboard.executorpanel.utils import inject_nova_client_auth_params


def get_auth_params_from_request(request):
    """Extracts the properties from the request object needed by the novaclient
    call below. These will be used to memoize the calls to novaclient
    """
    return (
        request.user.username,
        request.user.token.id,
        request.user.tenant_id,
        api.base.url_for(request, 'compute'),
        api.base.url_for(request, 'identity')
    )


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


class DeleteJobAction(tables.Action):
    name = "Delete Job"

    def handle(self, data_table, request, object_ids):
        auth_params = get_auth_params_from_request(request)
        inject_nova_client_auth_params(auth_params)
        os.environ["GC3PIE_CONF"] = settings.GC3PIE_CONF
        os.environ["OS_AUTH_URL"] = settings.OS_AUTH_URL
        gsession = cmd_gsession()
        gsession._core = gc3libs.core.Core(gsession._make_config())
        basePath = "{}/{}".format(settings.JOBS_BASE_PATH, request.user.username)
        os.chdir(basePath)
        for jobPath in os.listdir(basePath):
            gsession.params.session = jobPath
            gsession.session = Session(jobPath, create=False)
            for task_key in gsession.session.tasks:
                if gsession.session.tasks[task_key].persistent_id in object_ids:
                    gsession.delete_session()
        return redirect(reverse('horizon:executordashboard:executorpanel:index'))


class KillJobAction(tables.Action):
    name = "Kill Job"

    def handle(self, data_table, request, object_ids):
        auth_params = get_auth_params_from_request(request)
        inject_nova_client_auth_params(auth_params)
        os.environ["GC3PIE_CONF"] = settings.GC3PIE_CONF
        os.environ["OS_AUTH_URL"] = settings.OS_AUTH_URL
        gsession = cmd_gsession()
        gsession._core = gc3libs.core.Core(gsession._make_config())
        basePath = "{}/{}".format(settings.JOBS_BASE_PATH, request.user.username)
        os.chdir(basePath)
        for jobPath in os.listdir(basePath):
            gsession.params.session = jobPath
            gsession.session = Session(jobPath, create=False)
            for task_key in gsession.session.tasks:
                if gsession.session.tasks[task_key].persistent_id in object_ids:
                    gsession.abort_session()
        return redirect(reverse('horizon:executordashboard:executorpanel:index'))


class DownloadOutputJobAction(tables.Action):
    name = "Output Download"

    def handle(self, data_table, request, object_ids):
        zip_io = io.BytesIO()
        auth_params = get_auth_params_from_request(request)
        inject_nova_client_auth_params(auth_params)
        os.environ["GC3PIE_CONF"] = settings.GC3PIE_CONF
        os.environ["OS_AUTH_URL"] = settings.OS_AUTH_URL
        gsession = cmd_gsession()
        gsession._core = gc3libs.core.Core(gsession._make_config())
        basePath = "{}/{}".format(settings.JOBS_BASE_PATH, request.user.username)
        os.chdir(basePath)
        for jobPath in os.listdir(basePath):
            gsession.params.session = jobPath
            gsession.session = Session(jobPath, create=False)
            for task_key in gsession.session.tasks:
                if gsession.session.tasks[task_key].persistent_id in object_ids:
                    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
                        zipdir(gsession.session.tasks[task_key].output_dir,
                               backup_zip)  # u can also make use of list of filename location
                        # and do some iteration over it
        response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=%s' % 'output' + ".zip"
        response['Content-Length'] = zip_io.tell()
        return response


class JobRow(tables.Row):
    # this method is also used for automatic update of the row
    ajax = True

    @property
    def status(self):
        return True if "TERMINATED" in self.cells['status'].datum['status'] else None

    def get_data(self, request, job_id):
        # Add data to the context here...
        auth_params = get_auth_params_from_request(request)
        # runGC3PieTask.delay(auth_params)
        inject_nova_client_auth_params(auth_params)
        gsession = cmd_gsession()
        defaultPath = os.getcwd()

        basePath = "{}/{}".format(settings.JOBS_BASE_PATH, request.user.username)
        try:
            os.makedirs(basePath)
        except:
            pass
        os.chdir(basePath)

        for jobPath in os.listdir(basePath):
            gsession.params.session = jobPath
            gsession.session = Session(jobPath, create=False)

            for task_key in gsession.session.tasks:

                if job_id == gsession.session.tasks[task_key].persistent_id:
                    os.chdir(defaultPath)
                    return {
                        "id": gsession.session.tasks[task_key].persistent_id,
                        "jobname": gsession.session.tasks[task_key].jobname,
                        "status": gsession.session.tasks[task_key].execution.info
                    }
        return {}


class JobsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_("ID"))
    name = tables.Column('jobname', verbose_name=_("Job Name"))
    status = tables.Column('status', status=True,
                           verbose_name=_("Status"))


    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = "jobs"
        verbose_name = _("Jobs")
        row_actions = (DownloadOutputJobAction, KillJobAction, DeleteJobAction)
        row_class = JobRow
        status_columns = ['status']
