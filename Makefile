SERVICE = catalog
SERVICE_CAPS = Catalog

# note, service port should really be defined in deploy.cfg, as in:
#$(shell perl server_scripts/get_deploy_cfg.pm $(SERVICE_CAPS).port)
SERVICE_PORT = 5000
SPEC_FILE = catalog.spec
URL = https://kbase.us/services/catalog/rpc

#End of user defined variables

KB_RUNTIME ?= /kb/runtime
DEPLOY_RUNTIME ?= $(KB_RUNTIME)
JAVA_HOME ?= $(KB_RUNTIME)/java
TARGET ?= /kb/deployment

GITCOMMIT := $(shell if [ -d .git ]; then git rev-parse --short HEAD; else echo 'NOT_TRACKED_BY_GIT'; fi)
TAGS := $(shell if [ -d .git ]; then git tag --contains $(GITCOMMIT); fi)

TOP_DIR = $(shell python -c "import os.path as p; print(p.abspath('../..'))")

TOP_DIR_NAME = $(shell basename $(TOP_DIR))

DIR = $(shell pwd)

LIB_DIR = lib

PATH := kb_sdk/bin:$(PATH)

default: init compile-kb-module

init:
	git submodule init
	git submodule update

compile-kb-module:
	kb-mobu compile $(SPEC_FILE) \
		--out $(LIB_DIR) \
		--plclname Bio::KBase::$(SERVICE_CAPS)::Client \
		--jsclname javascript/Client \
		--pyclname biokbase.$(SERVICE).Client \
		--javasrc java \
		--java \
		--pysrvname biokbase.$(SERVICE).Server \
		--pyimplname biokbase.$(SERVICE).Impl;
	touch $(LIB_DIR)/biokbase/__init__.py
	touch $(LIB_DIR)/biokbase/$(SERVICE)/__init__.py


# start/stop the service running out of THIS directory
build-local-server-control-scripts:
	python service/build_server_scripts.py \
		service/start_service.template \
		service/stop_service.template \
		$(SERVICE) \
		$(KB_RUNTIME) \
		$(DIR) \
		$(DIR)/service \
		service
	chmod +x service/start_service
	chmod +x service/stop_service


deploy: deploy-client deploy-service deploy-server-control-scripts

deploy-service: deploy-python-service

deploy-client:
	mkdir -p $(TARGET)/lib/Bio $(TARGET)/lib/biokbase $(TARGET)/lib/javascript
	rsync -av lib/Bio/* $(TARGET)/lib/Bio/.
	rsync -av lib/biokbase/* $(TARGET)/lib/biokbase/. --exclude *.bak-*
	rsync -av lib/javascript/* $(TARGET)/lib/javascript/.

deploy-python-service:
	rsync -av lib/biokbase/* $(TARGET)/lib/biokbase/. --exclude *.bak-*
	echo $(GITCOMMIT) > $(TARGET)/lib/biokbase/$(SERVICE)/$(SERVICE).version
	echo $(TAGS) >> $(TARGET)/lib/biokbase/$(SERVICE)/$(SERVICE).version

# This will setup the deployment services directory for
# this service, which includes start/stop scripts
deploy-server-control-scripts:
	mkdir -p $(TARGET)/services/$(SERVICE)
	cp service/get_kb_config.py $(TARGET)/services/$(SERVICE)/.
	python service/build_server_scripts.py \
		service/start_service.template \
		service/stop_service.template \
		$(SERVICE) \
		$(KB_RUNTIME) \
		$(TARGET) \
		$(TARGET)/services/$(SERVICE) \
		$(TARGET)/services/$(SERVICE)
	chmod +x $(TARGET)/services/$(SERVICE)/start_service
	chmod +x $(TARGET)/services/$(SERVICE)/stop_service
	echo $(GITCOMMIT) > $(TARGET)/services/$(SERVICE)/$(SERVICE).version
	echo $(TAGS) >> $(TARGET)/services/$(SERVICE)/$(SERVICE).version


TESTDIR = test
TESTLIB = test/pylib

setup-tests:
	mkdir -p $(TESTLIB)/biokbase
	mkdir -p $(TESTDIR)/nms
	rsync -av lib/biokbase/* $(TESTLIB)/biokbase/. --exclude *.bak-*
	rsync -av auth/python-libs/biokbase/* $(TESTLIB)/biokbase/.
	rsync -av kbapi_common/lib/biokbase/* $(TESTLIB)/biokbase/.
	cd narrative_method_store; make; make build-classpath-list;
#	rsync -av narrative_method_store/lib/biokbase/* $(TESTLIB)/biokbase/.



test: setup-tests
	-cp -n $(TESTDIR)/test.cfg.example $(TESTDIR)/test.cfg
	cd $(TESTDIR); ./run_tests.sh


clean:
