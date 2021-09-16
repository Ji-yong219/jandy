import commands, os, sys

def mysql_install(args) :


    if args[0] == '5.7' :
        os.system("echo Install start > return.output")
        os.system("systemctl stop mysqld > /dev/null 2>&1")
        os.system("yum -y erase mysql*-community* > /dev/null 2>&1")
        os.system("rm -rf /var/lib/mysql")
        os.system("rm -f /var/log/mysqld.log")

        os.system("firewall-cmd --zone=public --permanent --add-port=3306/tcp > /dev/null 2>&1")
        os.system("firewall-cmd --reload > /dev/null 2>&1")

        os.system("yum -y install http://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm > mysql_install.log")
        os.system("yum -y install mysql-community-server >> mysql_install.log")
        os.system("sed -i '4a\\port=3306' /etc/my.cnf")

        print("It is mysql starting")
        os.system("systemctl start mysqld")
        os.system("echo True > return.output")

    elif args[0] == '8.0' :

        os.system("systemctl stop mysqld > /dev/null 2>&1")
        os.system("yum -y erase mysql*-community* > /dev/null 2>&1")
        os.system("rm -rf /var/lib/mysql")
        os.system("rm -f /var/log/mysqld.log")

        os.system("firewall-cmd --zone=public --permanent --add-port=3306/tcp > /dev/null 2>&1")
        os.system("firewall-cmd --reload > /dev/null 2>&1")

        os.system("yum -y install https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm > mysql_install.log")
        os.system("yum -y install mysql-community-server >> mysql_install.log")
        os.system("sed -i '4a\\port=3306' /etc/my.cnf")

        print("start wait......")
        os.system("systemctl start mysqld")
        os.system("echo True > return.output")

args = sys.argv[1:]
mysql_install(args)