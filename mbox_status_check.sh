#!/bin/bash
/bin/echo "******************************"
/bin/echo "Showing Mailbox Service Status"
/bin/echo "******************************"
/usr/bin/sudo -u sysadmin /usr/bin/ssh $1 '/usr/bin/sudo /bin/su - zimbra -c "zmmailboxdctl status"'
/bin/echo 
/bin/echo "***************************************"
/bin/echo "Displaying GC Counts of last 10 Minutes"
/bin/echo "***************************************"
output="$(/usr/bin/sudo -u sysadmin /usr/bin/ssh $1 '/usr/bin/sudo /usr/local/bin/zmstat gc_major_count  | tail -10')"
/bin/echo "${output}"
/bin/echo
/bin/echo
/bin/echo
/bin/echo "***************************************"
/bin/echo "Displaying Mail Flow of last 25 Minutes"
/bin/echo "***************************************"
output="$(/usr/bin/sudo -u sysadmin /usr/bin/ssh $1 '/usr/bin/sudo /usr/local/bin/zmstat lmtp_rcvd_msgs  | tail -25')"
/bin/echo "${output}"
while true; do
 read -p "Based on the above results, do you wish to restart mailbox service?" yn
  case $yn in
  [Yy]* ) /usr/bin/sudo -u sysadmin /usr/bin/ssh $1 '/usr/bin/sudo /bin/su - zimbra -c "zmmailboxdctl restart"'; break;;
  [Nn]* ) exit;;
  * ) echo "Please answer Y/y or N/n.";;
  esac
done
/bin/echo
/bin/echo
/bin/echo
/bin/echo "*************************************************************************************"
/bin/echo "If you have restarted mailbox service, do not forget to calculate SLA after 5 minutes"
/bin/echo "You need to execute  "sudo /usr/local/bin/zimbra_sla_impact.sh" to calculate SLA"
/bin/echo "*************************************************************************************"

