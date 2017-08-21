# PyBoson
Python library for distributed computing using AWS

# Installation in Console
git clone https://github.com/Deboleena/PyBoson.git

# Usage
\# Import \#\
From PyBoson import \*\
\
\# Configuration \#\
AWSConfigure(\
  aws.access.key.id = '****',\
  aws.secret.access.key = '****'\
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
\# Cleanups \#
BatchCleanup(batch.id = 1, s3.bucket = 's3://boson-base/')\
BosonCleanup()