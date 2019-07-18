# PyBoson - a python library for distributed computing on AWS cloud.
Deboleena Mukhopadhyay

PyBoson leverage AWS Batch and the Simple Storage Service (S3) for performing distributed computing at scale. AWS provides a command line interface (CLI) that allow users to perform all necessary tasks such as user-authentication, scaling up or down the computing environment, submitting jobs, reading and writing files on S3 etc. However, using this CLIs requires in-depth understanding of AWS and therefore it is hard to use. PyBoson abstracts away nitty-gritty's of these functionalities from the user, and let user distribute their work with bare minimum inputs.




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
