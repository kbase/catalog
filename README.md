# KBase Catalog

KBase core service to manage app and module information, registration, and release.

Build status:
master:  [![Build Status](https://travis-ci.org/kbase/catalog.svg?branch=master)](https://travis-ci.org/kbase/catalog)
staging: [![Build Status](https://travis-ci.org/kbase/catalog.svg?branch=staging)](https://travis-ci.org/kbase/catalog)
develop: [![Build Status](https://travis-ci.org/kbase/catalog.svg?branch=develop)](https://travis-ci.org/kbase/catalog)

Code coverage: (develop branch)
[![Coverage Status](https://coveralls.io/repos/github/kbase/catalog/badge.svg?branch=develop)](https://coveralls.io/github/kbase/catalog?branch=develop)

#### v2.0.3 - TBA
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
