#!/bin/sh

# TODO: a lot could be improved- this could be a python script instead that does better
# cleanup, generate the deploy.cfg files on the fly, etc.

# Note: JAVA_HOME needs to be set

################################################################
####  STARTUP - run the NMS server and local docker registry

# start the test NMS endpoint
echo 'Starting NMS...'
export KB_DEPLOYMENT_CONFIG=test.cfg
docker compose -f docker-compose_nms.yml up -d
NMS_PID=$!

echo 'Starting Mock Auth API...'
docker run -d --rm -v ${PWD}/mock_auth:/config -v ${PWD}/mock_auth/server.py:/server/server.py -p 7777:5000 --name mock-auth mockservices/mock_json_service

echo 'Waiting for NMS to start...'
sleep 25
curl -d '{"id":"1","params":[],"method":"NarrativeMethodStore.ver","version":"1.1"}' http://localhost:7125/rpc
if [ $? -ne 0 ]; then
    kill -9 $NMS_PID
    echo 'NMS did not startup in time.  Fail.'
    exit 1
fi

echo '\nStarting local Docker Registry...'
docker run -d --rm -p 5000:5000 --name registry registry:2
if [ $? -ne 0 ]; then
    docker start registry
    if [ $? -ne 0 ]; then
        kill -9 $NMS_PID
        echo 'Unable to start up a docker registry.  Fail.'
        exit 1
    fi
fi
sleep 1



################################################################
####  RUN the actual tests

echo '\n\nstarting tests'
export PYTHONPATH=pylib:$PYTHONPATH
coverage run --source=pylib/biokbase/catalog --omit=*Client.py,*Server.py -m unittest discover -p "*_test.py"
TEST_RETURN_CODE=$?
coverage report
echo "unit tests returned with error code=${TEST_RETURN_CODE}"



################################################################
####  SHUTDOWN stuff and exit

# stop NMS
docker compose -f docker-compose_nms.yml down

#stop Docker containers
docker stop mock-auth
docker stop registry

exit ${TEST_RETURN_CODE}