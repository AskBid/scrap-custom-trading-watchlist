from boto.ec2 import connect_to_region
from paramiko import SSHClient, RSAKey, AutoAddPolicy
from scp import SCPClient

class EC2connection():

    def __init__(self,
                 dns_name = "ec2-35-176-112-198.eu-west-2.compute.amazonaws.com",
                 access_keys_csv = "rootkey.csv",
                 keypair_pem = "scrapit.pem"):

        self.dns_name = dns_name
        self.access_keys_csv = access_keys_csv
        self.keypair_pem = keypair_pem

    def getFiles(self, files, to_dir):
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        privkey = RSAKey.from_private_key_file(self.keypair_pem)
        ssh.connect(self.dns_name, username='ec2-user', pkey=privkey)

        with SCPClient(ssh.get_transport()) as scp:
           # scp.put('test.txt', 'test2.txt')
           scp.get(files, to_dir)

    def putFile(self, file_):
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        privkey = RSAKey.from_private_key_file(self.keypair_pem)
        ssh.connect(self.dns_name, username='ec2-user', pkey=privkey)

        with SCPClient(ssh.get_transport()) as scp:
           scp.put(file_)

    def getAllFiles(self, dir_, to_dir):
        files = self.cmd('ls {}'.format(dir_))
        for file_name in files:
            if '.' in file_name:
                file_path = dir_ + '/' + file_name
                self.getFiles(file_path, to_dir)

    def rmAll(self, dir_):
        files = self.cmd('ls {}'.format(dir_))
        for file_name in files:
            file_path = dir_ + '/' + file_name
            self.cmd('rm {}'.format(file_path))

    def cmd(self, command = "ls"):

        with open(self.access_keys_csv) as f:
            csv = f.readlines()

        conn =  connect_to_region(
                    "eu-west-2",
                    aws_access_key_id = csv[0].split('=')[1],
                    aws_secret_access_key = csv[1].split('=')[1])

        def stringit(arr):
            arr2 = []
            for i in arr:
                i = i.decode("utf-8")
                arr2.append(i)
            return arr2

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        privkey = RSAKey.from_private_key_file('scrapit.pem')
        ssh.connect(self.dns_name, username='ec2-user', pkey=privkey)

        stdin, stdout, stderr = ssh.exec_command(command)
        stdin.flush()
        data = stdout.read().splitlines()
        data = stringit(data)
        for line in data : print(line)

        ssh.close()

        return data

if __name__ == '__main__':
    ec2 = EC2connection()
    # ec2.getFiles(['watchlistdaily.csv', 'macrowatchlist.csv'], 'trash')
    # ec2.cmd('ls')
    # ec2.getAllFiles('~/','trash')
    # ec2.cmd('ls')
    # ec2.rmAll('logs')
    # ec2.putFile('scrapit.py')
