
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
        action = sender[0]
        orderqty = sender[1]
        marketposition =sender[2]
        marketposition_size= sender[3]
        prevmarketposition = sender[4]
        prevmarketposition_size = sender[5]
        strmssg = "weborder side:{0} orderqty:{1} marketposition:{2} prevmarketposition:{3}".format(action,orderqty,marketposition,prevmarketposition)
        print(strmssg)


        if marketposition == "flat" and prevmarketposition == "long" and action == "sell":
            # long position 返済
            # 返済ポジションがデータフレーム有るかチェックする
            side = SIDES['売']
            tradetype = TRADETYPE['返済']

            # tradinクラスへ
            self.handler(self.handweborder,[side,orderqty,tradetype])
        elif marketposition == "flat" and prevmarketposition == "short" and action == "buy":
            # short position 返済
            side = SIDES['買']
            tradetype = TRADETYPE['返済']
            self.handler(self.handweborder, [side, orderqty, tradetype])

        elif marketposition == "long" and prevmarketposition == "flat" and action == "buy":
            # 新規　買い 成行買い発注
            side = SIDES['買']
            tradetype = TRADETYPE['新規']
            self.handler(self.handweborder, [side, orderqty, tradetype])

        elif marketposition == "short" and prevmarketposition == "flat" and action == "sell":
            # 新規　売り
            side = SIDES['売']
            tradetype = TRADETYPE['新規'] 
            self.handler(self.handweborder,[side,orderqty,tradetype])

        elif marketposition == "long" and prevmarketposition == "short" and action == "buy":
            # 買いドテン
            # ドテン売買の場合[order_contracts]は返済　枚数+買い　枚数となる
            # 1.short position 決済(買戻し)
            side = SIDES['買']
            tradetype = TRADETYPE['返済']
            qty = prevmarketposition_size
            self.handler(self.handweborder,[side,qty,tradetype])

            side = SIDES['買']
            tradetype = TRADETYPE['新規']
            qty = marketposition_size
            self.handler(self.handweborder,[side,qty,tradetype])
            
        elif marketposition == "short" and prevmarketposition == "long" and action == "sell":
            # 売りドテン
            # 1.long position　決済(売り戻し)
            side = SIDES['売']
            tradetype = TRADETYPE['返済']
            qty = prevmarketposition_size
            self.handler(self.handweborder,[side,qty,tradetype])
            # 2.新規　売り
            side = SIDES['売']
            tradetype = TRADETYPE['新規']
            qty = marketposition_size
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
