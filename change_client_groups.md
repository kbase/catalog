# How to change client groups in the catalog
* The url is `/#catalog/admin`
* Changing the client groups will affect all jobs
* If you don't know what you are doing, please ask for help in #devops , #sysadmin, and/or #poc 
* To get the `Module Name` is easy, its just the first line in your kbase sdk app spec eg `module kb_StrainFinder {`
* To get the `Function name` is harder, you have to go into the App/UI definition that you want and [see what method it calls](https://github.com/kbaseapps/kb_StrainFinder/blob/master/ui/narrative/methods/run_StrainFinder_v1/spec.json#L96)
 
## Change from `njs` to `bigmem` or `extreme`
* Difficulty Level: Easy
* The default clientgroup is `njs`. It's resource values are [here](https://github.com/kbase/execution_engine2/blob/ce70b9c818aa84f77a9dec310ef5c5bf256b04c9/deploy.cfg#L53-L56)
* If you change to `bigmem` or `extreme` it will have default settings for those queues

## Specify Custom Values
* Difficulty Level: Medium
* If you want [resources values](https://github.com/kbase/execution_engine2/blob/ce70b9c818aa84f77a9dec310ef5c5bf256b04c9/deploy.cfg#L53-L56)
* If you change to `bigmem` or `extreme` it will have default settings for those queues. If you want custom cpu or memory values, you can set it like so
* This requires knowledge of the capabilities of the hardware that the jobs run on. If these values are incorrectly set, the jobs will not be able to be scheduled and will not run.
```
# client_group one of njs, extreme, bigmem, kb_upload
# memory in megabytes
{"request_cpus": "32", "client_group": "extreme", "request_memory" : "250000"}
```

## Specify Upload Jobs
* Difficulty Level: Medium
* Jobs require both the "kb_upload" clientgroup to get to the right machines, and additional specification of the volume mounts
* Step 1) Upload to kb_upload
* Step 2) Add volume mounts as well `/dtn/disk0/bulk/${username}      /staging`
