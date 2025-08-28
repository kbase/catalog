# KBase Catalog

KBase core service to manage app and module information, registration, and release.
Administrators need to be set separately for the job stats page by being added to [deploy.cfg.](https://github.com/kbaseapps/kb_Metrics/blob/master/deploy.cfg)

## Docker Registry Configuration

The catalog supports dual Docker registry configuration for Kubernetes deployments:

- **`docker_registry_host`** - Registry for internal operations (push/pull within cluster)
- **`docker_registry_client_host`** - Registry URL for client-facing image names (external access)

When only `docker_registry_host` is set, it is used for both internal operations and client references, maintaining backward compatibility.

Example configuration:
```bash
# Internal cluster registry
export docker_registry_host="internal-registry.cluster.local:5000"
# External registry URL for clients
export docker_registry_client_host="registry.example.com"
```

Test: Please refer to the instructions at the top of `test/test.cfg.example` file.

Build status:
master:  [![Build Status](https://travis-ci.org/kbase/catalog.svg?branch=master)](https://travis-ci.org/kbase/catalog)
staging: [![Build Status](https://travis-ci.org/kbase/catalog.svg?branch=staging)](https://travis-ci.org/kbase/catalog)
develop: [![Build Status](https://travis-ci.org/kbase/catalog.svg?branch=develop)](https://travis-ci.org/kbase/catalog)

Code coverage: (develop branch)
[![Coverage Status](https://coveralls.io/repos/github/kbase/catalog/badge.svg?branch=develop)](https://coveralls.io/github/kbase/catalog?branch=develop)

