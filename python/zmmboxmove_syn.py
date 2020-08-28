#!/usr/bin/python
import commands
def run_command(user, fserver_name, tserver_name):
    status, data = commands.getstatusoutput('ssh -l user \'su - zimbra -c " zmprov -l fserver_name tserver_name"\'')
    print data

user = string(input("Please Enter the your username: "))
fserever_name = string(input("Please Enter the server name from where mailboxes need to move: "))
tserver_name = string(input("Please Enter the name of server to move the mailboxes: "))

run_command(user, fserver_name, tserver_name)
