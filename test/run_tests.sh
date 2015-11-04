#!/bin/sh

# TODO: a lot could be improved- this could be a python script instead that does better
# cleanup, generate the deploy.cfg files on the fly, etc.

# Note: JAVA_HOME needs to be set

# start the test NMS endpoint
echo 'Starting NMS...'
export KB_DEPLOYMENT_CONFIG=test.cfg
classpath=`cat ../narrative_method_store/dist/jar.classpath.txt`
java -cp $classpath us.kbase.narrativemethodstore.NarrativeMethodStoreServer 7125 > nms/error.log 2>&1 &

NMS_PID=$!

echo 'Waiting for NMS to start...'
sleep 20
curl -d '{"id":"1","params":[],"method":"NarrativeMethodStore.ver","version":"1.1"}' http://localhost:7125

echo '\nstarting tests'

export PYTHONPATH=pylib:$PYTHONPATH
python -m unittest discover -p "*_test.py"

kill -9 $NMS_PID