# How administrators change Client Groups (_CG_)

# Background
* All KBase Jobs use a _CG_ to schedule jobs 
* The default _CG_ is `njs`
* Changing a _CG_ will affect the scheduling of *all future jobs*
* If you don't know what you are doing, please ask for help in #devops , #sysadmin, and/or #poc 
* The catalog _CG_ UI is available at https://narrative.kbase.us/#catalog/admin
* The default resources at kept in [ee2](https://github.com/kbase/execution_engine2/blob/ce70b9c818aa84f77a9dec310ef5c5bf256b04c9/deploy.cfg#L53-L56)

As of Dec 2022, the default resources are
```
{"client_group": "njs", "request_cpus": "12", "request_memory" : "10000"}
{"client_group": "bigmem", "request_cpus": "16", "request_memory" : "250000"}
{"client_group": "extreme", "request_cpus": "32", "request_memory" : "200000"}
```


## Step 1: Choose the app you want to change

* To get the `Module Name` is easy, its just the first line in your kbase sdk app spec eg `module kb_StrainFinder {`
* To get the `Function name` is harder, you have to go into the App/UI definition that you want and [see what method it calls](https://github.com/kbaseapps/kb_StrainFinder/blob/master/ui/narrative/methods/run_StrainFinder_v1/spec.json#L96)
 
## Step 2: Select the ClientGroup
* To get the default settings and run on different hardware, set the _CG_ as follows:
```
{"client_group": "bigmem"}
{"client_group": "extreme"}
```

## Step 3: Specify Custom Values (Optional)
**WARNING** You must know the actual capacity of the hardware or the job will be stuck forever and never run
```
{"request_cpus": "64", "client_group": "bigmem", "request_memory" : "500000"}
```


# Give access to the "staging" area on the Data Transfer Node (dtn) for upload jobs
**WARNING** THE DTN NODE IS FOR UPLOAD JOBS, NOT FOR JOBS THAT DO SIGNIFICANT COMPUTATION **WARNING** 
**WARNING** PLEASE CHECK WITH THE DEVELOPER BEFORE ADDING COMPUTATIONALLY INTENSIVE JOBS TO THE UPLOAD QUEUE **WARNING** 

### Step 1: Choose the app you want to change
* Get module name and function name
### Step 2: Select the ClientGroup
```
{"client_group": "kb_upload"}
```
### Step 3: Specify the Docker Volume Mount
Heres an example 
```
kb_model_analysis	model_heatmap_analysis	kb_upload	/dtn/disk0/bulk/${username}      /staging   (read-only)
```
