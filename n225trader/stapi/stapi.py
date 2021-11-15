# -*- coding: utf-8 -*-
import yaml
import sys
import json
import urllib.request
import urllib.parse
import urllib.error


class stapi:
    def __init__(self):
        self.domain = "http://localhost:"
        self.wsDomain = "ws://localhost:"
        self.Port = ""
        self.apiPassword = ''
        self.xApikey = ''

    def token(self, ReqestBody):  # トークンを取得する。取得する度・またはkabuステーション再起動の度に変わる。
        # パスワードは引数で渡す(今は違う後日変更する）
        # 戻り値　string apikey番号　nullの場合はエラー
        result = []
        url = self.domain+self.Port + '/kabusapi/token'
        # ReqestBodyを文字型に変更する
        json_data = json.dumps(ReqestBody).encode('utf8')
        req = urllib.request.Request(url, json_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        try:
            with urllib.request.urlopen(req) as res:
                reason = res.reason
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            # HTTPError
            content = json.loads(e.read())
            result.append(content)
            status = content['Code']
            reason = content['Message']
        except Exception as e:
            print('ホスト以外のエラー： ', e)
            status = 0
            result.append(e)
        return status, result

    def sendorder(self, ReqestBody, xApikey):
        result = []
        json_data = json.dumps(ReqestBody).encode('utf-8')
        url = self.domain+self.Port + '/kabusapi/sendorder/future'
        req = urllib.request.Request(url, json_data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', self.xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            status = content['Code']
            result.append(content)
        except Exception as e:
            result.append(e)
            status = 0
        return status, result

    def cancelorder(self, ReqestBody, xApikey):
        result = []
        json_data = json.dumps(ReqestBody).encode('utf8')
        url = self.domain + self.Port + '/kabusapi/cancelorder'
        req = urllib.request.Request(url, json_data, method='PUT')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', self.xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            status = content['Code']
            result.append(content)
        except Exception as e:
            status = 0
            result.append(e)
        return status, result

    def ordes(self, Queryparam, xApikey):
        # 注文約定紹介
        result = []
        url = self.domain + self.Port + '/kabusapi/orders'
        params = {'product': 0, }
        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)), method='GET')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', self.xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            status = content['Code']
            result.append(content)
        except Exception as e:
            status = 0
            result.append(e)
        return status, result

    # 先物銘柄コード取得
    def symbolname(self, params, xApikey):
        # print('symbolName test',xApikey)
        result = []
        url = self.domain + self.Port + '/kabusapi/symbolname/future'
        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)), method='GET')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            print(e)
            content = json.loads(e.read())
            status = content['Code']
            result.append(content)
        except Exception as e:
            status = 0
            result.append(e)
        return status, result

    # 銘柄情報
    def symbol(self, symbol, exchange, xApikey):
        result = []
        # 引数作成
        param = symbol + '@' + exchange
        url = self.domain + self.Port + '/kabusapi/symbol/' + param
        req = urllib.request.Request(url, method='GET')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', self.xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            result.append(content)
            status = content['Code']
        except Exception as e:
            status = 0
            result.append(e)
        return status, result

    def wallet(self, xApikey):
        # 取引余力
        result = []
        url = self.domain + self.Port + '/kabusapi/wallet/future'
        req = urllib.request.Request(url, method='GET')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', self.xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            status = content['Code']
            result.append(content)
        except Exception as e:
            status = 0
            result.append(e)
        return status, result

    def positions(self, params, xApikey):
        #   残高照会 全て
        result = []
        url = self.domain + self.Port + '/kabusapi/positions'
        # params = {'product': 0, }
        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)), method='GET')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', self.xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            status = content['Code']
            result.append(content)
        except Exception as e:
            status = 0
            result.append(e)
        return status, result

    def board(self, symbol, exchange, xApikey):
        # 時価、板情報取得
        # 文字列の連結
        # path = {symbol}@{exchange} 例 '6701@1'
        result = []
        param = symbol + '@' + exchange
        url = self.domain + self.Port + '/kabusapi/board/'+param
        req = urllib.request.Request(url, method='GET')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', self.xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            status = content['Code']
            result.append(content)
        except Exception as e:
            status = 0
            result.append(e)
        return status, result

    def Register(self, ReqestBody, xApikey):
        # 本番／検証url設定
        result = []
        json_data = json.dumps(ReqestBody).encode('utf8')
        url = self.domain + self.Port + '/kabusapi/register'
        req = urllib.request.Request(url, json_data, method='PUT')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', self.xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            status = content['Code']
            result.append(content)
        except Exception as e:
            status = 0
            result.append(e)
        return status, result

    def Unregisterall(self, xApikey):
        # 登録リスト全部削除
        result = []
        url = self.domain + self.Port + 'kabusapi/unregister/all'
        req = urllib.request.Request(url, method='PUT')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-API-KEY', self.xApikey)
        try:
            with urllib.request.urlopen(req) as res:
                # print(res.status, res.reason)
                status = res.status
                content = json.loads(res.read())
                result.append(content)
        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            status = content['Code']
            result.append(content)
        except Exception as e:
            status = 0
            result.append(e)
        return status, result


# FunctionApi関数テスト用関数
def loadDefinition():  #C:/Users/takao2/rl-TradeNIKEI/myliblary/
    # obj = ""
    try:
        # with open('apiDefinitions.yaml', 'r') as file:
        with open('C:/Users/takao2/n225_trade/config/apidef.yaml', 'r') as file:
            obj = yaml.safe_load(file)
    except Exception as e:
        print('Exception occurred while loading YAML...', file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        return obj


if __name__ == '__main__':
    app = stapi()
    obj = loadDefinition()
    # Apiぴパスワード取得
    apiPass = app.apiPassword        # メソッドから取得
    # objよりReqestBody取得
    ReqestBody = obj['RequestToken']
    # APIPasswordキーのvalueを変更する
    ReqestBody['APIPassword'] = apiPass
    xApikey = app.token(ReqestBody)

    print(xApikey, type(xApikey))
    #ReqestBody作成
    ReqestBody = obj['RequestSendOrder']
    # ReqestBody['Password'] = 'takao102769'
    ReqestBody['Symbol'] = '8001'
    ReqestBody['Side'] = '2'
    ReqestBody['Qty'] = 100
    ReqestBody['Price'] = 23325
    ReqestBody['FrontOrderType'] = 20

    app.sendorder(ReqestBody, xApikey)
