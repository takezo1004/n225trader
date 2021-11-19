import socket
import json
import threading

host = 'localhost'
# port = 80
port = 8000

class Webhookclient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # callback　handler 関数セット
        self.sendorder = None  # メッセージ表示
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as msg:
            print(msg)
            print("webhook sever is shutdown now")
            # exit(1)
        else:
            print("webhookclient connecting host:{0} port:{1}".format(host,port))


    def handler(self, func, *args):
        if func != None:
            func(*args)

    def send_order(self,recivedata):
        # byte型をstr型に変換する
        msg = recivedata.decode()
        # print(type(msg))

        # 辞書型に変換する
        msg =json.loads(msg)
        # print(type(msg))
        self.handler(self.sendorder,msg)

    def stop(self):
        if self.sock != None:
            self.sock.close()

    def run(self):
        while True:
            try:
                # byte型をstr型に変換する
                recivedata =self.sock.recv(2048)
            except OSError as msg:
                # print(msg)
                print("webhookclient down error msg:{0}".format(msg))
                self.sock.close()
                self.sock = None
                break
            else:
                if len(recivedata) > 0:
                    # print(type(recivedata),len(recivedata))
                    self.send_order(recivedata)
                else:
                    break
        print('webhookclient close')

if __name__ == '__main__':
    from n225trader.trade_lib.weborder import weborder
    client = Webhookclient()
    weborder = weborder()
    weborder.handweborder = weborder.handlertest
    client.sendorder = weborder.weborder # clientに接続
    client.connect()
    client.start()