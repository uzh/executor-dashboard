# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import os
import uuid

from cli._ext.argparse import _StoreAction, _CountAction
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from gc3libs.session import Session
from gc3utils.commands import cmd_gsession

from horizon import views, tables
from openstack_dashboard import api
from openstack_dashboard import settings

from executor.content.executordashboard.executorpanel.tables import JobsTable
from executor.content.executordashboard.executorpanel.utils import inject_nova_client_auth_params
from executor.content.executordashboard.gc3apps.gndn import GndnScript
from executor.content.executordashboard.tasks import runGC3PieTask
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


class ListView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'executordashboard/executorpanel/index.html'
    table_class = JobsTable

    def get_data(self):
        # SessionBasedScript
        return None  # Job.objects.all()


class IndexView(tables.DataTableView):
    template_name = 'executordashboard/executorpanel/index.html'
    # A very simple class-based view...
    table_class = JobsTable

    def get_data(self):
        # Add data to the context here...
        auth_params = get_auth_params_from_request(self.request)
        # runGC3PieTask.delay(auth_params)
        inject_nova_client_auth_params(auth_params)
        gsession = cmd_gsession()
        defaultPath = os.getcwd()
        try:
            os.makedirs(settings.JOBS_BASE_PATH)
        except:
            pass
        os.chdir(settings.JOBS_BASE_PATH)

        tasks = []
        for jobPath in os.listdir(settings.JOBS_BASE_PATH):
            gsession.params.session = jobPath
            gsession.session = Session(jobPath, create=False)
            for task_key in gsession.session.tasks:
                tasks.append({
                    "id": gsession.session.tasks[task_key].persistent_id,
                    "jobname": gsession.session.tasks[task_key].jobname,
                    "status": gsession.session.tasks[task_key].execution.info
                })
        os.chdir(defaultPath)
        return tasks


class CreateJobView(views.APIView):
    # A very simple class-based view...
    template_name = 'executordashboard/executorpanel/job_form.html'

    def get_data(self, request, context, *args, **kwargs):


        payload = {}
        for key, action in GndnScript().actions.items():
            if action.option_strings[0] not in settings.IGNORE_PARAMS:
                payload[key] = action.__dict__
                if isinstance(action, _StoreAction):
                    payload[key]["type"] = "text"
                elif isinstance(action, _CountAction):
                    payload[key]["type"] = "number"
                else:
                    payload[key]["type"] = "bool"
                if type(payload[key]['const']) is str:
                    payload[key]['const'] = payload[key]['const'].split(',')
                else:
                    payload[key]['const'] = None
        context["params"] = payload
        return context

    def post(self, request, *args, **kwargs):
        try:
            os.makedirs(settings.INPUT_BASE_PATH)
        except:
            pass
        paths = []
        for key, file in request.FILES.iteritems():
            filename, file_extension = os.path.splitext(file.name)
            file_path = "{}/{}{}".format(settings.INPUT_BASE_PATH, uuid.uuid4(), file_extension)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            paths.append(file_path)
        runGC3PieTask.delay(get_auth_params_from_request(request), request.POST, paths)
        return redirect(reverse('horizon:executordashboard:executorpanel:index'))
