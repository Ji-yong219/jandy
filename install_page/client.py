from socket import *
try :
    import pymysql, sys, os, pexpect, commands
except :
    import os, sys, commands
    os.system("curl -O https://bootstrap.pypa.io/get-pip.py")
    os.system("python get-pip.py")
    os.system("pip2.7 install pexpect pymysql")
    os.system("rm -f get-pip.py")
    import pymysql, pexpect

def install() :
    clientSock.send("install".encode('utf-8'))
    ver = clientSock.recv(1024)

    if ver == '5.7' :
        os.system("systemctl stop mysqld > /dev/null 2>&1")
        os.system("rpm -e $(rpm -qa | grep mysql) --nodeps > /dev/null 2>&1")
        os.system("rm -rf /var/lib/mysql")
        os.system("rm -f /var/log/mysqld.log")

        os.system("firewall-cmd --zone=public --permanent --add-port=3306/tcp > /dev/null 2>&1")
        os.system("firewall-cmd --reload > /dev/null 2>&1")

        os.system("rpm -Uvh http://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm > mysql_install.log")
        os.system("yum -y install mysql-community-server >> mysql_install.log")
        os.system("sed -i '4a\\port=3306' /etc/my.cnf")

        os.system("echo {0} >> mysql_install.log".format("\nstarting mysql"))
        os.system("systemctl start mysqld")
        os.system("echo {0} >> mysql_install.log".format("\nsuccess\n"))

        clientSock.send("True".encode('utf-8'))

    elif ver == '8.0' :
        os.system("systemctl stop mysqld > /dev/null 2>&1")
        os.system("rpm -e $(rpm -qa | grep mysql) --nodeps > /dev/null 2>&1")
        os.system("rm -rf /var/lib/mysql")
        os.system("rm -f /var/log/mysqld.log")

        os.system("firewall-cmd --zone=public --permanent --add-port=3306/tcp > /dev/null 2>&1")
        os.system("firewall-cmd --reload > /dev/null 2>&1")

        os.system("rpm -Uvh https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm > mysql_install.log")
        os.system("yum -y install mysql-community-server >> mysql_install.log")
        os.system("sed -i '4a\\port=3306' /etc/my.cnf")

        os.system("echo {0} >> mysql_install.log".format("\nstarting mysql"))
        os.system("systemctl start mysqld")
        os.system("echo {0} >> mysql_install.log".format("\nsuccess\n"))

        clientSock.send("True".encode('utf-8'))

    temp, initial_passwd = commands.getstatusoutput("grep 'temporary password' /var/log/mysqld.log")
    initial_passwd = initial_passwd.split()
    initial_passwd = initial_passwd[len(initial_passwd)-1]

    mysql = pexpect.spawn("mysql -uroot -p")

    mysql.expect("Enter password: ")
    mysql.sendline(initial_passwd)

    mysql.expect("mysql> ")
    mysql.sendline("ALTER USER 'root'@'localhost' IDENTIFIED BY '{0}';".format(initial_passwd))

    mysql.expect("mysql> ")
    mysql.sendline("flush privileges;")

    mysql.expect("mysql> ")
    mysql.sendline("quit")

    mysql.close()

def set_passwd() :
    clientSock.send("passwd_c".encode('utf-8'))

    datazip = clientSock.recv(1024)
    datazip = datazip.split(" ")

    conn = pymysql.connect(host='localhost', user='root', password=datazip[0], port=int(datazip[2]), db='mysql', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = 'select user,host from user where user="root"'
    curs.execute(sql)

    rows = curs.fetchall()
    for row in rows :
        row = list(row.values())
    del row[1]

    if row == "%" :
        sql = "ALTER USER 'root'@'%' IDENTIFIED BY '{0}';".format(datazip[1])
    else :
        sql = "ALTER USER 'root'@'localhost' IDENTIFIED BY '{0}';".format(datazip[1])
    curs.execute(sql)

    sql = "flush privileges;"
    curs.execute(sql)

    conn.close()
    return True

def set_port() :
    clientSock.send("port_c".encode('utf-8'))

    port = clientSock.recv(1024)
    port = port.split(",")

    os.system("firewall-cmd --zone=public --permanent --remove-port="+ port[0] + "/tcp")
    os.system("sed -i '5d' /etc/my.cnf")
    os.system("sed -i '5 i\port={0}\n' /etc/my.cnf".format(port[1]))
    os.system("firewall-cmd --zone=public --permanent --add-port="+ port[1] + "/tcp")
    os.system("firewall-cmd --reload")
    os.system("systemctl restart mysqld")

def policy_change() :
    clientSock.send("policy_c".encode('utf-8'))

    datazip = clientSock.recv(1024)
    datazip = datazip.split(",,")
    option = datazip[2].split(" ")
    del datazip[2]
    values = datazip[2].split(" ")
    del datazip[2]
    
    # MySQL Connection
    conn = pymysql.connect(host='localhost', user='root', password=datazip[0], port=int(datazip[1]), db='mysql', charset='utf8')

    # Connection Dictoionary Cursor
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ### 0. check_user_name    1. length    2.mixed_case_count    3. number_count    4. policy    5.special_char_count ###
    if '0' in option :
        try :
            sql = "SET GLOBAL validate_password_check_user_name=" + values[option.index('0')]  + ";"
            curs.execute(sql)

        except pymysql.err.InternalError :
            sql = "SET GLOBAL validate_password.check_user_name=" + values[option.index('0')] + ";"
            curs.execute(sql)

    if '2' in option :
        try :
            sql = "SET GLOBAL validate_password_mixed_case_count={0};".format(values[option.index('2')])
            curs.execute(sql)

        except pymysql.err.InternalError :
            sql = "SET GLOBAL validate_password.mixed_case_count={0};".format(values[option.index('2')])
            curs.execute(sql)
            sql = "flush privileges;"

    if '3' in option :
        try :
            sql = "SET GLOBAL validate_password_number_count={0};".format(values[option.index('3')])
            curs.execute(sql)

        except pymysql.err.InternalError :
            sql = "SET GLOBAL validate_password.number_count={0};".format(values[option.index('3')])
            curs.execute(sql)

    if '4' in option :
        try :
            sql = "SET GLOBAL validate_password_policy={0};".format(values[option.index('4')])
            curs.execute(sql)

        except pymysql.err.InternalError :
            sql = "SET GLOBAL validate_password.policy={0};".format(values[option.index('4')])
            curs.execute(sql)

    if '5' in option :
        try :
            sql = "SET GLOBAL validate_password_special_char_count={0};".format(values[option.index('5')])
            curs.execute(sql)

        except pymysql.err.InternalError :
            sql = "SET GLOBAL validate_password.special_char_count={0};".format(values[option.index('5')])
            curs.execute(sql)

    if '1' in option :
        try :
            sql = "SET GLOBAL validate_password_length={0};".format(values[option.index('1')])
            curs.execute(sql)

        except pymysql.err.InternalError :
            sql = "SET GLOBAL validate_password.length={0};".format(values[option.index('1')])
            curs.execute(sql)

    sql = "flush privileges;"
    curs.execute(sql)
    conn.close()
    
def get_info() :
    clientSock.send("get_info".encode('utf-8'))

    try :
        temp, mysql_log = commands.getstatusoutput("grep 'Version: ' /var/log/mysqld.log")
        mysql_log = mysql_log.split("\n")
        mysql_log = mysql_log[len(mysql_log)-1]
        mysql_log = mysql_log.split()
        
        ### version ###
        mysql_ver = mysql_log[mysql_log.index("Version:")+1]
        
        ### port ###
        mysql_port = mysql_log[mysql_log.index("port:")+1]
        
        ### status ###
        temp, active_check = commands.getstatusoutput("systemctl is-active mysqld")

        ### initial passwd ###
        temp, initial_passwd = commands.getstatusoutput("grep 'temporary password' /var/log/mysqld.log")
        initial_passwd = initial_passwd.split()
        initial_passwd = initial_passwd[len(initial_passwd)-1]

    except IndexError :
        mysql_ver = "unknown"
        mysql_port = "unknown"
        initial_passwd = "unknown"
        active_check = "unknown"

    temp = "{0}\n{1}\n{2}\n{3}".format(initial_passwd, mysql_ver, mysql_port, active_check)
    clientSock.send(temp.encode('utf-8'))

def passwd_check() :
    clientSock.send("passwd_check".encode('utf-8'))
    datazip = clientSock.recv(1024)

    try :
        mysql = pexpect.spawn("mysql -uroot -p")

        mysql.expect("Enter password: ")
        mysql.sendline(datazip)

        mysql.expect("mysql> ")
        mysql.sendline("quit")

        mysql.close()
        clientSock.send("True".encode('utf-8'))


    except :
        clientSock.send("False".encode('utf-8'))

def policy_output() :
    clientSock.send("policy_output".encode('utf-8'))
    datazip = clientSock.recv(1024)
    datazip = datazip.split(" ")

    conn = pymysql.connect(host='localhost', user='root', password=datazip[0], port=int(datazip[1]), db='mysql', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SHOW VARIABLES LIKE 'validate_password%'"
    curs.execute(sql)
    
    values = ""

    rows = curs.fetchall()
    for row in rows :
        row = list(row.values())
        values += row[1] + " " + row[0] + "\n"

    clientSock.send(values.encode('utf-8'))

def quit() :
    clientSock.send("quit".encode('utf-8'))

clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect(('lion.cju.ac.kr', 1234))

print('Connection check finish')

args = sys.argv[1:]

if args[0] == "install" :
    install()

elif args[0] == "pw_change" :
    set_passwd()

elif args[0] == "port_change" :
    set_port()

elif args[0] == "policy_change" :
    policy_change()

elif args[0] == "get_info" :
    get_info()

elif args[0] == "passwd_check" :
    passwd_check()

elif args[0] == "policy_output" :
    policy_output()

elif args[0] == "quit" :
    quit()