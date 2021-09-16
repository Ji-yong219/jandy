import pexpect, os
def passwd_change(passwd) :
    try :
        mysql = pexpect.spawn("mysql -uroot -p")

        mysql.expect("Enter password: ")
        mysql.sendline(passwd)

        mysql.expect("mysql> ")
        mysql.sendline("quit")

        #mysql.interact()
        mysql.close()
        return True

    except :
        return False

with open("nowpassword", "r") as f :
    passwd = f.readline()

if passwd_change(passwd) :
    os.system("echo True > return.output")
else :
    os.system("echo False > return.output")