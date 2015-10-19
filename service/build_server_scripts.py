#!/usr/bin/env python
"""
SYNOPSIS

    build_server_scripts.py [START_TEMPLATE] [STOP_TEMPLATE] [SERVICE] [KB_RUNTIME] [KB_TOP] [SERVICE_DIR] [OUTPUTDIR]

DESCRIPTION

    Get a KBase deployment config variable.  The config file location is set
    by the deployment config environment variable KB_DEPLOYMENT_CONFIG.  Useful
    for getting service configuration variables in Makefiles 

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
    print('Usage: python get_kb_config.py  [START_TEMPLATE] [STOP_TEMPLATE] [SERVICE_NAME] [KB_RUNTIME] [KB_TOP] [SERVICE_DIR] [OUTPUTDIR]')

def main ():
    if len(sys.argv)<8:
        print('Not enough arguments.')
        usage()
        return

    if len(sys.argv)>8:
        print('Too many arguments.')
        usage()
        return

    # create the start_service.sh script
    with open (sys.argv[1], "r") as template:
        startTemplate=template.read()

    startScript = startTemplate.format(
        service_name=sys.argv[3],
        kb_runtime=sys.argv[4],
        kb_top=sys.argv[5],
        kb_service_dir=sys.argv[6],
        )
    with open (sys.argv[7]+'/start_service', "w") as start_service_file:
        start_service_file.write(startScript)

    # create the stop_service.sh script
    with open (sys.argv[2], "r") as template:
        stopTemplate=template.read()

    stopScript = stopTemplate.format(
        service_name=sys.argv[3],
        kb_runtime=sys.argv[4],
        kb_top=sys.argv[5],
        kb_service_dir=sys.argv[6],
        )
    with open (sys.argv[7]+'/stop_service', "w") as stop_service_file:
        stop_service_file.write(stopScript)


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


