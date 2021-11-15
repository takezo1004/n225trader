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

    def send_order(self,msg):
        time = msg['time']
        symbol = msg['ticker']
        interval =msg['interval']
        side = msg['strategy']['order_action']
        qty = msg['strategy']['order_contracts']
        marketposition = msg['strategy']['market_position']
        prevmarketposition = msg['strategy']['prev_market_position']
        marketposition_size = msg['strategy']['market_position_size']
        prevmarketposition_size = msg['strategy']['prev_market_position_size']
        strmssg = "recive alert 時間 {0} 銘柄名: {1} {2}分足 : {3} : {4}枚 : marketposition:{5} prevmarketposition:{6}".format(time,symbol,interval,side,qty,marketposition,prevmarketposition)
        print(strmssg)
        self.handler(self.sendorder, [side,qty,marketposition,marketposition_size,prevmarketposition,prevmarketposition_size])

    def stop(self):
        if self.sock != None:
            self.sock.close()

    def run(self):
        while True:
            try:
                data =self.sock.recv(1024)
            except OSError as msg:
                # print(msg)
                print("webhookclient down error msg:{0}".format(msg))
                self.sock = None
                break
            # 受信データはbyte型なのでstr型に変換する
            msg = data.decode()
            #辞書型に変換する
            msg =json.loads(msg)

            self.send_order(msg)
            # print(msg['strategy']['order_action'])

        print('webhookclient close')

if __name__ == '__main__':
    from n225trader.trade_lib.weborder import weborder
    client = Webhookclient()
    weborder = weborder()
    weborder.handweborder = weborder.handlertest
    client.sendorder = weborder.weborder # clientに接続
    client.connect()
    client.start()