
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
# 発注取引区分
TRADETYPE = {
    '新規': 1,
    '返済': 2,
    '取消': 3
}

AUTOTYPE = {
    '手動': 0,
    '自動': 1
}


class weborder():
    def __init__(self):
        self.handweborder = object     # trading.weborder()を設定する。send_order メソッド

    def handler(self,func,*args):
        func(*args)

    def weborder( self,sender):
        time = sender['time']
        alert_name = sender['alert_name']
        symbol = sender['ticker']
        interval = sender['interval']
        id = sender['strategy']['order_id']
        action = sender['strategy']['order_action']
        price = sender['strategy']['order_price']
        contracts = sender['strategy']['order_contracts']  # prevmarketposition_size + prevmarketposition_size
        marketposition = sender['strategy']['market_position']
        prevmarketposition = sender['strategy']['prev_market_position']
        marketposition_size = sender['strategy']['market_position_size']
        prevmarketposition_size = sender['strategy']['prev_market_position_size']
        # print(sender)
        strmssg = "recive alert 時間 {0} alert_name: {1} ID: {2} 時間足: {3} {4}　price: {5} : {6}枚 : marketposition:{7} prevmarketposition:{8}".format(
            time,alert_name, id,interval, action, price,marketposition_size, marketposition, prevmarketposition)

        # action = sender[0]
        # orderqty = sender[1]
        # marketposition =sender[2]
        # marketposition_size= sender[3]
        # prevmarketposition = sender[4]
        # prevmarketposition_size = sender[5]
        # strmssg = "weborder side:{0} orderqty:{1} marketposition:{2} prevmarketposition:{3}".format(action,orderqty,marketposition,prevmarketposition)
        print(strmssg)


        if marketposition == "flat" and prevmarketposition == "long" and action == "sell":
            # long position 返済
            # 返済ポジションがデータフレーム有るかチェックする
            side = SIDES['売']
            tradetype = TRADETYPE['返済']
            msg = "time: {0} 返済: {1} action:{2} qty]:{3} price:{4}".format(time, prevmarketposition,
                                                                                        action, prevmarketposition_size, price)
            print(msg)
            # tradinクラスへ
            self.handler(self.handweborder,[side,contracts,tradetype])
        elif marketposition == "flat" and prevmarketposition == "short" and action == "buy":
            # short position 返済
            side = SIDES['買']
            tradetype = TRADETYPE['返済']
            msg = "time: {0}  返済: {1} action:{2} qty]:{3} price:{4}".format(time,prevmarketposition,action,prevmarketposition_size,price)
            print(msg)
            self.handler(self.handweborder, [side, contracts, tradetype])

        elif marketposition == "long" and prevmarketposition == "flat" and action == "buy":
            # 新規　買い 成行買い発注
            side = SIDES['買']
            tradetype = TRADETYPE['新規']
            msg = "time: {0}  新規: {1} action:{2} qty]:{3} price:{4}".format(time,marketposition,action,marketposition_size,price)
            print(msg)
            self.handler(self.handweborder, [side, contracts, tradetype])

        elif marketposition == "short" and prevmarketposition == "flat" and action == "sell":
            # 新規　売り
            side = SIDES['売']
            tradetype = TRADETYPE['新規']
            msg = "time: {0}  新規: {1} action:{2} qty]:{3} price:{4}".format(time,marketposition,action,marketposition_size,price)
            print(msg)

            self.handler(self.handweborder,[side,contracts,tradetype])

        elif marketposition == "long" and prevmarketposition == "short" and action == "buy":
            # 買いドテン
            # ドテン売買の場合[order_contracts]は返済　枚数+買い　枚数となる
            # 1.short position 決済(買戻し)
            side = SIDES['買']
            tradetype = TRADETYPE['返済']
            qty = prevmarketposition_size
            msg = "time: {0}  ドテン返済: {1} action:{2} qty]:{3} price:{4}".format(time,prevmarketposition,action,qty,price)
            print(msg)
            self.handler(self.handweborder,[side,qty,tradetype])

            side = SIDES['買']
            tradetype = TRADETYPE['新規']
            qty = marketposition_size
            msg = "time: {0}  ドテン新規: {1} action:{2} qty]:{3} price:{4}".format(time,marketposition,action,qty,price)
            print(msg)
            self.handler(self.handweborder,[side,qty,tradetype])
            
        elif marketposition == "short" and prevmarketposition == "long" and action == "sell":
            # 売りドテン
            # 1.long position　決済(売り戻し)
            side = SIDES['売']
            tradetype = TRADETYPE['返済']
            qty = prevmarketposition_size
            msg = "time: {0}  ドテン返済: {1} action:{2} qty]:{3} price:{4}".format(time,prevmarketposition,action,qty,price)
            print(msg)
            self.handler(self.handweborder,[side,qty,tradetype])
            # 2.新規　売り
            side = SIDES['売']
            tradetype = TRADETYPE['新規']
            qty = marketposition_size
            msg = "time: {0}  ドテン新規: {1} action:{2} qty]:{3} price:{4}".format(time,marketposition,action,qty,price)
            print(msg)
            self.handler(self.handweborder,[side,qty,tradetype])

    def handlertest(self,sender):
        side =sender[0]
        orderqty = sender[1]
        tradetype = sender[2]
        if side == SIDES['売']:
            strside = "売"
        elif side == SIDES['買']:
            strside = "買"

        if tradetype == TRADETYPE['新規']:
            strtrandetype = "新規"
        elif tradetype == TRADETYPE['返済']:
            strtrandetype = "返済"
        order = "order data side:{0} orderqty:{1} tradetype:{2}".format(strside,orderqty,strtrandetype)

        print(order)

# 新規発注処理 tradingクラスで記述する
