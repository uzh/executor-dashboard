CELERY_BROKER_URL = "redis://redis:6379/0"

GC3PIE_CONF = "/home/docker/code/gc3pie.conf"

JOBS_BASE_PATH = "/home/docker/persistent/gc3pie"
INPUT_BASE_PATH = "/home/docker/persistent/gc3input"
OUTPUT_BASE_PATH = "/home/docker/persistent/gc3output"

IGNORE_PARAMS = ['-s', '-l', '-o', '-r', '-v', '-u', '-l', '-N', '-C']

OS_AUTH_URL="https://cloud.s3it.uzh.ch:5000/v2.0"


OPENSTACK_HOST = "cloud.s3it.uzh.ch"
OPENSTACK_KEYSTONE_URL = "https://%s:5000/v2.0" % OPENSTACK_HOST
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "_member_"

ALLOWED_HOSTS = '*'
USE_SSL = False