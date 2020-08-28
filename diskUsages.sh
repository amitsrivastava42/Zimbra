#This script will check the usages of partition by the zimbra and throw the output in the csv file.
# This is written by Amit Srivastava, if you think any modification or optimization can made please write
# to amit.srivastava@synacor.com 
# Suggestions are most welcome :)

# This script starts from here. 

# Variable definition section. 
TEMPFILE='.diskinfo_md.synacor.com.tmp'
OUTPUTFILE='diskinfo_md.synacor.com'
touch $TEMPFILE
rm $OUTPUTFILE
SUSER='/usr/bin/sudo -u sysadmin'
SSH='/usr/bin/ssh' 
AKEY='-o StrictHostKeyChecking=no'
HOSTNAME='/bin/hostname'
DFOUT="df -h|egrep 'db|index|zimbra|fstore|store'"
SOUT='sed '/dev/d''
MBOX='mailboxes'
NEWLINE='printf "\n"'
touch $MBOX

###############This kept under consideration for further improvisation if required ##############
#LDAPSEARCH='/usr/bin/ldapsearch'
#/usr/bin/ldapsearch -x -H ldap://ldap01-a.cableone.cmh.synacor.com:389 -D uid=zimbra,cn=admins,cn=zimbra -w 76wmjHkp -LLL -b 'cn=servers,cn=zimbra' cn | grep cn:| grep md | awk '{print $2}'
#LDAPURL=/usr/bin/sudo -u sysadmin ssh md10.cableone.cmh.synacor.com 'hostname; /usr/bin/sudo su - zimbra -c "zmlocalconfig | grep -e "ldap_master_url" "' | awk '{print $3}'
#LDAPPASS=/usr/bin/sudo -u sysadmin ssh md10.cableone.cmh.synacor.com 'hostname; /usr/bin/sudo su - zimbra -c "zmlocalconfig -s| grep "zimbra_ldap_password""' | awk '{print $3}'

##################################################################################################

# Geting list of machine from source file
echo "Please enter the name of any server from the environment like md10.cableone.cmh.synacor.com, followed by [ENTER]:"
read env
$SUSER $SSH $AKEY $env '/usr/bin/sudo su - zimbra -c "zmprov -l gas mailbox"' > $MBOX

echo -n "Fetching data.."
# This will look all the servers for an environment for the space. 
for server in `cat $MBOX`
do 
echo -n "."
$SUSER $SSH $AKEY $server "$HOSTNAME;$DFOUT" >> $TEMPFILE 
done 

sed 's/.*dev.*// ; s/^ *// ; s/  */, /g ; /^$/d; s/^md/\nmd/' $TEMPFILE > $OUTPUTFILE # Alternative to the below line
#$SOUT $TEMPFILE |awk '{for(i=1;i<NF;i++)if(i!=NF){$i=$i","}  }1'  > $OUTPUTFILE

# Remove temporary file 
rm $TEMPFILE
rm $MBOX

# Display the output file 
echo ""
echo "The disk details are available in $OUTPUTFILE"
