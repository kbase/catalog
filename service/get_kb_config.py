#!/usr/bin/env python
"""
SYNOPSIS

    get_kb_config.py [CFG_SECTION] [CFG_OPTION]

DESCRIPTION

    Get a KBase deployment config variable.  The config file location is set
    by the deployment config environment variable KB_DEPLOYMENT_CONFIG.  Useful
    for getting service configuration variables in Makefiles and server scripts.

AUTHOR

    Michael Sneddon <mwsneddon@lbl.gov>

LICENSE

   See LICENSE.md
"""

from __future__ import print_function

import os, sys, traceback
from ConfigParser import ConfigParser

DEPLOY_CFG = 'KB_DEPLOYMENT_CONFIG'

def usage():
    print('Usage: python get_kb_config.py [CFG_SECTION] [CFG_OPTION]')

def main ():
    if DEPLOY_CFG not in os.environ:
        print('Please define $'+DEPLOY_CFG+' environment variable to point to the kbase deployment.cfg or deploy.cfg file.')
        sys.exit(1)

    if len(sys.argv)<3:
        print('Not enough arguments.')
        usage()
        return

    if len(sys.argv)>3:
        print('Too many arguments.')
        usage()
        return

    try:
        config = ConfigParser()
        config.read(os.environ[DEPLOY_CFG])
    except Exception, e:
        print('Error reading config file.  Check environment variable $'+DEPLOY_CFG, file=sys.stderr)
        print(str(e))
        sys.exit(1)

    print(config.get(sys.argv[1],sys.argv[2]))

if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print('ERROR: ' + str(e), file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


