FROM kbase/sdkbase2:latest AS build

COPY . /tmp/catalog
RUN cd /tmp/catalog && make && make deploy

FROM kbase/kb_python:latest

COPY --from=build /kb/deployment/lib/biokbase /kb/deployment/lib/biokbase
COPY --from=build /kb/deployment/services /kb/deployment/services

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/catalog.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0-rc1" \
      us.kbase.vcs-branch=$BRANCH \
      maintainer="Steve Chan sychan@lbl.gov"


ENTRYPOINT [ "/kb/deployment/bin/dockerize" ]

# Here are some default params passed to dockerize. They would typically
# be overidden by docker-compose at startup
CMD [ ]