#!/usr/bin/python
import paramiko

host_name = raw_input('server name: ')
cmd = raw_input('Enter the command: ') 
username = raw_input('Please enter your username: ')
password = raw_input('Please enter you LDAP password: ')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.remote_hostname = host_name
ssh.connect(host_name, username=username, password=password)

stdin,stdout,stderr = ssh.exec_command(cmd)
outlines = stdout.readlines()
resp=''.join(outlines)
print(resp)

#stdin,stdout,stderr=ssh.exec_command('some really useful command')
#outlines=stdout.readlines()
#resp=''.join(outlines)
#print(resp)
