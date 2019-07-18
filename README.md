# PyBoson
A python library for distributed computing on AWS cloud.
Deboleena Mukhopadhyay, Chiranjit Mukherjee

PyBoson leverage AWS Batch and the Simple Storage Service (S3) for performing distributed computing at scale. AWS provides a command line interface (CLI) that allow users to perform all necessary tasks such as user-authentication, scaling up or down the computing environment, submitting jobs, reading and writing files on S3 etc. However, using this CLIs requires in-depth understanding of AWS and therefore it is hard to use. PyBoson abstracts away nitty-gritty's of these functionalities from the user, and let user distribute their work with bare minimum inputs.

## Prerequisites
There are 4 steps a user will require to carry out before they start running distributed computations using Boson libraries. These steps are administrative, therefore can not be automated away by Boson.

1. Create an AWS account and provide billing credentials
2. Go to AWS S3 (https://s3.console.aws.amazon.com) and create an S3 bucket that Boson libraries can use as a data store. Any S3 bucket will work.
3. Go to AWS IAM (https://console.aws.amazon.com/iam/home) and do the following:
a. Click on ‘Users’ on the left pane. Create an user with Programmatic Access, AWS Management Console Access, a console password, and attach the AdministratorAccess policy to their role. Copy the Access Key ID, Secret Access Key and Password
b. Click on ‘Roles’ on the left pane. Create a new AWS Batch Service Role and attach the following policies: AmazonS3FullAccess, AWSBatchFullAccess, AWSBatchServiceRole. Note the Service Role ARN
4. Select an AWS region on the top pane. Go to AWS VPC and observe that there exists a default VPC already. Go to Security Groups and copy the Group ID of the ‘default’ VPC security group. Go to ‘Subnets’ and copy the 3 Subnet IDs for this VPC. Advanced AWS users can create their own VPC and Security Group and use those entities instead.



# Installation in Console
git clone https://github.com/Deboleena/PyBoson.git

# Usage
\# Import \#\
from PyBoson import \*\
\
\# Configuration \#\
AWSConfigure(\
  aws.access.key.id = '\*\*\*\*',\
  aws.secret.access.key = '\*\*\*\*'\
)\
\
\# Setup \#\
BosonSetup (\
  service.role.arn = "arn:aws:iam::757968107665:role/BosonBatch",\
  subnets = c("subnet-1a69d77d","subnet-4da19315","subnet-abfc2ce2"),\
  security.group.ids = "sg-ddd562a7"\
)\
\
\# Execution \#\
\# Step 1: Define tasks\
def BosonTask(x):\
	return( x * x )\
\
BosonParams = []\
for x in range(100):\
	BosonParams.append( {'x': x} )\
\
\# Step 2: Bootstrapping\
out = SubmitBosonTasks (\
  X = BosonParams,\
  FUN = BosonTask,\
  njobs = 10,\
  s3.bucket = 's3://boson-base/',\
  blocking.call = True\
)\
print(out)\
\
\# Cleanups \#\
BatchCleanup(batch.id = 1, s3.bucket = 's3://boson-base/')\
BosonCleanup()
