FROM python:3.9.19 AS build

# The rsync installation is required for the Makefile
RUN apt-get update && apt-get install -y rsync
RUN mkdir -p /kb/deployment/lib/biokbase

COPY . /tmp/catalog
RUN cd /tmp/catalog && make deploy-service deploy-server-control-scripts

FROM python:3.9.19
# These ARGs values are passed in via the docker build command
ARG BUILD_DATE
ARG VCS_REF
ARG BRANCH

RUN apt-get update && apt-get install -y wget uwsgi

# install dockerize
WORKDIR /opt
RUN wget -q https://github.com/kbase/dockerize/raw/master/dockerize-linux-amd64-v0.6.1.tar.gz \
    && tar xvzf dockerize-linux-amd64-v0.6.1.tar.gz \
    && rm dockerize-linux-amd64-v0.6.1.tar.gz
RUN mkdir -p /kb/deployment/bin/
RUN ln -s /opt/dockerize /kb/deployment/bin/dockerize

ENV KB_DEPLOYMENT_CONFIG "/kb/deployment/conf/deploy.cfg"

COPY --from=build /kb/deployment/lib/biokbase /kb/deployment/lib/biokbase
COPY --from=build /kb/deployment/services /kb/deployment/services
COPY --from=build /tmp/catalog/deployment/conf /kb/deployment/conf

WORKDIR /tmp/catalog
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/catalog.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0-rc1" \
      us.kbase.vcs-branch=$BRANCH \
      maintainer="Steve Chan sychan@lbl.gov"


ENTRYPOINT [ "/kb/deployment/bin/dockerize" ]

# Here are some default params passed to dockerize. They would typically
# be overidden by docker-compose at startup
CMD [ "-template", "/kb/deployment/conf/.templates/deploy.cfg.templ:/kb/deployment/conf/deploy.cfg", \
      "/kb/deployment/services/catalog/start_service" ]
