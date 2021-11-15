# -*- coding: utf-8 -*-
import json
import threading
import time
import websocket   # 必須条件　ライブラリを追加する pip install websocket-client
import n225trader.trade_lib.event as event

"""
    class KabuClients(threading.Thread)
    KabuステーションからPUSH配信によりいた情報を受信する。
    受信した情報は
    １．板情報としてGUI画面表示する
    ２．current price はトレードオーダーコントロールで使用する
    ３．ローソク足を作成する
        Copyright by Takao uchida　2020　 10/23
 """

# すれど終了処理に使用する辞書
ctx = {"lock": threading.Lock(), "stop": False}


class KabuClients(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.isconnect = False
        # self.server = WebServe()
        self.ticker = None
        self.evthandler = event.Event()
        self.ws = None

    def connect(self):
        self.ws = websocket.WebSocketApp(
                'ws://localhost:18080/kabusapi/websocket', on_open=self.on_open,
                on_message=self.on_message, on_error=self.on_error,
                on_close=self.on_close)
        # self.ws = websocket.WebSocketApp(
        #     'ws://localhost:8000/hook', on_open=self.on_open,
        #     on_message=self.on_message, on_error=self.on_error,
        #     on_close=self.on_close)

        # self.ws.keep_running = True
        # self.thread = threading.Thread(target=self.forever())
        # self.thread.daemon = True
        # self.thread.start()

    def is_connected(self):
        return self.ws.sock and self.ws.sock.connected

    def disconnect(self):
        self.ws.keep_running = False
        self.ws.close()
        self.isconnect = False
        print("kabuclient disconnect")
    def get(self):
        return self.ticker

    def on_message(self, message):
        # message = json.loads(message)['params']
        # self.ticker = message
        board = json.loads(message)
        # print(message)
        self.evthandler(board)
        # self.callbuck(board)

    def on_error(self, error):
        self.disconnect()
        time.sleep(0.5)
        print("kabuclient on error reconnect")
        self.connect()

    def on_close(self):
        self.isconnect = False
        time.sleep(1)
        print('kabuclient close')

    def on_open(self):
        self.isconnect = True
        # ws.send(json.dumps( {'method':'subscribe',
        #     'params':{'channel':'lightning_ticker_' + self.symbol}} ))
        print('kabuclient connected')

    def run(self):
        print("ws.run_foreve")
        self.ws.run_forever()

# 使用例
# 1. client callback関数を引数としインスタンスを作成する
# 2. client.connect() コネクトする
# 3. client.start クライアントをスタートさせる

# ---- イベント　サンプルpログラム
def tickcallback(sender, earg):
    print(sender)


close = 0


def tickc(sender, earg):
    global close
    price = sender['CurrentPrice']
    symbol = sender['Symbol']
    print("recive symbol:{0} price:{1}".format(symbol,price))
    symbolname = sender['SymbolName']
    if symbol == '9434':
        if close != price:
            close = price
            # print('price', price, Symbol, SymbolName)
            # server.send_data(price)
            print("send data")

if __name__ == '__main__':
    msintarval =15
    intarval =5
    symbol = '9434'
    client = KabuClients()
    client.evthandler +=tickc
    client.connect()
    client.start()
    count = 0

    while True:
        print('busy Count', count)
        count +=1
        time.sleep(5)
