import os, commands
try :
    ### status ###
    temp, active_check = commands.getstatusoutput("systemctl is-active mysqld")

    ### version ###
    os.system("yum list installed mysql-community-server* > temp")
    temp, mysql_ver = commands.getstatusoutput("awk '{print $2}' temp")
    mysql_ver = mysql_ver.split("\n")
    mysql_ver = mysql_ver[2]
    os.system("rm -f temp")

    ### port ###
    temp, firewall_port = commands.getstatusoutput("firewall-cmd --list-port")
    firewall_port = firewall_port.split(" ")


    temp, mysql_set_port = commands.getstatusoutput("cat /etc/my.cnf")
    mysql_set_port = mysql_set_port.split("\n")
    mysql_set_port = mysql_set_port[4]

    if mysql_set_port == '' or mysql_set_port == '#' :
        if '3306/tcp' in firewall_port :
            mysql_set_port = '3306/tcp'
        else :
            mysql_set_port = "not seted"
    else :
        if mysql_set_port[5:]+"/tcp" in firewall_port :
            mysql_set_port = mysql_set_port[5:]+"/tcp"


    ### initial passwd ###
    try :
        temp, initial_passwd = commands.getstatusoutput("cat /var/log/mysqld.log")
        initial_passwd = initial_passwd.split()
        passwd_where = initial_passwd.index("root@localhost:")
        initial_passwd = initial_passwd[passwd_where+1]
    except :
        initial_passwd = "mysql is not installed"

except IndexError :
    mysql_ver = "unknown"
    mysql_set_port = "unknown"
    initial_passwd = "unknown"
    active_check = "unknown"

temp = "{0}\n{1}\n{2}\n{3}".format(initial_passwd, mysql_ver, mysql_set_port, active_check)

with open('get_info.output', 'w') as f :
    f.write(temp)