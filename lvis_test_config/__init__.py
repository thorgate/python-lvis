import os
import sys

try:
    from .local import *
except ImportError:
    PROXY_HOST_URL = os.environ.get('PROXY_HOST_URL')
    TESTING_RANGE = os.environ.get('TESTING_RANGE', True)
    TEST_CERTIFICATE_PATH = os.environ.get('TEST_CERTIFICATE_PATH')
    TEST_CERTIFICATE_PERSON_CODE = os.environ.get('TEST_CERTIFICATE_PERSON_CODE')
    TEST_CERTIFICATE_PASSWORD = os.environ.get('TEST_CERTIFICATE_PASSWORD')
    if None in (PROXY_HOST_URL, TEST_CERTIFICATE_PATH, TEST_CERTIFICATE_PERSON_CODE, TEST_CERTIFICATE_PASSWORD):
        sys.stderr.write("Couldn't import lvis_test_config.local or ENV var not set, have you created it from lvis_test_config/local.py.example?\n")
        sys.exit(1)
