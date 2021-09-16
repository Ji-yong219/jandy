from socket import *
import threading

def thread1() :
    port = 1234

    serverSock = socket(AF_INET, SOCK_STREAM)
    serverSock.bind(('', port))
    serverSock.listen(1)

    while True :
        print('%d번 포트로 접속 대기중...'%port)

        connectionSock, addr = serverSock.accept()

        print(str(addr), 'connection.')

        recvData = connectionSock.recv(1024)
        data = recvData.decode('utf-8')

        if data == "passwd_c" :
            datazip = "현재비밀번호,바꿀비밀번호"
            connectionSock.send(datazip.encode('utf-8'))

        elif data == "port_c" :
            datazip = "현재포트,바꿀포트"
            connectionSock.send(datazip.encode('utf-8'))

        elif data == "policy_c" :
            datazip = "현재비밀번호,현재포트,옵션 ex)0 1 2 3 4 5,값 ex)off 30 5 5 low 5"
            connectionSock.send(datazip.encode('utf-8'))

        elif data == "get_info" :
            recvData = connectionSock.recv(1024)
            get_info = recvData.decode('utf-8')
            print(get_info)

        elif data == "passwd_check" :
            datazip = "체크할 비밀번호"
            connectionSock.send(datazip.encode('utf-8'))

            recvData = connectionSock.recv(1024)
            passwd_check = recvData.decode('utf-8')
            print(passwd_check)

        elif data == "policy_output" :
            datazip = "현재비밀번호,현재포트"
            connectionSock.send(datazip.encode('utf-8'))

            recvData = connectionSock.recv(1024)
            policy_output = recvData.decode('utf-8')
            print(policy_output)
           
        elif data == "quit" :
            break
         
        else :
            pass

thr = threading.Thread (target = thread1, args = ())
thr.start ()
