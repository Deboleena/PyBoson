# PyBoson_py
# run: python PyBoson_py

# load libraries & scripts
import s3utils
import AWSBatchUtils

import os
import time


#' Setup an environment for executing tasks in parallel using Boson
#'
#' @param comp_env_name name of the AWS Batch Compute Environment; default is 'boson-comp-env'
#' @param instance_types what type of EC2 instance to attach to the Compute Environment; default is 'm4.large'
#' @param min_vcpus minimum number of vcpus to maintain in the Compute Environment; default valus is 0
#' @param max_vcpus maximum number of vcpus to maintain in the Compute Environment; default valus is 2
#' @param initial_vcpus number of vcpus initially attached to the Compute Environment; default valus is 2
#' @param service_role_arn ARN of a role created in AWS IAM with the following policies attached: AmazonS3FullAccess, AWSBatchServiceRole, AWSBatchFullAccess; required
#' @param subnets subnets from AWS VPC; required
#' @param security_group_ids security_group_ids from AWS VPC; required
#' @param job_queue_name name of the AWS Job Queue; default is 'boson-job-queue'
#' @param job_definition_name name if the AWS Job Definition; default is 'boson-job-definition'


def BosonSetup ( service_role_arn, subnets, security_group_ids, comp_env_name = 'boson-comp-env',
    instance_types = c("m4.large"),
    min_vcpus = 0,
    max_vcpus = 2,
    initial_vcpus = 2,
    job_queue_name = 'boson-job-queue',
    job_definition_name = 'boson-job-definition'):
    
    # create a compute-environment for Boson
    CreateBatchComputeEnvironment (
        comp_env_name = comp_env_name,
        instance_types = instance_types,
        min_vcpus = min_vcpus,
        max_vcpus = max_vcpus,
        initial_vcpus = initial_vcpus,
        service_role_arn = service_role_arn,
        subnets = subnets,
        security_group_ids = security_group_ids
    )

    # create a job queue for Boson
    CreateJobQueue (
        job_queue_name = job_queue_name,
        comp_env_name = comp_env_name
    )

    # register a job-definition for Boson
    RegisterBosonJobDefinition ( job_definition_name = job_definition_name)

#' Configure AWS-CLI
#' 
#' @param aws_access_key_id aws_access_key_id; required
#' @param aws_secret_access_key aws_secret_access_key; required
#' @param aws_region aws_region; defalut value is 'us-west-2'
#' @param output_format output format; defalute value is 'json'
#' @param profile; default value is 'boson'
#' @export

def AWSConfigure ( aws_access_key_id, aws_secret_access_key, aws_region = 'us-west-2', output_format = 'json', profile = 'boson'):

    # make sure ~/_aws
    directory = os.path.dirname("~/.aws/")
    os.mkdir(directory)
    
    # update ~/_aws/credentials
    # if os.path.isfile('~/.aws/credentials') != True:
    #   filename = file("~/.aws/credentials", "rw")
    #   with open(filename, 'r') as f:
    #       lines = f.readlines()

    #   with open(filename, 'w') as f:
 #          for idx,line in enumerate(lines):
 #              (idx in ln and f.write("aws_access_key_id = {}\n aws_secret_access_key ={}".format(aws_access_key_id, aws_secret_access_key))
 #              f.write(line)
        
 #        filename.close()

#' Cleaup a Boson environment
#' 
#' @param comp_env_name name of the AWS Batch Compute Environment; default is 'boson-comp-env'
#' @param job_queue_name name of the AWS Job Queue; default is 'boson-job-queue'
#' @param job_definition_name name if the AWS Job Definition; default is 'boson-job-definition'
#' @export
def BosonCleanup ( comp_env_name = 'boson-comp-env', job_queue_name = 'boson-job-queue', job_definition_name = 'boson-job-definition'):
  
    # deregister a job-definition for Boson
    DeregisterBosonJobDefinition (
      job_definition_name = job_definition_name
    )
    
    # delete the job queue for Boson
    DeleteJobQueue (
      job_queue_name = job_queue_name
    )
    
    # delete the compute-environment for Boson
    DeleteBatchComputeEnvironment (
      comp_env_name = comp_env_name
    )

#'  Submit parallel tasks for batch execution using Boson
#'  
#'  @param X a list of named lists collecting argument tuples of FUN; required
#'  @param FUN a function that solves one parallel task in the batch when run with one argument tuple in X; required
#'  @param njobs number of AWS Batch jobs to spawn for solving all parallel tasks; required
#'  @param s3_bucket an S3 bucket where intermediate files can be stored in sub-folders; required
#'  @param batch_id batch id; default value is NULL, which yields automatic calculation of the batch id
#'  @param s3_path path to an S3 folder; default value is NULL, which causes s3_path to be automatically set by s3_bucket and batch_id
#'  @param bootstarp_agent whetehr to use local R or AWS Batch for bootstrapping jobs; default value is 'localR'
#'  @param job_name name of the Batch job; default value is 'boson-job'
#'  @param job_queue name of the job queue to use; default value is 'boson-job-queue'
#'  @param job_definition name of the job_definition; default value is 'boson-batch-job'
#'  @param region AWS region; default value is 'us-west-2'
#'  @param blocking_call boolean, whether to make SubmitBosonTasks() a blocking call; default value is TRUE
#'  @param ping if blocking_call = TRUE, frequency of printing job status in seconds; default is every 10 seconds
#'  @param print_job_status if blocking_call = TRUE, level of details in printing job status; default value is 'summary'
#'  
#'  @export
def SubmitBosonTasks(
    X,
    FUN,
    njobs,
    s3_bucket,
    batch_id = None,
    s3_path = None,
    bootstarp_agent = ['localR', 'awsBatch'],
    job_name = 'boson-job',
    job_queue = 'boson-job-queue',
    job_definition = 'boson-batch-job',
    region = 'us-west-2',
    blocking_call = True,
    ping = 10,
    print_job_status = ['summary', 'detailed', 'none']):

    # create a new batch_id
    if (batch_id is None):
        objects_in_bucket = S3ListFiles(s3path = s3_bucket)
        batch_folders = re.search(r"batch", object_in_bucket).replace("/", "") 

        if (length(batch_folders) == 0):
            batch_id = 1
        else :
            last_id = -1
            for i in range(batch_folders):
                id = len(batch_folders[i].split("_"))
                if (id > last_id):
                    last_id = id 
            
            batch_id = last_id + 1
        
    
    print "batch_id ={}\n ".format(batch_id)

    # create an s3_path (folder in s3_bucket) where inputs and outputs will be stored
    if (s3_path != None):
        if(re.search(s3_bucket, object_in_bucket)) :
            s3_bucket =  len(s3_bucket) - 1
        
        s3_path = s3_bucket + '{}/batch_{}/'.format(s3_bucket,batch_id)
    print "s3_path = {}\n".format(s3_path)

    # upload inputs to Batch jobs
    SaveObjectesInS3(
        FUN = BosonTask, X = BosonParams, extra_args = list(___),
        s3_path = s3_path,
        key = paste0('batch_', batch_id, '_in')
    )

    # Bootstrap jobs
    if (bootstarp_agent[1] == 'localR') :
        df_jobid = BootstrapBatchJobs (
            batch_id = batch_id,
            ntasks = length(X),
            njobs = njobs,
            s3_path = s3_path,
            job_name = job_name,
            job_queue = job_queue,
            job_definition = job_definition,
            region = region
        )
    else if (bootstarp_agent[1] == 'awsBatch') :
        SubmitBatchJob (
            batch_id = batch_id,
            njobs = njobs,
            s3_path = s3_path, 
            job_type = "bootstrap-r-jobs", 
            job_id = '0',
            task_ids = '0',
            job_name = job_name, 
            job_queue = job_queue, 
            job_definition = job_definition, 
            region = region
        )

        df_jobid = None
        while (df_jobid == None):
            time.sleep(ping)
            df_jobid = LoadObjectsFromS3(
                s3_path = s3_path,
                key = paste0('batch_', batch_id, '_jobids'),
                supressWarnings = TRUE
            )[['df_jobid']]
        
    else:
        stop("Enter a correct boostrap_agent - acceptable values are 'localR', 'awsBatch'")
    
    print "Submitted jobs:\n"
    return (df_jobid)

#' Wait until specified jobs are finished
#' 
#' @param job_ids vector of job-ids; required
#' @param ping frequency of printing job status in seconds; default is every 10 seconds
#' @param print_job_status level of details in printing job status; default value is 'summary'
#' @export
def WaitForJobsToFinish(job_ids, ping = 10, print_job_status = ('summary', 'detailed', 'none')):
    df_monitor = MonitorJobStatus(job_ids, print_job_status = print_job_status)
    if (df_monitor_status not in ['SUCCEEDED', 'FAILED']):
        time.sleep(ping)
    df_monitor = MonitorJobStatus(job_ids, print_job_status = print_job_status)


#' Fetch outcomes of jobs submitted as a Boson batch
#' 
#' @param batch_id bacth_id; required
#' @param njobs number of jobs submitted with the batch_id; required
#' @param s3_bucket S3 bucket where intermediate files can be stored in sub-folders; required
#' @param s3_path path to an S3 folder; default value is NULL, which causes s3_path to be automatically set by s3_bucket and batch_id
def FetchBatchOutcomes (batch_id, njobs, s3_bucket, s3_path = NULL):
  if (s3_path == None):
    if(re.search(s3_bucket, object_in_bucket)) :
      s3_bucket = len(s3_bucket) - 1
    
    s3_path = "{}/batch_{}/".format(s3_bucket, batch_id) 
  
    out_all = LoadObjectsFromS3(
        s3_path = s3_path, 
        keys = 'batch_{}_out_{}'.format(batch_id, njobs)
    )
    return(out_all)

#' Cleanup AWS resources used by a Batch
#' 
#' @param batch_id batch id; required
#' @param s3_bucket S3 bucket where intermediate files can be stored in sub-folders; required
#' @param s3_path path to an S3 folder; default value is NULL, which causes s3_path to be automatically set by s3_bucket and batch_id
def BatchCleanup (batch_id, s3_bucket, s3_path = NULL):
    if (s3_path == None):
        if(re.search(s3_bucket, object_in_bucket)) :
            s3_bucket = s3_bucket - 1
        
        s3_path = "{}/batch_{}/".format(s3_bucket, batch_id) 
    
    S3DeleteFolder(s3_path)












