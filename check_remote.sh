#This script will check the usages of partition by the zimbra and throw the output in the csv file.
# This is written by Amit Srivastava, if you think any modification or optimization can made please write
# to amit.srivastava@synacor.com 
# Suggestions are most welcome :)

# This script starts from here. 

# Variable definition section. 
SUSER='/usr/bin/sudo -u sysadmin'
SSH='/usr/bin/ssh' 
AKEY='-o StrictHostKeyChecking=no'

# Call the commands options to run
while getopts h:c:help: opt; do
case $opt in
    h) host=$OPTARG ;;
    c) command=$OPTARG ;;
    *) exit 1 ;;
esac
done
