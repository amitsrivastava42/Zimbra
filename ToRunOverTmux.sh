#!/bin/bash
SSH='/usr/bin/ssh' 
SUSER='/usr/bin/sudo -u sysadmin'
AKEY='-o StrictHostKeyChecking=no'
INSMYSQL='yum -y install MySQL-python'
ZIMBRA='/usr/bin/sudo su - zimbra -c "tmux new -s remote -d "top""'
TMUXS='tmux new -s remote -d "top"'
MBOX='mailboxes'
touch $MBOX

echo "Please enter the name of any server from the environment like md01.agate.dfw.synacor.com, followed by [ENTER]:"
read env
$SUSER $SSH $AKEY $env '/usr/bin/sudo su - zimbra -c "zmprov -l gas mailbox"' > $MBOX

for server in `cat $MBOX`
do 

echo -n "Fetching mailbox to apply command..."

echo ""
echo ""

$SUSER $SSH $AKEY $server "$INSMYSQL ; $ZIMBRA"
done 
	
echo ""
echo ""
echo "Command Executed"
echo ""
echo "You can check using (tmux attach )command using zimbra user "
echo "Please not You need to use (ctrl + a + d) command to detach from source server"

#Remove temporary file 
rm $MBOX
