# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
from tkinter import *
#from n225trader.trade_lib import kabustclient as client, weborder, webhookclient as webclient
from n225trader.trade_lib.kabustclient import KabuClients
from n225trader.trade_lib.weborder import weborder
from n225trader.trade_lib.webhookclient import Webhookclient as webclient

import formn225 as form
import trading as trade

# import trading

# 売買区分辞書の定義
SIDES = {
    '売': '1',
    '買': '2'
    }
# 注文の種類
ORDERTYP = {
    'limit': 0,
    'market': 1,
    'stop': 2
}
# 注文命令
ORDERCMD = {
    'buy': 1,
    'sell': 2,
    'sellshort': 3,
    'buytocover': 4
}

PRODUCT = {
    '全て': '0',
    '現物': '1',
    '信用': '2',
    '先物': '3',
    'OP': '4'
}

# 発注取引区分
TRADETYPE = {
    '新規': 1,
    '返済': 2,
    '取消': 3
}

# 約定照会取引区分
CASHMARGIN = {
    '新規': 2,
    '返済': 3,
    '取消': 1         # 追加
}

AUTOTYPE = {
    '手動': 0,
    '自動': 1
}


class autotrad(form.formn225):
    def __init__(self):
        super(autotrad, self).__init__()
        self.alerttimer = 0         # アラート監視用ストップウォッチ
        self.trade_count = 0
        # ウインドウが閉じる前にon_closing()を実行する
        self.master.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.trade = trade.trade()
        self.trade.handMessage = self.WriteMassege
        self.trade.handDispSign = self.disp_sign
        self.trade.handInsrtInfo = self.insrtInfo
        self.trade.handinitinfo = self.init_orders_positions
        self.initial()

        # 配信初期化
        self.client = KabuClients()
        self.client.evthandler += self.tickprice
        self.client.connect()
        # alert recive client (traidingviewのアラートシグナル)
        self.webclient = webclient()
        self.weborder = weborder()
        # 本番はself.weborder.handweborder=self.trading.weborder とする
        self.weborder.handweborder = self.trade.weborder
        # self.weborder.handweborder = self.weborder.handlertest
        self.webclient.sendorder = self.weborder.weborder  # clientに接続
        self.webclient.connect()
        self.ThreadStart()
        # self.testList = {'AutoType': 0, 'TradeType': 1, 'ExecutionID': 'E20201130044AE', 'State': 0}
        #     '20201209A02N19338994'
        #     'E20201130044AE'
    def initial(self):
        # 本番用で認証する
        apiPass = self.trade.set_port_apiPass(1)
        status, apikey = self.trade.get_token()
        if status == 200:
            self.trade.xAPIkey = apikey
            self.xAPIkey.set(apikey)
            # symbolname,symbol 作成
            status, symbol, name = self.trade.get_symbolnameN225mini()
            if status == 200:
                self.symbolname.set(name)
                self.symbol.set(symbol)
                # 銘柄登録
                status, reglist = self.trade.registration(symbol)
                if status == 200:
                    # kabuステーションからorder.potitionを読み込みデータフレームを初期化する
                    self.trade.init_orders_positions()
                    # boad 時価情報取得
                    status, board = self.trade.get_board()
                    if status == 200:
                        # curent price 取得
                        price = board['CurrentPrice']
                        # 取引が始まる前でprice=Noneの場合前日終値を設定する
                        if price ==None:
                            PreviousClose = board['PreviousClose']
                            self.curenPrice.set(PreviousClose)
                            self.trade.curentPrice = PreviousClose
                        else:
                            self.curenPrice.set(price)
                            self.trade.curentPrice = price
                        # テストno
                        # テストの場合trad.set_port_apiPass(0),
                        # Verifystr.set("検証")に書き換える
                        self.Verifystr.set("本番")
                        apiPass = self.trade.set_port_apiPass(1)
                        self.APIpass.set(apiPass)
                        status, apikey = self.trade.get_token()
                        self.trade.xAPIkey = apikey
                        self.xAPIkey.set(apikey)
                        # strategy Nameを取得して画面に描写する
                        strtegyname = None
                        self.StrtegyName.set(strtegyname)
                    else:
                        pass
                else:
                    pass
            else:
                self.WriteMassege(symbol)
        else:
            self.xAPIkey.set("認証失敗")
            # エラーメッセージ表示
            self.WriteMassege(apikey)

    def ThreadStart(self):
        self.trade.setDaemon(True)
        self.client.setDaemon(True)
        self.webclient.setDaemon(True)
        self.trade.start()
        self.client.start()
        self.webclient.start()
        ms = int(datetime.now().microsecond / 1000)
        next_time = 1000 - ms
        self.after(next_time, self.moniter)

    def moniter(self):
        # afterイベントを使って1秒ごとに監視
        # PushClient,Server,Candel1,2,Trade 稼働状態を観察する
        # self.datetime_now = datetime.now().replace(microsecond=0).strftime('%m/%d %H:%M %S')
        # self.time_now = datetime.now().time().replace(microsecond=0)  # 現在の時刻
        if self.alerttimer == 4:
            # アラートチェック
            if self.trade_count < self.trade.loopalert:
                self.lbtrade_alert['image'] = self.imagegrren
            else:
                # トレードループ停止エラー　表示
                self.lbtrade_alert['image'] = self.imagered
                self.WriteMassege("トレーディングループ停止")

            if self.client.isconnect == False:
                self.lbclient_alert['image']= self.imagered
                self.WriteMassege("Push配信クライアント停止")
            else:
                self.lbclient_alert['image'] = self.imagegrren

            if self.webclient.sock == None:
                # self.WriteMassege("webhooksever 停止 ")
                self.button6["state"] = NORMAL
            else:
                self.button6["state"] = DISABLED

            self.alerttimer = 0         # タイムストップウォッチ　リセット
            self.trade_count = self.trade.loopalert
        self.alerttimer += 1
        if self.alerttimer == 4:
            self.lbtrade_alert['image'] = self.imagemaru        # 1秒　点滅

        # print("alert count: ",self.alerttimer,self.trade_count,self.trad.loopalert)
        # 1秒タイマーの時間修正
        ms = int(datetime.now().microsecond / 1000)
        next_time = 1000 - ms
        # nex_time 後　自分自身にイベント
        self.after(next_time, self.moniter)  # nex_ti

    # webhookclientに再接続する
    def btn6_click(self):
        print(self.webclient.sock)
        if self.webclient.sock == None:
            self.webclient = webclient()
            self.weborder = weborder()
            # 本番はself.weborder.handweborder=self.trading.weborder とする
            self.weborder.handweborder = self.trade.weborder
            # self.weborder.handweborder = self.weborder.handlertest
            self.webclient.sendorder = self.weborder.weborder  # clientに接続
            self.webclient.connect()
            self.webclient.connect()
            self.webclient.start()


    def verifybtn(self):
        if self.Verifystr.get() == "検証":
            self.Verifystr.set("本番")
            # objから本番用apiパスワード取得する
            apiPass = self.trade.set_port_apiPass(1)
            # GUIラベル書き込み
            self.APIpass.set(apiPass)
        else:
            self.Verifystr.set("検証")
            # objから検証用apiパスワード取得する
            apiPass = self.trade.set_port_apiPass(0)
            self.APIpass.set(apiPass)
        self.apiTokn()

    def apiTokn(self):
        status, apikey = self.trade.get_token()
        if status == 200:
            self.xAPIkey.set(apikey)
        else:
            self.xAPIkey.set("認証失敗")
            # エラーメッセージ表示
            self.WriteMassege(apikey)

    def btn1_click(self):
        if self.auto.get() == '手動':
            self.auto.set('自動')
            # マルチチャートデータをリセットしてからスタートする
            self.trade.autotrade = True
        else:
            self.auto.set('手動')
            # auto Trade stop
            self.trade.autotrade = False

    def btn2_click(self):
        # 新規売発注ボタンイベント
        ordertype = self.rdovar.get()  # 0:指値　1:成行　2:対当値
        tradetype = TRADETYPE['新規']
        side = SIDES['売']
        qty = self.spinval1.get()
        # 対当値で売り注文/push配信されている時のみ発注可能
        if ordertype == 2 and self.client.isconnect==True:
            price = self.askprice.get()
            ordertype = 0
        else:
            price = self.spinval2.get()
        # 引数　tradetype: 1 新規　2,3 返済, Side：1 売り ２買い, ordertype: 0 指値　1 成行
        status, orderid = self.trade.send_order(AUTOTYPE['手動'], tradetype, side, price, qty, ordertype)
        """
        if status == 200:
            # 約定照会へ
            self.trad.autoState = 10
        else:
            self.WriteMassege(str(datetime.now()) + '　新規売り発注エラー')
            self.trad.autoState = 0
        """
    def btn3_click(self):
        # 新規買い発注ボタンイベント
        ordertype = self.rdovar.get()  # 0:指値　1:成行　2:対当値
        AutoTradeType = AUTOTYPE['手動']
        tradetype = TRADETYPE['新規']
        side = SIDES['買']
        qty = self.spinval1.get()
        if ordertype == 2 and self.client.isconnect == True:
            price = self.bidprice.get()
            ordertype = 0
        else:
            price = self.spinval2.get()
        # 引数　tradetype: 1 新規　2,3 返済, Side：1 売り ２買い, ordertype: 0 指値　1 成行
        status, orderid = self.trade.send_order(AutoTradeType, tradetype, side, price, qty, ordertype)
        """
        if status == 200:
            # 約定照会へ
            self.trad.autoState = 10
        else:
            self.WriteMassege(str(datetime.now()) + '　新規買い発注エラー')
            self.autoState = 0
        """
    def btn4_click(self):
        # 手動トレード
        strSide =""
        orderQty = 0
        tradetype = TRADETYPE['返済']
        ordertype = self.rdovar.get()  # 0:指値　1:成行　2:対当値
        qty = self.spinval1.get()
        item = self.Treeview2.selection()
        ExecutionID = self.Treeview2.set(item, 8)
        strSide = self.Treeview2.set(item, 3)
        if ordertype == 2 and self.client.isconnect == True:
            if strSide == '売':
                price = self.bidprice.get()
            else:
                price = self.askprice.get()
            ordertype = 0
        else:
            price = self.spinval2.get()
         # id = self.trad.dfinfo2.loc[0,'ExecutionID']
        # Treeview2が選択されていない場合はエラー
        if ExecutionID != "":
            strautotype = self.Treeview2.set(item, 1)
            if strautotype == "手動":
                autotype = AUTOTYPE['手動']
            else:
                autotype = AUTOTYPE['自動']
            # 保有枚数取得
            strQty = self.Treeview2.set(item, 4)  # カラム３
            holdqty = int(float(strQty))
            strSide = self.Treeview2.set(item, 3)
            # 返済の場合　買い建玉の場合は売り返済
            if strSide == '売':
                side = SIDES['買']
            else:
                side = SIDES['売']
            # 指値／成行　分岐
            if ordertype == 1:
                price = 0
            if qty > holdqty:
                orderQty = holdqty
            else:
                orderQty = qty

            # 引数　tradetype: 1 新規　2,3 返済, Side：1 売り ２買い, ordertype: 0 指値　1 成行
            status, orderid = self.trade.send_order(autotype, tradetype, side, price, orderQty, ordertype, ExecutionID)

        else:
            self.WriteMassege(str(datetime.now()) + '　返済データは選択されていません')

    def btn5_click(self):
        # 注文中のキャンセルする
        orderId = ''
        item = self.Treeview1.selection()
        state = self.Treeview1.set(item, 5)
        if state == "注文中":
            AutoType = AUTOTYPE['手動']
            orderId = self.Treeview1.set(item, 9)
            status, orderId = self.trade.cancelorder(AutoType, orderId)
            """
            if status == 200:
                self.trad.autoState = 10
            else:
                self.trad.autoState = 0
            """

    def SetcurentPrice(self):
        # spinbox注文価格イベント
        price = self.spinval2.get()
        curentPrice = self.curenPrice.get()
        if curentPrice != None:
            # 注文価格は下限価格以上で上限価格以下の場合オーダーする  下限現在の価格より５００円　上限　現在価格から５００円上
            if price >= curentPrice - 800 and price <= curentPrice + 800:
                pass
            else:
                # 現在のぁ連と価格をセットする
                self.spinval2.set(curentPrice)
        return


    def tree_select(self, event):
        pass

    # ---- GUI インターフェース
    def WriteMassege(self, txt):
        self.Statustxt["state"] = NORMAL  # 編集可能にし文字列を書き込む
        # self.Statustxt.insert(1.0, "Hello!"+"\n")
        self.Statustxt.insert(END, txt + "\n")  # 最終行に書き込む
        self.Statustxt.see(END)  # スクロールする
        self.Statustxt["state"] = DISABLED  # 編集不可 state=DISABLEDに設定

    def disp_sign(self, sign):
        # signはlist 0:Date ,1:売買 , 2:価格
        self.entryDate.set(sign[0])
        self.entrySign.set(sign[1])
        self.entryPrice.set(sign[2])

    # Push配信より価格を受信する
    def tickprice(self, sender, earg):
        price = sender['CurrentPrice']
        Symbol = sender['Symbol']
        SymbolName = sender['SymbolName']
        if Symbol == self.symbol.get():
            # 最良買気配値
            ask =sender['AskPrice']
            self.askprice.set(ask)
            # print(sender['AskSign'])
            self.asksign = sender['AskSign']
            # 最良売り気配値
            bid = sender['BidPrice']
            self.bidprice.set(bid)
            self.bidsign = sender['BidSign']
            if self.prevprice != price:
                self.prevprice = price
                self.curenPrice.set(price)
                # 約定情報profitLossの計算をする
                items = self.Treeview2.get_children()
                for item in items:
                    side = self.Treeview2.set(item, 3)
                    positionprice = float(self.Treeview2.set(item, 6))
                    posqty = float(self.Treeview2.set(item, 4))
                    if side == '買':
                        profit = (price - positionprice) * posqty * 100
                        self.Treeview2.set(item, 7,profit)
                    else:
                        profit = (positionprice - price) * posqty * 100
                        self.Treeview2.set(item, 7, profit)
                self.trade.curentPrice = price

    def init_orders_positions(self,box):
        orders = box[0]
        positions = box[1]
        # for index,row でないとエラーになる
        # item = (AutoType, RecvTime, tradetype, Side, state, OrderQty, Price, ID)
        for index,row in orders.iterrows():
            # pands Seriesで１行のデータを配列で取得(valuesで)
            litem = row.values
            if litem[0] == AUTOTYPE['手動']:
                litem[0] = '手動'
            else:
                litem[0] = '自動'
            if litem[2]== 1:
                litem[2] = '新'
            else:
                litem[2] = '返'
            if litem[3] == '1':
                litem[3] = '売'
            else:
                litem[3] = '買'
            if litem[4] == 5:
                litem[4] = '約定済'
            elif litem[4] == 3:
                litem[4] = '注文中'
            else:
                litem[4] = '取消済'
            if litem[6] == float(0):
                litem[6] = '成　行'

            # タプル変換してtreeviewに表示
            item = tuple(litem)
            items = self.Treeview1.insert("", 'end', values=item)

        for index, row in positions.iterrows():
            # pands Seriesで１行のデータを配列で取得(valuesで)
            litem = row.values
            if litem[0] == AUTOTYPE['手動']:
                litem[0] = '手動'
            else:
                litem[0] = '自動'
            if litem[2] == '1':
                litem[2] = '売'
            else:
                litem[2] = '買'

            item = tuple(litem)

            items = self.Treeview2.insert("", 'end', values=item)

    def insrtInfo(self, sender):
        select = sender[0]
        item = sender[1]

        if select == 1:     # 新規注文
            state = ""
            price = object
            if item[0] == AUTOTYPE['手動']:
                autotype = '手動'
            else:
                autotype = '自動'
            if item[2] == 1:
                tradetype = '新'
            else:
                tradetype = '返'
            if item[3] == SIDES['売']:
                side = '売'
            else:
                side = '買'
            if item[4] == 3:
                state = '注文中'
                if item[6] == 0:
                    price = '成行注文'
                else:
                    price = item[6]
            elif item[4] == 5:
                state = '約定済'
            item = (autotype, item[1], tradetype, side, state, item[5], price, item[7],item[8])
            items = self.Treeview1.insert("", 'end', values=item)
        elif select == 2:
            state = ""
            price = object
            if item[0] == AUTOTYPE['手動']:
                autotype = '手動'
            else:
                autotype = '自動'
            if item[2] == 1:
                tradetype = '新'
            else:
                tradetype = '返'
            # 返済の場合は逆になる
            if item[3] == SIDES['売']:
                side = '売'
            else:
                side = '買'
            if item[4] == 3:
                state = '注文中'
                if item[6] == 0:
                    price = '成行注文'
                else:
                    price = item[6]
            elif item[4] == 5:
                state = '約定済'
            item = (autotype, item[1], tradetype, side, state, item[5], price, item[7],item[8])
            qty = item[5]
            items = self.Treeview1.insert("", 'end', values=item)
            item = self.Treeview2.selection()

            self.Treeview2.set(item, 5, qty)
        elif select == 3:   # 新規約定
            orderId = sender[3]
            if item[0] == AUTOTYPE['手動']:
                autotype = '手動'
            else:
                autotype = '自動'
            if item[2] == SIDES['売']:
                side = '売'
            else:
                side = '買'
            price = item[5]
            # 要素変更のためlistに変換する
            litem = list(item)
            litem[0] = autotype
            litem[2] = side
            # もう一度タプル変換
            item = tuple(litem)
            items = self.Treeview2.insert("", 'end', values=item)
            items = self.Treeview1.get_children()
            # 同じ注文idの発注データを書き換える
            for item in items:
                if self.Treeview1.set(item, 9) == orderId and self.Treeview1.set(item, 5) == '注文中':
                    self.Treeview1.set(item, 5, '約定済')
                    self.Treeview1.set(item, 7, price)
                    break
        elif select == 4:   # 返済約定　全数量
            # 引数　item = [self.ExecutionID, self.curentId, 5, price]
            ExecutionID = item[0]
            orderId = item[1]
            state = item[2]
            price = item[3]
            # self.Treeview2のExecutionIDと同じ行を探しこの行を削除する
            items = self.Treeview2.get_children()
            for item in items:
                if self.Treeview2.set(item, 8) == ExecutionID:
                    self.Treeview2.delete(item)  # 削除
            # Treeview1　update
            items = self.Treeview1.get_children()
            for item in items:
                if self.Treeview1.set(item, 9) == orderId:
                    self.Treeview1.set(item, 5, '約定済')
                    self.Treeview1.set(item, 7, price)

        elif select == 5:   #　返済約定　分割
            # 引数　item = [self.ExecutionID, qtybase - qty, self.curentId, 5, price]
            ExecutionID = item[0]
            qty = item[1]
            orderId = item[2]
            state = item[3]
            price = item[4]
            items = self.Treeview2.get_children()
            for item in items:
                if self.Treeview2.set(item, 8) == ExecutionID:
                    self.Treeview2.set(item, 4, qty)
                    self.Treeview2.set(item, 5, 0)
            # Treeview1　update
            items = self.Treeview1.get_children()
            for item in items:
                if self.Treeview1.set(item, 9) == orderId:
                    self.Treeview1.set(item, 5, '一部約定')
                    self.Treeview1.set(item, 6, qty)
                    self.Treeview1.set(item, 7, price)
        if select == 6:         # 取り消し
            orderid = sender[1]
            state = sender[2]
            items = self.Treeview1.get_children()
            for item in items:
                if self.Treeview1.set(item, 9) == orderid:
                    self.Treeview1.set(item, 5, '取消し')

    def on_closing(self):
        # 終了前の朱里をここに記述する
        # self.server.on_server_destruct()
        self.client.disconnect()
        self.client.on_close()
        self.trade.tradStop()
        self.webclient.stop()
        # self.client.join()
        # self.webclient.join()
        # self.trad.join()


        print("client",self.client.is_alive())
        print("trad", self.trade.is_alive())
        print("webclient",self.webclient.is_alive())
        self.master.destroy()


win = Tk()
app = autotrad()
app.mainloop()

# if __name__ == '__main__':
#      autotrad()