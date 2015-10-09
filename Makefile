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

# we need to stop this.  Everything should be part of the SDK
ifeq ($(TOP_DIR_NAME), dev_container)
include $(TOP_DIR)/tools/Makefile.common
endif

default: compile-kb-module

ifeq ($(TOP_DIR_NAME), dev_container)
include $(TOP_DIR)/tools/Makefile.common.rules
else
	$(warning Warning! Running outside the dev_container - some targets will not work!)
endif

compile-kb-module:
	kb-mobu compile $(SPEC_FILE) \
		--out $(LIB_DIR) \
		--plclname Bio::KBase::$(SERVICE_CAPS)::Client \
		--jsclname javascript/Client \
		--pyclname biokbase.$(SERVICE_CAPS).Client \
		--javasrc java \
		--java \
		--pysrvname biokbase.$(SERVICE_CAPS).Server \
		--pyimplname biokbase.$(SERVICE_CAPS).Impl;
	touch $(LIB_DIR)/biokbase/__init__.py
	touch $(LIB_DIR)/biokbase/$(SERVICE_CAPS)/__init__.py


# start/stop the service running out of THIS directory
build-local-server-control-scripts:
	python service/build_server_scripts.py \
		service/start_service.template \
		service/stop_service.template \
		$(SERVICE_CAPS) \
		$(KB_RUNTIME) \
		$(DIR) \
		$(DIR)/service \
		service
	chmod +x service/start_service.sh
	chmod +x service/stop_service.sh


deploy: deploy-service deploy-server-control-scripts deploy-cfg

# TODO: this needs to work outside the dev_container!!  The mkcfg tool should
# be part of the SDK tooling
#deploy-cfg:
#	perl $(MK_CONFIG) -t $(TARGET)

deploy-service: deploy-python-service

deploy-clients:
	rsync -av lib/Bio/* $(TARGET)/lib/Bio/. --exclude *.bak-*
	rsync -av lib/biokbase/* $(TARGET)/lib/biokbase/. --exclude *.bak-*
	rsync -av lib/javascript/* $(TARGET)/lib/javascript/.

deploy-python-service:
	rsync -av lib/biokbase/* $(TARGET)/lib/biokbase/. --exclude *.bak-*
	echo $(GITCOMMIT) > $(TARGET)/lib/biokbase/$(SERVICE_CAPS)/$(SERVICE).version
	echo $(TAGS) >> $(TARGET)/lib/biokbase/$(SERVICE_CAPS)/$(SERVICE).version

# This will setup the deployment services directory for
# this service, which includes start/stop scripts
deploy-server-control-scripts:
	mkdir -p $(TARGET)/services/$(SERVICE)
	cp service/get_kb_config.py $(TARGET)/services/$(SERVICE)/.
	python service/build_server_scripts.py \
		service/start_service.template \
		service/stop_service.template \
		$(SERVICE_CAPS) \
		$(KB_RUNTIME) \
		$(TARGET) \
		$(TARGET)/services/$(SERVICE) \
		$(TARGET)/services/$(SERVICE)
	chmod +x $(TARGET)/services/$(SERVICE)/start_service.sh
	chmod +x $(TARGET)/services/$(SERVICE)/stop_service.sh
	echo $(GITCOMMIT) > $(TARGET)/services/$(SERVICE).version
	echo $(TAGS) >> $(TARGET)/services/$(SERVICE).version


test:
	@echo 'no tests yet'


clean: