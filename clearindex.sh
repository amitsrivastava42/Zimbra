#!/bin/bash
# This is modified by Amit Srivastava
# This script is written to clear the index's of the users in the provided mailboxes.
# Variable declaration section.
============================================================

SSH='/usr/bin/ssh' 
SUSER='/usr/bin/sudo -u sysadmin'
AKEY='-o StrictHostKeyChecking=no'
INSMYSQL='sudo yum -y install MySQL-python'
ZIMBRA='/usr/bin/sudo su - zimbra -c "tmux new -s remote -d "top""'
TMUXS='tmux new -s remote -d "top"'
MBOX='.mailboxes' # Did the minor change to have the hiddin file. 

=============================================================
# Creating the blank file 
touch $MBOX

# Getting the information on which mailbox need to perform the action. 
echo "Please enter the name of any server from the environment like md01.agate.dfw.synacor.com, followed by [ENTER]: "
read env

# Proccessing the infromation
echo $env > $MBOX
#$SUSER $SSH $AKEY $env '/usr/bin/sudo su - zimbra -c "zmprov -l gas mailbox"' > $MBOX
# Above was not required as we are going to perform the action the specific servers not for all in the environment.

for server in `cat $MBOX`
do 
echo -n "Fetching mailbox to apply command..."
echo ""
echo ""
$SUSER $SSH $AKEY $server "if [`sudo yum info MySQL-python | grep installed | wc -l` -eq 0 ] then $INSMYSQL && echo "Installing MySQL-python" fi; $ZIMBRA"
done 
	
echo ""
echo ""
echo "Command Executed"
echo ""
echo "You can check using (tmux attach )command using zimbra user "
echo "Please not You need to use (ctrl + a + d) command to detach from source server"

#Remove temporary file 
rm $MBOX
