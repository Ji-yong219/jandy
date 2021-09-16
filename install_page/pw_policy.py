import os, sys, pexpect, commands

def policy() :
    try :
        os.system("echo skip-external-locking >> /etc/my.cnf")
        os.system("echo skip-grant-tables >> /etc/my.cnf")
        os.system("systemctl restart mysqld > /dev/null 2>&1")

        mysql = pexpect.spawn("mysql -uroot")

        mysql.expect("mysql> ")
        mysql.sendline("SHOW VARIABLES LIKE 'validate_password%';")
        mysql.logfile = open("return.output", "w")

        mysql.expect("mysql> ")
        mysql.sendline("quit")

        mysql.close()

        os.system("sed -i '/skip/d' /etc/my.cnf")

        os.system("systemctl restart mysqld")

        with open("return.output", "r") as f :
            pw_pl = f.readlines()[4:11]

        for i in range(len(pw_pl)):
            pw_pl[i] = pw_pl[i].split("|")
            pw_pl[i] = pw_pl[i][1]+pw_pl[i][2]

        with open("return.output", "w") as f :
            for i in pw_pl:
                f.write("{0}\n".format(i.strip(' ')))

    except :
        os.system("echo False > return.output")

policy()