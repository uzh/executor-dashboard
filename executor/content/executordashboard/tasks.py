# Create your tasks here
from __future__ import absolute_import, unicode_literals

import os
import sys
import uuid
import zipfile

from celery import shared_task
from gc3libs.config import Configuration

from openstack_dashboard import settings
from openstack_dashboard.dashboards.executordashboard import gndn
from openstack_dashboard.dashboards.executordashboard.executorpanel.utils import inject_nova_client_auth_params

IGNORE_PARAMS = ['-s', '-l', '-o']


@shared_task
def runGC3PieTask(auth_params, script_params, input_files):
    inject_nova_client_auth_params(auth_params)

    defaultPath = os.getcwd()
    defaultArgv = sys.argv
    try:
        os.makedirs(settings.JOBS_BASE_PATH)
    except:
        pass
    os.chdir(settings.JOBS_BASE_PATH)
    script = gndn.GndnScript()
    payload = {}
    for key, action in script.actions.items():
        if action.option_strings[0] not in IGNORE_PARAMS and key in script_params and len(script_params[key]) > 0:
            payload[action.option_strings[0]] = script_params[key]
            # payload[key] = action.__dict__
            # if isinstance(action, _StoreAction):
            #     payload[key]["type"] = "text"
            # elif isinstance(action, _CountAction):
            #     payload[key]["type"] = "number"
            # else:
            #     payload[key]["type"] = "bool"
            # if type(payload[key]['const']) is str:
            #     payload[key]['const'] = payload[key]['const'].split(',')
            # else:
            #     payload[key]['const'] = None

    sessionName = '{}'.format(uuid.uuid4())
    sys.argv = [sessionName]
    for key, param in payload.items():
        sys.argv.append(key)
        sys.argv.append(param)
    sys.argv.append("-o")
    sys.argv.append("{}/NAME".format(settings.OUTPUT_BASE_PATH))
    for file in input_files:
        if file.lower().endswith('zip'):
            directory_path = "{}/{}".format(settings.INPUT_BASE_PATH, uuid.uuid4())
            zip_ref = zipfile.ZipFile(file, 'r')
            zip_ref.extractall(directory_path)
            zip_ref.close()
            sys.argv.append(directory_path)
        else:
            sys.argv.append(file)
    print " ".join(sys.argv)
    script = gndn.GndnScript()

    script.config = Configuration("/Users/ale/.gc3/gc3pie.conf")
    os.environ["OS_AUTH_URL"] = "https://cloud.s3it.uzh.ch:5000/v2.0"

    print "starting script"
    try:
        script.run()
    except SystemExit:
        print "exit called"

    sys.argv = defaultArgv
    os.chdir(defaultPath)
    print "script finished"
