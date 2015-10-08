SERVICE = catalog
SERVICE_CAPS = Catalog

# note, service port should really be defined in deploy.cfg, as in:
#$(shell perl server_scripts/get_deploy_cfg.pm $(SERVICE_CAPS).port)
SERVICE_PORT = 5000
SPEC_FILE = catalog.spec
URL = https://kbase.us/services/catalog/rpc

#End of user defined variables


KB_RUNTIME ?= /kb/runtime
JAVA_HOME ?= $(DEPLOY_RUNTIME)/java
TARGET ?= /kb/deployment


GITCOMMIT := $(shell if [ -d .git ]; then git rev-parse --short HEAD; else echo 'NOT_TRACKED_BY_GIT'; fi)
TAGS := $(shell if [ -d .git ]; then git tag --contains $(GITCOMMIT); fi)

TOP_DIR = $(shell python -c "import os.path as p; print(p.abspath('../..'))")

TOP_DIR_NAME = $(shell basename $(TOP_DIR))

DIR = $(shell pwd)

LIB_DIR = lib





default: compile-kb-module
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


# start/stop the service running out of THIS directory
build-local-server-control-scripts:
	python service/build_server_scripts.py \
		service/start_service.template \
		service/stop_service.template \
		$(SERVICE) \
		$(KB_RUNTIME) \
		$(DIR) \
		$(DIR)/service/. \
		service
	chmod +x service/start_service.sh


test:
	@echo 'no tests yet'


clean: