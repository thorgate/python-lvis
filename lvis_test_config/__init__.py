import sys

try:
    from .local import *
except ImportError:
    sys.stderr.write("Couldn't import lvis_test_config.local, have you created it from lvis_test_config/local.py.example?\n")
    sys.exit(1)
