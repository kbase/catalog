#!/bin/sh

# start the test NMS endpoint
echo 'Starting NMS...'
export KB_DEPLOYMENT_CONFIG=test.cfg
../narrative_method_store/dist/run_test_nms_endpoint.sh 7125 > nms/error.log 2>&1 &
NMS_PID=$!
echo 'Waiting for NMS to start...'
sleep 20

export PYTHONPATH=pylib:$PYTHONPATH
python -m unittest discover -p "*_test.py"

kill $NMS_PID