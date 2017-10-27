import boto.ec2
import paramiko

with open('rootkey.csv') as f:
    csv = f.readlines()

conn =  boto.ec2.connect_to_region(
            "eu-west-2",
            aws_access_key_id = csv[0].split('=')[1],
            aws_secret_access_key = csv[1].split('=')[1])

# reservations = conn.get_all_reservations()
# r = reservations[0].instances[0]
# print(r.public_dns_name)
# inst = str(r)
# inst=inst[9:]
# print(inst)
# print("Connection to EC2 service successful ")

dns_name = "ec2-35-176-112-198.eu-west-2.compute.amazonaws.com"
command = ""

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privkey = paramiko.RSAKey.from_private_key_file('scrapit.pem')
    # ssh.connect(r.public_dns_name, username='ec2-user', pkey=privkey)
    ssh.connect(dns_name, username='ec2-user', pkey=privkey)
    stdin, stdout, stderr = ssh.exec_command(command)
    stdin.flush()
    data = stdout.read().splitlines()
    for line in data:
    	print(line)
    ssh.close()
except:
	print("Error while executing the shell command on the instance")
