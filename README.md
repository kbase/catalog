# KBase Catalog

KBase core service to manage app and module information, registration, and release.
Administrators need to be set separately for the job stats page by being added to [deploy.cfg.](https://github.com/kbaseapps/kb_Metrics/blob/master/deploy.cfg)

Build status:
master:  [![Build Status](https://travis-ci.org/kbase/catalog.svg?branch=master)](https://travis-ci.org/kbase/catalog)
staging: [![Build Status](https://travis-ci.org/kbase/catalog.svg?branch=staging)](https://travis-ci.org/kbase/catalog)
develop: [![Build Status](https://travis-ci.org/kbase/catalog.svg?branch=develop)](https://travis-ci.org/kbase/catalog)

Code coverage: (develop branch)
[![Coverage Status](https://coveralls.io/repos/github/kbase/catalog/badge.svg?branch=develop)](https://coveralls.io/github/kbase/catalog?branch=develop)

#### v2.2.0 - 1/23/19
  - Update code to run on Python 3
  - Use Auth Roles for Catalog Admin
  
#### v2.1.3 - 11/16/18
  - Update docker-py client code to current 3.x API
  - Get Travis-CI tests working again
  - Convert to dockerhub image builds
  - Change start script to keep service running in foreground

#### v2.1.2 - 3/16/18
  - Pull a new base image if possible each time a module is registered
  - Fix the logic that allows additional html files to be passed from a method's 
  ui specification directory to the narrative method service during method validation

#### v2.1.1 - 6/26/17
  - Bugfix for change in docker build log

#### v2.1.0 - 4/13/17
  - No change from 2.0.7, but upgraded minor version number because many new features
    now exist since the initial 2.0.x release.

#### v2.0.7 - 3/28/17
  - Added job_id field to raw execution statistics
  - Support for hidden configuration parameters

#### v2.0.6 - 12/7/16
  - Bug is fixed in module registration related to docker client timeout happening 
    for long reference-data stage

#### v2.0.5 - 9/12/16
  - Added volume mount configuration
  - Modified client group configurations so that functions are specified, not app_ids
  - Allow admin users to register modules
  - Initial porting to new KBase authentication clients

#### v2.0.3 - 5/31/16
  - Major release to support storage of local functions and dynamic services information,
    including methods to query/filter/fetch local function and dynamic service info
  - Improved methods for fetching module versions by semantic version matching
  - All old module versions are now preserved and can be retrieved by git commit hash
  - Module descriptions are now attached to specific module versions instead of to
    the module itself, so are effectively versioned
  - Tests extended to cover docker steps in registration in Travis, and added to coveralls

#### v1.0.4 - 2/26/16
  - Fix for bug with accessible dev-version after registration failure

#### v1.0.3 - 2/24/16
  - Method to generate usage stats for admins

#### v1.0.2 - 2/18/16
  - Allow specification of client groups
  - Method to check for admin status

#### v1.0.1 - 2/17/16
  - Prevent reregistration of inactive modules

#### v1.0.0 - 2/11/16
  - First release, all features are new
  - Dynamic KBase SDK module registration
  - Management of the module release process (dev->beta->release)
  - Versioning of all release versions
  - Basic query and search of modules
  - Management of approved KBase developers
  - Management of favorite Apps
  - Tracking and query of SDK module run statistics
  - Admin methods for approving modules/developers, updating module state
