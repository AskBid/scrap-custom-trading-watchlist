from subprocess import call
import os

os.system("scp -i scrapit.pem ec2-user@ec2-35-176-112-198.eu-west-2.compute.amazonaws.com:~/* ./db_2_merge/")
os.system("scp -i scrapit.pem ec2-user@ec2-35-176-112-198.eu-west-2.compute.amazonaws.com:~/logs/* ./logs/")



# call(["ls", "-l"])
