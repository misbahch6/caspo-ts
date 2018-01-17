
from __future__ import print_function

import sys

def dbg(msg):
    print(msg, file=sys.stderr)

def warning(msg):
    print("WARNING: %s" % msg, file=sys.stderr)

