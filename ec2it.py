from boto.ec2 import connect_to_region
import boto
from paramiko import SSHClient, RSAKey, AutoAddPolicy
from scp import SCPClient
from shutil import copyfile
from time import strftime
from os import remove

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

# def fetch(del_onEC2 = 'leave'): #fetch from temp DB
#     import mergeit
#
#     ec2 = EC2connection()
#     ec2.getFiles('data/scrapData.db', 'fetch/')
#     if del_onEC2 == 'delete':
#         ec2.rmAll('data')
#     copyfile('fetch/scrapData.db', 'fetch/_bak/{}_scrapData.db'.format(strftime('%Y-%m-%d_%H')))
#     copyfile('scrapData.db', '_bak/{}_scrapData.db'.format(strftime('%Y-%m-%d_%H')))
#     mergeit.merge_db('scrapData.db', 'fetch/scrapData.db')
#     remove('fetch/scrapData.db')
#     print('fetch complete.')

def fetch(del_onEC2 = 'leave'): #just download complete DB
    import mergeit

    copyfile('scrapData.db', '_bak/{}_scrapData.db'.format(strftime('%Y-%m-%d_%H')))
    ec2 = EC2connection()
    ec2.getFiles('scrapData.db', '.')
    print('fetch complete.')


def getLogs():
    try:
        ec2 = ec2it.EC2connection()
    except:
        print('No EC2 Connection.')
    try:
        ec2.getAllFiles('~/logs','logs')
        ec2.rmAll('logs')
    except:
        print('No such file or directory (logs/)')

if __name__ == '__main__':
    ec2 = EC2connection()
    # ec2.getFiles(, 'trash')
    # ec2.cmd('ls data')
    ec2.getFiles('data/scrapData.db', 'qui')
    # ec2.getAllFiles('~/logs','trash')
    # ec2.cmd('ls')
    # ec2.rmAll('logs')
    # ec2.putFile('htmit.py', 'mergeit.py', 'drawit.py', 'datait.py')
    # ec2.putFile('htmit.py')


    # ec2.putFile('gui/bigpage.html')
