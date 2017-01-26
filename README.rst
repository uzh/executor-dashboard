executor plugin for horizon
===========================
This plugin was created at the University of Zurich and aims at simplifying the interaction with the gc3pie utilities.
The UI offered by this plugin is integrated seamlessly in your openstack horizon installation and will pass over your
authentication token to gc3pie. The user does not need to enter any additional credentials. The dependencies required by
this plugin are the ones horizon implies + celery for launching the tasks asynchronously.

packaging the plugin
--------------------
This step is only relevant if you want to compile the package from source, if you already have a packaged version of the
plugin you can skip this and go directly to the installing section.

1. check out the sources
2. cd in the project (where setup.py is)
3. python setup.py sdist

Step 3 will create the plugin's package in dist/executor-0.0.0.tar.gz

installing the plugin
---------------------
To install the plugin first make sure you have the right virtual environment activated. Then simply install it with:

pip install dist/executor-0.0.0.tar.gz

activating the plugin in horizon
--------------------------------
open your horizon installation and create the followin file: "openstack_dashboard/local/enabled/_31050_executordashboard.py".
Enter the following content in that file:

.. code-block::python
    # The name of the dashboard to be added to HORIZON['dashboards']. Required.
    DASHBOARD = 'executordashboard'

    # If set to True, this dashboard will not be added to the settings.
    DISABLED = False

    # A list of applications to be added to INSTALLED_APPS.
    ADD_INSTALLED_APPS = [
        'executor.content.executordashboard',
    ]

This will activate the freshly installed dashboard.

configuring the plugin
----------------------
open your horizon installation and create the followin file: "openstack_dashboard/local/local_settings.d/_9900_executor_settings.py".
Enter the following content in that file:

.. code-block::python
    CELERY_BROKER_URL = "redis://localhost:6379/0"

    JOBS_BASE_PATH = "/tmp/gc3pie"
    INPUT_BASE_PATH = "/tmp/gc3input"
    OUTPUT_BASE_PATH = "/tmp/gc3output"

    IGNORE_PARAMS = ['-s', '-l', '-o', '-r', '-v', '-u', '-l', '-N', '-C']

    GC3PIE_CONF = "~/.gc3/gc3pie.conf"

    OS_AUTH_URL = "https://cloud.s3it.uzh.ch:5000/v2.0"

    OPENSTACK_HOST = "cloud.s3it.uzh.ch"
    OPENSTACK_KEYSTONE_URL = "https://%s:5000/v2.0" % OPENSTACK_HOST
    OPENSTACK_KEYSTONE_DEFAULT_ROLE = "_member_"

    ALLOWED_HOSTS = '*'
    USE_SSL = False

This will give the plugin every needed configuration for session, output and input storage. The celery config sets up the
broker.

taking the easy way out: Docker
-------------------------------
If you want to take the easy way and don't care about the installation steps just clone this repository and do a
"docker-compose up", this will install:
1. Redis
2. Web Application Container (nginx as the web server/load balancer)
3. Celery Application Container

All wired up and ready to consume at localhost:8000.

Note: Docker uses ssh keys that are in this repository. This is not secure for production deployments, please change the
keys under "docker/conf/id_rsa*".
