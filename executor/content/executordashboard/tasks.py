# Create your tasks here
from __future__ import absolute_import, unicode_literals

import logging
import os
import sys
import uuid
import zipfile

import gc3libs
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from executor.content.executordashboard.gc3apps import grayscaler

gc3libs.log = get_task_logger('gc3pie')
gc3libs.log.setLevel(logging.DEBUG)

from executor.content.executordashboard.executorpanel.utils import inject_nova_client_auth_params


@shared_task
def runGC3PieTask(auth_params, script_params, input_files):
    username = auth_params[0]
    inject_nova_client_auth_params(auth_params)

    defaultPath = os.getcwd()
    defaultArgv = sys.argv
    basePath = "{}/{}".format(settings.JOBS_BASE_PATH, username)
    try:
        os.makedirs(basePath)
    except:
        pass
    os.chdir(basePath)
    script = grayscaler.GrayscaleScript()
    payload = {}
    for key, action in script.actions.items():
        if action.option_strings[0] not in settings.IGNORE_PARAMS and key in script_params and len(
                script_params[key]) > 0:
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
    sys.argv.append("-vvv")
    sys.argv.append("-C")
    sys.argv.append("30")
    sys.argv.append("-o")
    outputPath = "{}/{}".format(settings.OUTPUT_BASE_PATH, username)
    sys.argv.append("{}/NAME".format(outputPath))
    for file in input_files:
        if file.lower().endswith('zip'):
            directory_path = "{}/{}/{}".format(settings.INPUT_BASE_PATH, username, uuid.uuid4())
            zip_ref = zipfile.ZipFile(file, 'r')
            zip_ref.extractall(directory_path)
            zip_ref.close()
            sys.argv.append(directory_path)
        else:
            sys.argv.append(file)
    print " ".join(sys.argv)
    os.environ["GC3PIE_CONF"] = settings.GC3PIE_CONF
    os.environ["OS_AUTH_URL"] = settings.OS_AUTH_URL
    script = grayscaler.GrayscaleScript()

    print "starting script"
    try:
        def noop(*args, **kwargs):
            pass

        gc3libs.configure_logger = noop
        script.run()
    except SystemExit:
        print "exit called"

    sys.argv = defaultArgv
    os.chdir(defaultPath)
    print "script finished"
