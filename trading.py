# -*- coding: utf-8 -*-
import os
import yaml
import sys
import pandas as pd
import threading
import time
from datetime import datetime
# kabusut 本番　API

# トレードテスト用　 自作API
# import  trade_api.testApi as Api
# from n225trader.trade_lib import is_holiday

from n225trader.stapi.stapi import stapi
from n225trader.trade_lib.is_holiday import is_holiday
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

# 約定照会取引区分
CASHMARGIN = {
    '新規': 2,
    '返済': 3,
    '取消': 1         # 追加
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

AUTOTYPE = {
    '手動': 0,
    '自動': 1
}

TradingHistory = "C:/Users/takao2/n225_trade/datas/histry.csv"
AutoTradeList = "C:/Users/takao2/n225_trade/datas/AutoTradeList.csv"

# すれど終了処理に使用する辞書
ctx = {"lock": threading.Lock(), "stop": False}


class trade(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start_time = datetime.strptime('8:45:00', '%H:%M:%S').time()
        self.end_time = datetime.strptime('15:15:00', '%H:%M:%S').time()
        self.night_start = datetime.strptime('16:30:00', '%H:%M:%S').time()
        self.night_end = datetime.strptime('05:30:00', '%H:%M:%S').time()
        # 日中/夜間　引け建玉EXIT時間とサイン
        self.exittime1 = datetime.strptime('15:00:00', '%H:%M:%S').time()
        self.exittime2 = datetime.strptime('04:00:00', '%H:%M:%S').time()
        self.time_now = datetime.now().time().replace(microsecond=0)  # 現在の時刻
        self.datetime_now = datetime.now().replace(microsecond=0).strftime('%y-%m-%d %H:%M')
        self.API = stapi()
        self.objApi = self.loadDefinition()
        # メソッド
        self.xAPIkey = ''
        self.apiPassword = ''
        self.selectUrl = 0                  # Ture 本番用url,Flse　検証用url
        self.Port = '18081'
        self.symbol = ''
        self.symbolname = ''
        self.StrategyName = ''
        # callback　handler 関数セット
        self.handMessage = object           # メッセージ表示
        self.handDispSign = object          # マルチチャートサイン表示
        self.handInsrtInfo = object         # 注文発注、約定　新規登録
        self.handinitinfo = object
        self.interval = 1  # 1秒タイマー設定
        self.isHoliday = is_holiday
        self.holiday_test = False  # 休場のときテスト：TRUE、 通常：FALSE　
        self.ExchangeOpen = False  # 取引所の稼動　False 休み
        # 注文情報は自動又は手動かlistにsend_order()、キャンセル関数で作成する
        self.deforder = {'AutoType': 0, 'TradeType': 1, 'ExecutionID': "", 'State': 0}
        self.OrderList = {}
        # 約定明細リストの定義文
        self.dfcontract = {'SeqNum': 0, 'AutoType': 0, 'tradetype': 0, 'Side': 0, 'Price': 0, 'Qty': 1, 'ExecutionID': "",'State': 0}
        # 空のリスト定義
        self.contractList = {}
        # 注文、約定保存データフレーム初期化           日時　　　　　新規/返済　売/買　　注文状態　　枚数　注文価格　　約定数,注文番号
        self.orderDF = pd.DataFrame(columns=['AutoType', 'datetime', 'order', 'side', 'State', 'qty', 'price', 'cumqty', 'orderId'])
        self.positionDF = pd.DataFrame(columns=['AutoType', 'datetime', 'side', 'hold', 'qty', 'price', 'profit', 'ExecutionID'])
        # self.dfinfo2.astype({'hold': 'int32', 'qty': 'int32', 'price': 'int32','profit':'int32'})
        self.AutoPositionDf = pd.DataFrame(columns=['AutoType', 'datetime', 'side', 'hold', 'qty', 'price', 'ExecutionID', 'orderId'])
        self.History = pd.DataFrame(columns=['AutoType', 'datetime', 'tradeType', 'side', 'qty', 'price', 'ExecutionID'])
        # autotradコントロール
        self.autotrade = False
        # trade Loop 監視
        self.loopalert = 0          # １秒ごとにカウントする
        # トレード関係の変数
        self.marketPosition = 0
        self.longPosition = 0
        self.shortPosition = 0
        self.curentPrice = 0        # (メイン)から設定される
        #
        self.initial()

    def initial(self):
        # 初期値は検証用に設定する
        self.set_port_apiPass(0)
        # FanctionApiにもapiPasswordとPortbanngouを保存しておく
        self.API.apiPassword = self.apiPassword
        self.API.Port = self.Port

    def loadDefinition(self):       # C:/Users/takao2/rl-TradeNIKEI/myliblary/
        try:
            # with open('apiDefinitions.yaml', 'r') as file:
            with open('C:/Users/takao2/n225trader/config/apidef.yaml', 'r') as file:
                obj = yaml.safe_load(file)
        except Exception as e:
            print('Exception occurred while loading YAML...', file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)
        else:
            return obj

    # 検証用　select :0  ,本番用　select :1
    def set_port_apiPass(self, select):
        if select == 0:
            self.Port = '18081'
            self.apiPassword = self.objApi['apiPassword'][0]
            # FanctionApiにもapiPasswordとPortbanngouを保存しておく
            self.API.apiPassword = self.apiPassword
            self.API.Port = self.Port
            self.selectUrl = select
        elif select == 1:
            self.Port = '18080'
            self.apiPassword = self.objApi['apiPassword'][1]
            # FanctionApiにもapiPasswordとPortbanngouを保存しておく
            self.API.apiPassword = self.apiPassword
            self.API.Port = self.Port
            self.selectUrl = select
        # 履歴ファイルテスト
        if os.path.isfile(TradingHistory):      # ファイルがあるか？
            # csvファイルをDataframeに読み込む
            df5 = pd.read_csv(TradingHistory)
        else:
            # 空のCSVファイル作成
            self.History.to_csv(TradingHistory, index=False)

        return self.apiPassword

    # 注文/約定データフレームを初期化する
    def init_orders_positions(self):
        AutoType = AUTOTYPE['手動']
        status, positions = self.get_positions()
        if status == 200 and len(positions) >= 1:
            for position in positions:
                ExecutionDay = position['ExecutionDay']
                Side = position['Side']
                HoldQty = position['HoldQty']
                LeavesQty = position['LeavesQty']
                Price = position['Price']
                ProfitLoss = position['ProfitLoss']
                ExecutionID = position['ExecutionID']

                item = (AutoType, ExecutionDay, Side, LeavesQty, HoldQty, Price, ProfitLoss, ExecutionID)
                ds = pd.Series(item, index=self.positionDF.columns)
                # 売買約定データ新規追加と注文デーたの’状態'='約定済'書き換え
                self.positionDF = self.positionDF.append(ds, ignore_index=True)
        status, orders = self.get_orders()
        if status == 200:
            for order in orders:
                # 時間取り出し　Tをスペースに置き換える
                RecvTime = order['RecvTime'].split('.')[0].replace('T', ' ').replace('-', '/')
                RecvTime = RecvTime[5:16]       # YYYYと秒を削除する
                # 照会取引区分を注文取引区分に変換する
                CashMargin = order['CashMargin']
                tradetype = CashMargin - 1
                Side = order['Side']
                state = order['State']
                OrderQty = order['OrderQty']
                cumqty = order['CumQty']
                Price = order['Price']
                ID = order['ID']
                # cumqty = ０の場合は約定でなくキャンセルかログアウトエラーでキャンセル
                if state == 5 and cumqty == 0 and OrderQty== 0:
                    state = 0           # state = 0 はキャンセルに定義する
                item = (AutoType, RecvTime, tradetype, Side, state, OrderQty, Price,cumqty, ID)
                ds = pd.Series(item, index=self.orderDF.columns)
                # 売買約定データ新規追加と注文デーたの’状態'='約定済'書き換え
                self.orderDF = self.orderDF.append(ds, ignore_index=True)
                # 注文中があったらorderListに追加する
                if state == 3 and cumqty != OrderQty:
                    # OrderListに自動注文/手動注文区分を追加する
                    myorder = self.deforder.copy()
                    myorder['AutoType'] = AutoType
                    myorder['TradeType'] = tradetype
                    self.OrderList[ID] = myorder
                    # 約定リスト作成
                    #   空の約定詳細リスト作成
                    self.contractList[ID] = []
                    for Detail in order['Details']:
                        if Detail['State'] == 3 and Detail['RecType'] == 8:
                            if CashMargin == CASHMARGIN['新規']:
                                ExecutionID = Detail['ExecutionID']
                                # 同じSeqNum番号が約定リストに有るかチェックしない場合はリストに追加する
                                result = self.checklist(ID, Detail, AutoType, tradetype, Side, ExecutionID, CashMargin)
                            elif CashMargin == CASHMARGIN['返済']:
                                result = self.checklist(ID, Detail, AutoType, tradetype, Side, "Non ExecutionID", CashMargin)


                    # ordersBox.append(item)
            # 自動トレードデータを読み込みデータフレームの初期化とdfinfo1,dfinfo2のAutoTypeを更新する
            if os.path.isfile(AutoTradeList):
                columnsName = ('AutoType', 'datetime', 'side', 'hold', 'qty', 'price', 'ExecutionID', 'orderId')
                # csvファイルの読み込み
                self.AutoPositionDf = pd.read_csv(AutoTradeList, names=columnsName, header=0)
                if len(self.AutoPositionDf) >= 1:
                    # for 文で1行ずつ読み込み処理を行う
                    for index, row in self.AutoPositionDf.iterrows():
                        # おなじorderがある場合 AutoTypeを自動に初期化
                        orderId = row['orderId']
                        ExecutionID = row['ExecutionID']
                        # rowside = row['side']
                        # print(rowside,type(rowside))
                        # 約定データに自動売買が含まれてイルカチェック
                        chack = self.positionDF.loc[self.positionDF['ExecutionID'] == ExecutionID]
                        if  len(chack.index) != 0:
                            self.orderDF.loc[self.orderDF['orderId'] == orderId, 'AutoType'] = row['AutoType']
                            self.positionDF.loc[self.positionDF['ExecutionID'] == ExecutionID, 'AutoType'] = row['AutoType']
                            rowside = row['side']
                            # sideが数値型かチェック
                            if type(rowside) is int:
                                rowside = str(rowside)
                            if rowside == SIDES['売']:
                                self.shortPosition += row['hold']
                            else:
                                hold = row['hold']
                                self.longPosition += hold
                            if self.shortPosition == 0 and self.longPosition == 0:
                                self.marketPosition = 0
                            elif self.shortPosition != 0 and self.longPosition == 0:
                                self.marketPosition = -1
                            elif self.shortPosition == 0 and self.longPosition != 0:
                                self.marketPosition = 1
                            else:
                                # 両建ての場合はmarketpositionは未定値10を指す
                                self.marketPosition = 10
                        else:
                            # 行削除
                            drop_index = self.AutoPositionDf.index[self.AutoPositionDf['ExecutionID']==ExecutionID]
                            self.AutoPositionDf = self.AutoPositionDf.drop(drop_index,axis=0)
                else:
                    pass
            # GUI form へ
            info1 = self.orderDF.copy()
            info2 = self.positionDF.copy()
            self.handler(self.handinitinfo, (info1, info2))

    def handler(self, func, *args):
        func(*args)

    # 取引履歴をCSVファイルに保存
    def append_to_csv5(self, df):
        # 1行ごとにローソク足データ追加する
        df.to_csv(TradingHistory, mode='a', header=False, index=False)

    ''' --------- kabuSAPI 呼び出しメンバー関数 ------- '''
    def get_token(self):
        apipass = self.apiPassword
        ReqestBody = self.objApi['RequestToken']
        # APIPasswordキーのvalueを変更する
        ReqestBody['APIPassword'] = apipass
        status, result = self.API.token(ReqestBody)
        if status == 200:
            api = result[0]['Token']
            self.xAPIkey = api
            self.API.xApikey = api
        else:
            if status != 0:
                code = result[0]['Code']
                massage = result[0]['Message']
                # GUI表示
                massage = '認証エラー　' + str(code) + massage
                api = massage
            else:
                error = result[0].args[0]
                winerror = str(error.args[0])
                strerror = error.args[1]
                api = winerror + strerror
        return status, api

    def post_sendOrder(self, tradetype, listbody):
        ReqestBody = self.objApi['RequestSendOrder']
        # 新規発注処理
        if tradetype == TRADETYPE['新規']:
            # listbody = (symbol, exchange, CashMargin, TimeInForce, side, qty,FrontOrderType, price, expireday)
            ReqestBody = self.objApi['RequestSendOrder']
            ReqestBody['Symbol'] = listbody[0]
            ReqestBody['Exchange'] = listbody[1]
            ReqestBody['TradeType'] = listbody[2]
            ReqestBody['TimeInForce'] = listbody[3]
            ReqestBody['Side'] = listbody[4]  # 1:売り 2:買
            ReqestBody['Qty'] = listbody[5]
            ReqestBody['FrontOrderType'] = listbody[6]
            ReqestBody['Price'] = listbody[7]
            ReqestBody['ExpireDay'] = listbody[8]
        elif tradetype == TRADETYPE['返済']:
            # listbody = (symbol, exchange, CashMargin, TimeInForce, side, qty,ExecutionID, FrontOrderType, price, expireday)
            # [{'HoldID':'E20200924*****','Qty':2},{'HoldID':'E20200924*****','Qty':1}]
            ReqestBody = self.objApi['RequestPaySendOrder']
            ReqestBody['Symbol'] = listbody[0]
            ReqestBody['Exchange'] = listbody[1]
            ReqestBody['TradeType'] = listbody[2]
            ReqestBody['TimeInForce'] = listbody[3]
            ReqestBody['Side'] = listbody[4]  # 1:売り 2:買
            ReqestBody['Qty'] = listbody[5]
            ReqestBody['ClosePositions'][0]['HoldID'] = listbody[6]
            ReqestBody['ClosePositions'][0]['Qty'] = listbody[5]
            ReqestBody['FrontOrderType'] = listbody[7]
            ReqestBody['Price'] = listbody[8]
            ReqestBody['ExpireDay'] = listbody[9]
        else:
            pass
            # ReqestBody['TradeType'] = 2
            # ClosePositionOrderを削除する
            # ReqestBody['ClosePositions'] = listbody[6]
            # ReqestBody['FrontOrderType'] = listbody[7]
            # ReqestBody['Price'] = listbody[8]
            # ReqestBody['ExpireDay'] = listbody[9]
        apikey = self.xAPIkey
        # print(listbody,apikey)
        # 発注 kabuSself.API call
        return self.API.sendorder(ReqestBody, apikey)

    def get_orders(self):
        # 約定照会
        Queryparam = self.objApi['RequestOrder']
        Queryparam['product'] = PRODUCT['先物']
        apikey = self.xAPIkey
        status, result = self.API.ordes(Queryparam, apikey)
        if status == 200:
            orders = result[0]
        else:
            if status != 0:
                code = result[0]['Code']
                massage = result[0]['Message']
                # GUI表示
                massage = '注文約定照会エラー　' + str(code) + massage
                self.handler(self.handMessage, massage)
            else:
                error = result[0].args[0]
                winerror = str(error.args[0])
                strerror = error.args[1]
                massage = '注文約定照会エラー　' + winerror + strerror
                self.handler(self.handMessage, massage)
            # エラー　データなし
            orders = []
        return status, orders

    def cancelorder(self, AutoType, orderId):
        orderId = orderId
        ReqestBody = self.objApi['RequestCancelOrder']
        ReqestBody['OrderId'] = orderId
        apikey = self.xAPIkey
        status, result = self.API.cancelorder(ReqestBody, apikey)
        if status == 200:
            orderId = result[0]['OrderId']
            self.handler(self.handMessage, self.datetime_now + '　取消し注文照会処理開始' + orderId)
        else:
            if len(self.OrderList) != 0:
                del self.OrderList[orderId]
                del self.contractList[orderId]
            if status != 0:
                code = result[0]['Code']
                massage = result[0]['Message']
                # GUI表示
                massage = '注文取り消しエラー　' + str(code) + massage
                self.handler(self.handMessage, massage)
            else:
                error = result[0].args[0]
                winerror = str(error.args[0])
                strerror = error.args[1]
                massage = '注文取り消しエラー　' + winerror + strerror
                self.handler(self.handMessage, massage)
                # エラー　データなし
        return status, orderId

    # 銘柄登録 先物N225min　日通しで登録する
    def registration(self, symbol, exchange=2):
        params = {'Symbols':
            [{
                'Symbol': symbol, 'Exchange': exchange},
            ]}
        apikey = self.xAPIkey
        status, result = self.API.Register(params, apikey)
        if status == 200:
            registlist = result[0]
        else:
            if status != 0:
                code = result[0]['Code']
                massage = result[0]['Message']
                # GUI表示
                massage = '銘柄登録エラー　' + str(code) + massage
                self.handler(self.handMessage, massage)
            else:
                error = result[0].args[0]
                winerror = str(error.args[0])
                strerror = error.args[1]
                massage = '銘柄登録エラー　' + winerror + strerror
                self.handler(self.handMessage, massage)
            # エラー　データなし
            registlist = []
        return status, registlist

    # n225ミニの銘柄名取得する
    def get_symbolnameN225mini(self):
        symbol = ""
        symbolname = ''
        params = {'FutureCode': 'NK225', 'DerivMonth': 0}
        apikey = self.xAPIkey
        status, result = self.API.symbolname(params, apikey)
        if status == 200:
            symbol = result[0]['Symbol']
            symbolname = result[0]['SymbolName']
            # 検証の場合の戻り値はNonを返す
            if (symbol != "") and (symbolname != ""):
                # 限月取得　文字列をスペースで分割　例　"SymbolName": "日経平均先物 20/12"
                listname = symbolname.split()
                listname = listname[1].split('/')
                str_yymm = '20' + listname[0] + listname[1]
                yymm = int(str_yymm)
                params = {'FutureCode': 'NK225mini', 'DerivMonth': yymm}
                apikey = self.xAPIkey
                status, result = self.API.symbolname(params, apikey)
                symbol = result[0]['Symbol']
                self.symbol = symbol
                symbolname = result[0]['SymbolName']
                self.symbolname = symbolname
            else:
                massege = '検証モード　symbol　取得不可'
                self.handler(self.handMessage, massege)
                status = 0
        else:
            if status != 0:
                code = result[0]['Code']
                massage = result[0]['Message']
                massage = 'symbol取得エラー　' + str(code) + massage
                self.handler(self.handMessage, massage)
            else:
                error = result[0].args[0]
                winerror = str(error.args[0])
                strerror = error.args[1]
                massage = 'symbol取得エラー　' + winerror + strerror
                self.handler(self.handMessage, massage)
        return status, symbol, symbolname

    # 銘柄情報 引数　先物　日通し:2, 日中:23,夜間:24
    def get_symbol(self):
        exchange = self.get_exchange_time()
        if exchange != 0:
            symbol = self.symbol
            apikey = self.xAPIkey
            status, result = self.API.symbol(symbol, str(exchange), apikey)
            if status == 200:
                symbol = result[0]
            else:
                if status != 0:
                    code = result[0]['Code']
                    massage = result[0]['Message']
                    massage = 'symbol取得エラー　' + str(code) + massage
                    self.handler(self.handMessage, massage)
                else:
                    error = result[0].args[0]
                    winerror = str(error.args[0])
                    strerror = error.args[1]
                    massage = 'symbol取得エラー　' + winerror + strerror
                    self.handler(self.handMessage, massage)
                symbol = []
        else:
            massege = '取引時間外です'
            self.handler(self.handMessage, massege)
            status = 0
            symbol = []
        return status, symbol

    # 銘柄情報 引数　先物　日通し:2, 日中:23,夜間:24
    def get_board(self):
        exchange = 2
        symbol = self.symbol
        apikey = self.xAPIkey
        status, result = self.API.board(symbol, str(exchange), apikey)
        if status == 200:
            boad = result[0]
        else:
            if status != 0:
                code = result[0]['Code']
                massage = result[0]['Message']
                massage = 'boad取得エラー　' + str(code) + massage
                self.handler(self.handMessage, massage)
            else:
                error = result[0].args[0]
                winerror = str(error.args[0])
                strerror = error.args[1]
                massage = 'boad取得エラー　' + winerror + strerror
                self.handler(self.handMessage, massage)
            boad = []

        return status, boad

    def get_positions(self):
        # 先物　約定残数　
        params = {'product': '3'}
        apikey = self.xAPIkey
        status, result = self.API.positions(params, apikey)
        if status == 200:
            position = result[0]
            positions = []
            for pos in position:
                # LeavesQtyが0でないpositionを取得する
                if pos['LeavesQty'] != 0:
                    positions.append(pos)
        else:
            if status != 0:
                code = result[0]['Code']
                massage = result[0]['Message']
                massage = 'positions取得エラー　' + str(code) + massage
                self.handler(self.handMessage, massage)
            else:
                error = result[0].args[0]
                winerror = str(error.args[0])
                strerror = error.args[1]
                massage = 'positions取得エラー　' + winerror + strerror
                self.handler(self.handMessage, massage)
            positions = []
        return status, positions

    # ----- auto Trade --------
    # 取引時間区分を取得する　
    # 2	日通し
    # 23	日中
    # 24	夜間
    def get_exchange_time(self):
        self.time_now = datetime.now().time().replace(microsecond=0)
        if self.time_now > self.night_end and self.time_now <= self.end_time:
            exchange = 23
        elif self.time_now > self.end_time:
            exchange = 24
        elif self.time_now <= self.night_end:
            exchange = 24
        else:
            exchange = 0            #

        return exchange

    # 自動売買　成行発注のRequest Body 作成
    # 引数　CashMargin: 2 新規　3 返済, Side：1 売り ２買い, ordertype: 0 指値　1 成行
    def send_order(self, AutoType, tradetype, side, price, qty, ordertype, ExecutionID=None):
        errcount = 0
        errlist = []
        orderId = ""
        status, symbol, symbolname = self.get_symbolnameN225mini()
        # 結果チェック
        if status != 200:
            err1 = 'symbol 取得エラー'
            errlist.append(err1)
            errcount += 1
        # 引数のチェック
        if tradetype == 0 or tradetype >= 3:
            err2 = '発注タイプのエラー（新規、返済以外)'
            errlist.append(err2)
            errcount += 1
        if ordertype == 0:
            # 注文価格は下限価格以上で上限価格以下の場合オーダーする  下限現在の価格より５００円　上限　現在価格から５００円上
            # if price < self.curentPrice -500 or price > self.curentPrice +500 :  # max, min renngeを後で設定する
            if price < self.curentPrice - 800 or price > self.curentPrice + 800:
                err3 = '指値は制限範囲外'
                errlist.append(err3)
                errcount += 1
        elif ordertype >= 2:
            err4 = '発注タイプのエラー（指値，成行以外)'
            errlist.append(err4)
            errcount += 1
        # ordertype 指値：0,成行: 1,逆指値：2
        #  注文枚数　１枚以上、５枚以下
        if qty == 0 or qty >= 5:
            err5 = '注文枚数  0 又は5枚以上　エラー'
            errlist.append(err5)
            errcount += 1
        exchange = self.get_exchange_time()
        if exchange == 0:
            err6 = '取引時間外　エラー'
            errlist.append(err6)
            errcount += 1
        if int(side) >= 1 and int(side) <= 2:
            pass
        else:
            err7 = '売買区分　エラー'
            errlist.append(err7)
            errcount += 1
        # # 引数データ正常 Request Body 作成
        if errcount == 0:
            self.symbol = symbol
            exchange = exchange
            # 発注有効期限　FAS :1 一部約定、残数有効、FAK:2 一部約定、残数無効、FOK:3 全数約定　約定しない場合全数量執行

            expireday = 0
            if ordertype == 0:
                FrontOrderType = 20
                TimeInForce = 1         # 指値注文 FAS
            else:
                FrontOrderType = 120
                TimeInForce = 2         # 成行注文 FAK
                price = 0
            # 新規 2/返済　3 分岐　約定条件は本日中のみ有効注文
            listbody = ()
            if tradetype == TRADETYPE['新規']:
                listbody = (symbol, exchange, tradetype, TimeInForce, side, qty,
                            FrontOrderType, price, expireday)
            elif tradetype == TRADETYPE['返済']:
                listbody = (symbol, exchange, tradetype, TimeInForce, side, qty,
                            ExecutionID, FrontOrderType, price, expireday)
            # 発注
            status, result = self.post_sendOrder(tradetype, listbody)
            # 発注情報をTreeviewに１行追加書き込みを行う
            if status == 200:
                orderId = result[0]['OrderId']
                dtime = datetime.now().replace(microsecond=0).strftime('%m/%d %H:%M')
                # 売買新規/返済区分処理
                if tradetype == TRADETYPE['新規']:
                    item = (AutoType, dtime, tradetype, side, 3, qty, price,0, orderId)
                    # データフレームに保存する
                    ds = pd.Series(item, index=self.orderDF.columns)
                    self.orderDF = self.orderDF.append(ds, ignore_index=True)
                    # GUIに書き込むデータは callback関数にて処理する
                    select = 1
                    hndData = [select, item]
                    self.handler(self.handInsrtInfo, hndData)
                    # items = self.Treeview1.insert("", 'end', values=item)
                    self.handler(self.handMessage, self.datetime_now + '　新規発注終了　ID　' + orderId)
                elif tradetype == TRADETYPE['返済']:
                    item = (AutoType, dtime, tradetype, side, 3, qty, price,0, orderId)
                    ds = pd.Series(item, index=self.orderDF.columns)
                    self.orderDF = self.orderDF.append(ds, ignore_index=True)
                    # dfinfo2　qty　に注文数を書き込む
                    self.positionDF.loc[self.positionDF['ExecutionID'] == ExecutionID, 'qty'] = qty
                    # print( type(self.dfinfo1['price']),self.dfinfo2)
                    # GUIに書き込むデータは callback関数にて処理する
                    select = 2
                    hndData = [select, item]
                    self.handler(self.handInsrtInfo, hndData)
                    self.handler(self.handMessage, self.datetime_now + '　返済発注終了　ID　' + orderId)
                # OrderListに自動注文/手動注文区分を追加する
                myorder = self.deforder.copy()
                myorder['AutoType'] = AutoType
                myorder['TradeType'] = tradetype
                myorder['ExecutionID'] = ExecutionID
                self.OrderList[orderId] = myorder
                #   空の約定詳細リスト作成
                self.contractList[orderId] = []
            else:
                if status != 0:
                    code = result[0]['Code']
                    massage = result[0]['Message']
                    massage = '発注エラー　' + str(code) + massage
                    self.handler(self.handMessage, massage)
                else:
                    error = result[0].args[0]
                    winerror = str(error.args[0])
                    strerror = error.args[1]
                    massage = '発注エラー　' + winerror + strerror
                    self.handler(self.handMessage, massage)
        else:
            massage = '発注エラー　発注データ再チェック'
            self.handler(self.handMessage, massage)
        return status, orderId

    # webhook order 処理
    def weborder(self, sender):
        if not self.autotrade:
            return
        side = sender[0]
        orderqty = sender[1]
        tradetype = sender[2]
        print("sid:{0} orderqty:{1} tradetype: {2}".format(side,orderqty,tradetype))
        status = None
        orderId = None
        # web order sign メッセージをstatus boxに表示する
        strside = ""
        strtradetype = ""
        if side == SIDES['買'] :
            strside = "買発注"
        elif side == SIDES['売']:
            strside = "売発注"
        else:
            strside = "売買区分なし"

        if tradetype == TRADETYPE['新規']:
            strtradetype = "新規 "
        elif tradetype == TRADETYPE['返済']:
            if side == SIDES['買']:
                strtradetype = "売り決済 "
                strside = "買発注"
            elif side == SIDES['売']:
                strtradetype = "買い決済 "
                strside = "売発注"
        else:
            strtradetype = "新規まは決済サインなし"
        massage = "webhook sign　" + strtradetype + strside +"を受信しました。"
        self.handler(self.handMessage, massage)
        if tradetype == TRADETYPE['新規']:
            # 新規 成行発注
            length = len(self.AutoPositionDf)
            if length == 0:
                if side == SIDES['買'] or side == SIDES['売']:
                    qty = orderqty
                    entryPrice = 0  # 成行
                    orderType = ORDERTYP['market']  # 成行 ラジオボタンと同じ
                    status, orderId = self.send_order(AUTOTYPE['自動'], tradetype, side, entryPrice, qty,orderType)

        elif tradetype == TRADETYPE['返済']:
            length = len(self.AutoPositionDf)
            if length == 0:
                print("返済するポジションはありません。")
            elif length == 1:
                # self.AutoPositionDf.loc[0, 'side']のsideは数値型になっているので文字型に変換する
                autoside = self.AutoPositionDf.loc[0, 'side']
                if type(autoside) is int:
                    autoside = str(autoside)

                if autoside == SIDES["買"] and side == SIDES["売"]:
                    tradetype = TRADETYPE['返済']
                    entryPrice = 0
                    qty = orderqty
                    orderType = ORDERTYP['market']
                    ExecutionID = self.AutoPositionDf.loc[0, 'ExecutionID']

                    status, orderId = self.send_order(AUTOTYPE['自動'], tradetype, side, entryPrice, qty,orderType, ExecutionID)
                elif autoside == SIDES["売"] and side == SIDES["買"]:
                    tradetype = TRADETYPE['返済']
                    entryPrice = 0
                    qty = orderqty
                    orderType = ORDERTYP['market']
                    ExecutionID = self.AutoPositionDf.loc[0, 'ExecutionID']
                    status, orderId = self.send_order(AUTOTYPE['自動'], tradetype, side, entryPrice, qty,orderType, ExecutionID)
                else:
                    print("返済するポジション(long or short)が違います。")
            else:
                print("返済するポジションが多すぎます。")

    def cancel_updada(self,orderId):
        # 取消、エラー（ログアウトによる取り消し ）
        # キャンセルに状態を書き換える
        self.orderDF.loc[self.orderDF['orderId'] == orderId, 'order'] = TRADETYPE['取消']
        self.orderDF.loc[self.orderDF['orderId'] == orderId, 'State'] = 0
        # treeviw1 データ書き換え
        select = 6
        hndData = [select, orderId, 0]
        self.handler(self.handInsrtInfo, hndData)
        # 終了
        self.handler(self.handMessage, self.datetime_now + '　取り消し注文処理終了')

        return

    def checklist(self,orderId, Detail,AutoType,tradetype,side,ExecutionID,CashMargin):
        fund = False
        for clist in self.contractList[orderId]:
            if clist['SeqNum'] == Detail['SeqNum']:
                fund = True
        if not fund:
            # 約定毎にデータ作成する
            contract = self.dfcontract.copy()
            contract['SeqNum'] = Detail['SeqNum']
            contract['AutoType'] = AutoType
            contract['tradetype'] = tradetype
            contract['Side'] = side
            contract['Price'] = Detail['Price']
            contract['Qty'] = Detail['Qty']
            if CashMargin == CASHMARGIN['新規']:
                contract['ExecutionID'] = Detail['ExecutionID']
            elif CashMargin == CASHMARGIN['返済']:
                contract['ExecutionID'] = ExecutionID
                # 明細リストに分割約定データを追加する
            self.contractList[orderId].append(contract)
        return not fund

    def position_append(self,orderId,orderState,Detail,AutoType,tradetype,side):
        # 新規注文約定追加
        ExecutionID = Detail['ExecutionID']
        price = Detail['Price']
        qty = Detail['Qty']
        RecvTime = Detail['ExecutionDay'].split('.')[0].replace('T', ' ').replace('-', '/')
        RecvTime = RecvTime[3:16]  # YYと秒を削除する yy/mm/dd HH:MM
        # dfinfo2に新規建て玉を追加する
        # item = (日時, 売買区分, 保有, 注文数、約定価格、評価損益)
        item = (AutoType, RecvTime, side, qty, 0, price, price, ExecutionID)
        ds = pd.Series(item, index=self.positionDF.columns)
        # 売買約定データ新規追加と注文デーたの’状態'='約定済'書き換え
        self.positionDF = self.positionDF.append(ds, ignore_index=True)
        # print(dfinfo2)
        # dfinfo1 State Updateする　
        self.orderDF.loc[self.orderDF['orderId'] == orderId, 'State'] = orderState
        # GUIformに表示する
        select = 3
        hndData = [select, item, orderState,orderId]
        self.handler(self.handInsrtInfo, hndData)
        # 履歴に保存する
        # columns=['datetime', 'tradetype', 'side', 'qty', 'price', 'ExecutionID'])
        #   tradetype = TRADETYPE['新規']
        dscsv = pd.DataFrame([[AutoType, RecvTime, tradetype, side, qty, price, ExecutionID]])
        self.append_to_csv5(dscsv)  # CSVファイルに保存する
        if AutoType == AUTOTYPE['自動']:
            # 自動取引のみ保存する
            item = (AutoType, RecvTime, side, qty, 0, price, ExecutionID, orderId)
            ds = pd.Series(item, index=self.AutoPositionDf.columns)
            self.AutoPositionDf = self.AutoPositionDf.append(ds, ignore_index=True)
            #  sideが数値型の時文字型変換する
            if type(side) is int:
                side = str(side)
            if side == SIDES['売']:
                self.shortPosition = self.shortPosition + qty
            else:
                self.longPosition = self.longPosition + qty

            # items = self.Treeview2.insert("", 'end', values=item)
            if self.shortPosition == 0 and self.longPosition == 0:
                self.marketPosition = 0
            elif self.shortPosition != 0 and self.longPosition == 0:
                self.marketPosition = -1
            elif self.shortPosition == 0 and self.longPosition != 0:
                self.marketPosition = 1
            else:
                # 両建ての場合はmarketpositionは未定値10を指す
                self.marketPosition = 10
            # 照会終了
            mkpositon = str(self.marketPosition)
            lposition = str(self.longPosition)
            sposition = str(self.shortPosition)
            # 自動取引データの保存
            self.AutoPositionDf.to_csv(AutoTradeList, index= False)
            self.handler(self.handMessage,self.datetime_now + '　marketposition:' + mkpositon + ' longposition:' + lposition + ' shortposition:' + sposition)
        self.handler(self.handMessage, self.datetime_now + '　新規約定')
        return

    def psition_updata(self,orderId,Detail,AutoType,tradetype,side,ExecutionID):
        # 返済処理
        price = Detail['Price']
        RecvTime = Detail['ExecutionDay'].split('.')[0].replace('T', ' ').replace('-', '/')
        RecvTime = RecvTime[3:16]  # YYと秒を削除する yy/mm/dd HH:MM
        qty = Detail['Qty']
        # 約定情報の該当行保有枚数更新、注文０にセット又は行削除
        # 注文枚数
        orderqty = self.positionDF.loc[self.positionDF['ExecutionID'] == ExecutionID, 'qty'].values[0]
        # 保有枚数
        qtyhold = self.positionDF.loc[self.positionDF['ExecutionID'] == ExecutionID, 'hold'].values[0]
        # print(type(qtyhold),type(qty))
        # 返済はside = 売りの場合買いpositionから注文数を引く
        if qtyhold <= qty:
            # 全返済
            drop_index = self.positionDF.index[self.positionDF['ExecutionID'] == ExecutionID]
            self.positionDF = self.positionDF.drop(drop_index, axis=0)
            self.orderDF.loc[self.orderDF['orderId'] == orderId, 'State'] = 5
            self.orderDF.loc[self.orderDF['orderId'] == orderId, 'price'] = price
            select = 4
            item = [ExecutionID, orderId, 5, price]
            hndData = [select, item]
            self.handler(self.handInsrtInfo, hndData)
        else:
            # 保存数書き換え、注文数を０にする
            self.positionDF.loc[self.positionDF['ExecutionID'] == ExecutionID, 'hold'] = qtyhold - qty
            self.positionDF.loc[self.positionDF['ExecutionID'] == ExecutionID, 'qty'] = 0
            self.orderDF.loc[self.orderDF['orderId'] == orderId, 'State'] = 5
            self.orderDF.loc[self.orderDF['orderId'] == orderId, 'price'] = price
            # treeview1 '状態'=’約定済 'に書き換え
            select = 5
            item = [ExecutionID, qtyhold - qty, orderId, 5, price]
            hndData = [select, item]
            self.handler(self.handInsrtInfo, hndData)
        # 履歴に保存する
        tradetype = TRADETYPE['返済']
        dscsv = pd.DataFrame([[AutoType, RecvTime, tradetype, side, qty, price, ExecutionID]])
        self.append_to_csv5(dscsv)  # CSVファイルに保存する
        # AutoPositionDf自動取引データフレームの更新
        if len(self.AutoPositionDf) != 0:
            # AutoPositionDfに同じExecutionID行検索
            ds = self.AutoPositionDf.loc[self.AutoPositionDf['ExecutionID'] == ExecutionID]
            if len(ds) >= 1:
                qtyhold = self.AutoPositionDf.loc[ds.index, 'hold'].values[0]
                # 返済はside = 売りの場合買いpositionから注文数を引く
                if qtyhold != 0 and qtyhold <= qty:
                    drop_index = self.AutoPositionDf.index[self.AutoPositionDf['ExecutionID'] == ExecutionID]
                    self.AutoPositionDf = self.AutoPositionDf.drop(drop_index, axis=0)
                elif qtyhold != 0:
                    # 保存数書き換え、注文数を０にする
                    self.AutoPositionDf.loc[self.AutoPositionDf['ExecutionID'] == ExecutionID, 'hold'] = qtyhold - qty
                    self.AutoPositionDf.loc[self.AutoPositionDf['ExecutionID'] == ExecutionID, 'qty'] = 0
                    self.AutoPositionDf.loc[self.AutoPositionDf['orderId'] == orderId, 'price'] = price
            if type(side) is int:
                side = str(side)
            if side == SIDES['売']:
                self.longPosition = self.longPosition - qty
            else:
                self.shortPosition = self.shortPosition - qty

            if self.shortPosition == 0 and self.longPosition == 0:
                self.marketPosition = 0
            elif self.shortPosition != 0 and self.longPosition == 0:
                self.marketPosition = -1
            elif self.shortPosition == 0 and self.longPosition != 0:
                self.marketPosition = 1
            else:
                # 両建ての場合はmarketpositionは未定値10を指す
                self.marketPosition = 10
            mkpositon = str(self.marketPosition)
            lposition = str(self.longPosition)
            sposition = str(self.shortPosition)
            # 自動取引データの保存
            self.AutoPositionDf.to_csv(AutoTradeList, index=False)
            self.handler(self.handMessage,
                         self.datetime_now + '　marketposition:' + mkpositon + ' longposition:' + lposition + ' shortposition:' + sposition)
        self.handler(self.handMessage, self.datetime_now + '　返済約定')
        return

    def tradStop(self):
        ctx["stop"] = True

    def run(self):
        # ローソク足作成と予測をしトレードシグナルを作成する self.datetime_now文字型
        global ctx
        base_time = time.time()
        while True:
            if ctx["stop"]:  # main側から終了を指示されたら終了
                break
            self.datetime_now = datetime.now().replace(microsecond=0).strftime('%y-%m-%d %H:%M %S')
            self.time_now = datetime.now().time().replace(microsecond=0)
            # print('トレードループ', self.time_now)  # 1分ごとに表示
            # 時間をラベルに書き込む
            # self.time.set(self.datetime_now )
            # 祝祭日、日曜日、の取引は行わない
            if self.holiday_test:
                self.ExchangeOpen = True
                # print(str(self.time_now), '休日テスト中')
            else:
                self.ExchangeOpen = not self.isHoliday(self.time_now, self.night_end)
            if self.ExchangeOpen:
                # 約定照会約定処理
                if len(self.OrderList) != 0:
                    # 約定照会処理
                    AutoType = 0
                    inquiry = 0
                    order = object
                    side = ""
                    tradetype = 0
                    ExecutionID = None
                    status, orders = self.get_orders()
                    if status == 200:
                        # 発注リストチェック
                        # 同じ発注リストorderIdと発注照会orderIdかチェック
                        # forループ内でorderListを削除するのでorderListのコピーを使用する
                        orderListbak = self.OrderList.copy()
                        for key in orderListbak.keys():
                            # OrderListからorderIdを取得する
                            # print(key)
                            for order in orders:
                                if order['ID'] == key:
                                    AutoType = orderListbak[key]['AutoType']
                                    tradetype = orderListbak[key]['TradeType']
                                    ExecutionID = orderListbak[key]['ExecutionID']
                                    CashMargin = order['CashMargin']
                                    side = order['Side']
                                    orderState = order['State']
                                    # 約定照会詳細データ検索
                                    for Detail in order['Details']:
                                        if Detail['State'] == 4:
                                            # 注文エラー
                                            print("注文エラー")
                                            self.cancel_updada(key)
                                        elif Detail['State'] == 3 and Detail['RecType'] == 6:
                                            print("注文キャンセル")
                                            self.cancel_updada(key)
                                        elif Detail['State'] == 3 and Detail['RecType'] == 7:
                                            print("注文失効　期限切れ")
                                            self.cancel_updada(key)
                                        elif Detail['State'] == 3 and Detail['RecType'] == 8:
                                            if CashMargin == CASHMARGIN['新規']:
                                                # 同じSeqNum番号が約定リストに有るかチェックしない場合はリストに追加する
                                                if self.checklist(key, Detail, AutoType, tradetype, side, ExecutionID,
                                                                  CashMargin):
                                                    self.position_append(key, order['State'], Detail, AutoType,
                                                                         tradetype, side)
                                            elif CashMargin == CASHMARGIN['返済']:
                                                if self.checklist(key, Detail, AutoType, tradetype, side, ExecutionID,
                                                                  CashMargin):
                                                    self.psition_updata(key, Detail, AutoType, tradetype, side,
                                                                        ExecutionID)
                                        else:
                                            pass
                                    #  全約定,取り消し、失効したときorderListと明細リスt削除する
                                    if order['State'] == 5:
                                        del self.OrderList[key]
                                        del self.contractList[key]
                                else:
                                    pass
                    else:
                        self.handler(self.handMessage, self.datetime_now + '　Order 取得エラー')
                else:
                    pass
                    # print("order listはありません。")
            else:
               print(str(self.time_now), '本日取引場は休場です。')

            # alert　警戒　モニター
            self.loopalert += 1

            next_time = ((base_time - time.time()) % self.interval) or self.interval
            time.sleep(next_time)

if __name__ == '__main__':
    trad = trade()
    time.sleep(3)
    trad.start()
    print('パスワード：', trad.apiPassword)
    count = 0
    while True:
        print('busy')
        time.sleep(5)
        count += 1