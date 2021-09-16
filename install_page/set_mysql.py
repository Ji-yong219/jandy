import os, sys, pymysql, pexpect

def set_passwd(nowpasswd, newpasswd) :
    ### passwd change ###
    mysql = pexpect.spawn("mysql -uroot -p")

    mysql.expect("Enter password: ")
    mysql.sendline(nowpasswd)

    mysql.expect("mysql> ")
    mysql.sendline("ALTER USER 'root'@'localhost' IDENTIFIED BY '{0}';".format(newpasswd))

    mysql.expect("mysql> ")
    mysql.sendline("flush privileges;")

    mysql.expect("mysql> ")
    mysql.sendline("quit")

    mysql.close()

    with open("nowpassword", "w") as f1 :
        f1.write(newpasswd)
    os.system("rm -f newpassword")

def set_port(args) :
    os.system("systemctl stop mysqld")
    os.system("firewall-cmd --zone=public --permanent --remove-port="+ args[0] + "/tcp")
    os.system("sed -i 's/port={0}/port={1}/' /etc/my.cnf".format(args[0], args[1]))
    os.system("firewall-cmd --zone=public --permanent --add-port="+ args[1] + "/tcp")
    os.system("firewall-cmd --reload")
    os.system("systemctl start mysqld")


def policy_change(nowpasswd, port, option, values) :
    # MySQL Connection
    conn = pymysql.connect(host='localhost', user='root', password=nowpasswd, port=int(port), db='mysql', charset='utf8')

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

    if '1' in option :
        try :
            sql = "SET GLOBAL validate_password_length={0};".format(values[option.index('1')])
            curs.execute(sql)

        except pymysql.err.InternalError :
            sql = "SET GLOBAL validate_password.length={0};".format(values[option.index('1')])
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

    sql = "flush privileges;"
    curs.execute(sql)
    conn.close()


### input values ###
args = sys.argv[1:]

if "pw" == args[0] :                # ex) pw
    with open("nowpassword", "r") as f1 :
        nowpasswd = f1.readline().strip()

    with open("newpassword", "r") as f2 :
        newpasswd = f2.readline().strip()

    set_passwd(nowpasswd, newpasswd)

elif "port" == args[0] :            # ex) port now_port change_port
    set_port(args[1:])

elif "policy" == args[0] :          # ex) policy port -o policy -v value
    with open("nowpassword", "r") as f1 :
        nowpasswd = f1.readline().strip()

    option = list()
    values = list()

    for i in range(args.index("-o")+1, args.index("-v")) :
        option.append(args[i])

    for i in range(args.index("-v")+1, len(args)) :
        values.append(args[i])

    policy_change(nowpasswd, args[1], option, values)