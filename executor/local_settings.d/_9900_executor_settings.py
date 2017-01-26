CELERY_BROKER_URL = "redis://localhost:6379/0"

JOBS_BASE_PATH = "/tmp/gc3pie"
INPUT_BASE_PATH = "/tmp/gc3input"
OUTPUT_BASE_PATH = "/tmp/gc3output"

IGNORE_PARAMS = ['-s', '-l', '-o', '-r', '-v', '-u', '-l', '-N', '-C']

GC3PIE_CONF = "~/.gc3/gc3pie.conf"

OS_AUTH_URL="https://cloud.s3it.uzh.ch:5000/v2.0"
