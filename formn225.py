
from tkinter import *    #tk.xxxx と記述しなくて良い　
from tkinter import ttk, scrolledtext

# 売買区分辞書の定義
SIDES = {
    '売': '1',
    '買': '2'
    }
imagemarupath = "C:/Users/takao2/n225_trade/datas/maru.gif"
imagegrrenpath = "C:/Users/takao2/n225_trade/datas/grren.gif"
imageredpath = "C:/Users/takao2/n225_trade/datas/red.gif"


class formn225(Frame):
    def __init__(self, master=None):
        super().__init__(master, height=765, width=650)
        # master.geometry("600x500")
        self.master.title("tradn225m")
        self.master.iconbitmap('C:/Users/takao2/n225_trade/datas/dollar(128).ico')
        # イベント変数初期化 callback 関数を割り振る
        # GUI 属性
        # 警戒アラート表示ラベル
        self.imagemaru = PhotoImage(file=imagemarupath)
        self.imagegrren = PhotoImage(file=imagegrrenpath)
        self.imagered = PhotoImage(file=imageredpath)
        self.testButton = StringVar()
        self.auto = StringVar()
        self.Verifystr = StringVar()
        self.spinval1 = IntVar()
        self.spinval2 = IntVar()
        self.cmb1 = StringVar()
        # コンボ初期化
        self.cblist1 = ["先物", "NEC", "その他"]
        self.cmb2 = StringVar()
        self.cblist2 = ["日中", "夜間", "日通し"]
        self.rdovar = IntVar()
        self.APIpass = StringVar()
        self.xAPIkey = StringVar()
        self.StrtegyName = StringVar()
        self.entryDate = StringVar()
        self.curenPrice = IntVar()
        self.entrySign = StringVar()
        self.entryPrice = StringVar()
        self.symbol = StringVar()
        self.symbolname = StringVar()
        self.padX = 5  # パッテェング　ピックセル
        # 注文関連変数
        self.orderType = 1
        self.orderside = ""
        self.currentid=''
        self.infobox1item = 0
        self.infobox2item = 0
        self.create_widgets()
        self.prevprice = 0
        # self.askprice = IntVar()
        self.asksign = 0
        # self.bidprice = IntVar()
        self.bidsign = 0

    def create_widgets(self):
        self.askprice = IntVar()
        self.bidprice = IntVar()
        self.testButton.set('再接続')
        self.Verifystr.set("検証")
        self.auto.set("手動")
        # Spinbox 初期化
        self.spinval1.set(1)
        # 初期値は成行なのでprice は''にする
        self.spinval2.set(0)
        self.cmb1.set("先物")
        self.cmb2.set("日中")
        # ラジオボタンの初期化 成行にチェックする
        self.rdovar.set(2)      #初期化　対当
        # ラベルフレームの作成
        # frame = LabelFrame(self, bd=2, relief="ridge", text="menu")
        # frame.pack(fill="x")
        # ------- 変数の初期化 ------
        self.APIpass.set("takaotest")       #検証用パスワード
        self.xAPIkey.set("xAPIkey")
        self.StrtegyName.set("Strategy name")
        self.entryDate.set("YY/MM/DD")
        self.curenPrice.set(0)
        self.entrySign.set("無し")
        self.entryPrice.set("123456")

        self.askprice.set(0)
        self.bidprice.set(0)
        # フレームの作成（フレームをrootに配置,フレーム淵を2pt,フレームの形状をridge）
        # self.frame = Frame(self,height=500, width=600, bd=2, relief="ridge")
        # フレームを画面に配置し、横方向に余白を拡張する
        # --------- 全ウィジットの定義　----------
        # ラベル
        self.lbclient = Label(self,text = 'Push配信')
        self.lbtrade = Label(self,text = 'トレード')
        # 警戒アラートサインイメージ表示
        self.lbtrade_alert = Label(self,image = self.imagemaru)
        self.lbclient_alert = Label(self, image= self.imagemaru)
        self.lbAPIpass = Label(self, textvariable=self.APIpass)
        self.lbxAPIkey = Label(self, textvariable=self.xAPIkey)
        # ボタン定義 Verification(検証ボタン）
        self.vrfyButton = Button(self, textvariable=self.Verifystr, fg="red", command=self.verifybtn)
        self.tknButton = Button(self, text="認証", fg="red", command=self.apiTokn)
        # マルチチャート関連 戦略名、エントリー日付、時間、サイン、エントリー価格
        self.lbStrtgy = Label(self, textvariable=self.StrtegyName)
        self.lbEntDate = Label(self, textvariable=self.entryDate)
        self.lbcurentPrice = Label(self, textvariable=self.curenPrice)
        self.lbSign = Label(self, textvariable=self.entrySign)
        self.lbEntPrice = Label(self, textvariable=self.entryPrice)
        # 最良買気配値
        self.lbaskPrice = Label(self, textvariable=self.askprice)
        self.lbbidPrice = Label(self, textvariable=self.bidprice)
        # 自動/手動切り替えボタン　トグル動作すす　自動　-> 手動
        self.button1 = Button(self, textvariable=self.auto, fg="red", height=1, width=5, command=self.btn1_click)
        self.button2 = Button(self, text="売注文", height=1, width=5, command=self.btn2_click)
        self.button3 = Button(self, text="買注文", height=1, width=5, command=self.btn3_click)
        self.button4 = Button(self, text="返済", height=1, width=5, command=self.btn4_click)
        self.button5 = Button(self, text="キャンセル", height=1, width=8, command=self.btn5_click)
        self.button6 = Button(self, textvariable=self.testButton, height=1, width=8, command=self.btn6_click)
        # コンボボックスの定義
        # 銘柄　konbo1、取引区分 konbo2（日中／夜間／日通し）
        # self.combo1 = ttk.Combobox(self, textvariable=self.cmb1,values=self.cblist1,justify=CENTER,width=8)
        # コンボをラベルに変更する
        self.lbsymbol = Label(self, textvariable=self.symbol)
        self.lbsymbolname = Label(self, textvariable=self.symbolname)
        self.combo2 = ttk.Combobox(self, textvariable=self.cmb2, values=self.cblist2, justify=CENTER, width=8)
        # ラジオボタン　指値･成行
        self.rdo1 = Radiobutton(self, value=0, variable=self.rdovar, text='指値', command=self.rdbutton)
        # rdo1.place(x=70, y=40)
        self.rdo2 = Radiobutton(self, value=1, variable=self.rdovar, text='成行', command=self.rdbutton)
        # rdo2.place(x=70, y=70)
        self.rdo3 = Radiobutton(self, value=2, variable=self.rdovar, text='対当値', command=self.rdbutton)
        # rdo3.place(x=70, y=100)

        # 注文枚数,注文価格 incrementはn225ミニで５に設定
        # justify文字位置指定・左寄せtk.LEFT、中央寄せtk.CENTER、右寄せtk.RIGHTから指定
        self.contract = ttk.Spinbox(self,
                                justify=CENTER,
                                textvariable=self.spinval1,
                                from_=0,
                                to=10,
                                increment=1,
                                width=8
                                )

        self.orderPrice = ttk.Spinbox(self,
                                justify=CENTER,
                                textvariable=self.spinval2,
                                from_=0,
                                to=50000,
                                increment=5,
                                width=10,
                                command=self.SetcurentPrice)

        # 発注情報、約定情報 表示行数　5
        self.Treeview1 = ttk.Treeview(self, height=5, padding=10)
        # 仮想イベントをバインドする　行が選択されたときイベント発生する
        self.Treeview1.bind("<<TreeviewSelect>>", self.tree_select)
        # 列インデックスの作成
        self.Treeview1["columns"] = (1, 2, 3, 4, 5, 6, 7, 8,9)
        # 表スタイルの設定(headingsはツリー形式ではない、通常の表形式)
        self.Treeview1["show"] = "headings"
        # 各列の設定(インデックス,オプション(今回は幅を指定))
        self.Treeview1.column(1, width=50, anchor='c')
        self.Treeview1.column(2, width=100, anchor='c')
        self.Treeview1.column(3, width=25, anchor='c')
        self.Treeview1.column(4, width=25, anchor='c')
        self.Treeview1.column(5, width=55, anchor='c')
        self.Treeview1.column(6, width=40, anchor='c')
        self.Treeview1.column(7, width=70, anchor='c')
        self.Treeview1.column(8, width=40, anchor='c')
        self.Treeview1.column(9, width=200, anchor='c')
        # 各列のヘッダー設定(インデックス,テキスト)
        self.Treeview1.heading(1, text="取引")
        self.Treeview1.heading(2, text="　日　時　")
        self.Treeview1.heading(3, text="注")
        self.Treeview1.heading(4, text="文")
        self.Treeview1.heading(5, text="状態")
        self.Treeview1.heading(6, text="枚数")
        self.Treeview1.heading(7, text="注文値")
        # 約定枚数追加　2021.4/3
        self.Treeview1.heading(8,text="約定数")
        self.Treeview1.heading(9, text="注文番号")
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.Treeview1.yview)
        self.Treeview1['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.place(x=610, y=300, height=150)

        self.Treeview2 = ttk.Treeview(self, height=5, padding=5)
        # 列インデックスの作成
        self.Treeview2["columns"] = (1, 2, 3, 4, 5, 6, 7, 8)
        # 表スタイルの設定(headingsはツリー形式ではない、通常の表形式)
        self.Treeview2["show"] = "headings"
        # 各列の設定(インデックス,オプション(今回は幅を指定))
        self.Treeview2.column(1,  width=50, anchor='c')
        self.Treeview2.column(2, width=100, anchor='c')
        self.Treeview2.column(3, width=40, anchor='c')
        self.Treeview2.column(4, width=40, anchor='c')
        self.Treeview2.column(5, width=40, anchor='c')
        self.Treeview2.column(6, width=70, anchor='c')
        self.Treeview2.column(7, width=70, anchor='c')
        self.Treeview2.column(8, width=150, anchor='c')
        # 各列のヘッダー設定(インデックス,テキスト)
        self.Treeview2.heading(1, text="取引")
        self.Treeview2.heading(2, text="　日　時　")
        self.Treeview2.heading(3, text="売買")
        self.Treeview2.heading(4, text="保有")
        self.Treeview2.heading(5, text="注文")
        self.Treeview2.heading(6, text="約定値")
        self.Treeview2.heading(7, text="評価損益")
        self.Treeview2.heading(8, text="ExecutionI")
        # Scrollbar
        self.scrollbar2 = ttk.Scrollbar(self, orient=VERTICAL, command=self.Treeview2.yview)
        self.Treeview2['yscrollcommand'] = self.scrollbar2.set
        self.scrollbar2.place(x=568, y=450, height=140)

        # status　スクロールテキストボックス作成 文字数:40 行数:7 編集不可 state=DISABLED,
        self.Statustxt = scrolledtext.ScrolledText(self, wrap=WORD, state=DISABLED, width=55,
                                                   height=7, font=('Helvetica', 12))
        # self.Statustxt["state"]= NORMAL   #編集可能にし文字列を書き込む
        # self.Statustxt.insert(1.0, "Hello!")
        # self.Statustxt["state"] = DISABLED     # 編集不可 state=DISABLEDに設定

        # --------- 全ウィジットの配置　----------
        self.pack(fill="x")
        self.vrfyButton.place(x=5, y=5)
        self.tknButton.place(x=50, y=5)
        self.lbAPIpass.place(x=100, y=5)
        self.lbxAPIkey.place(x=200, y=5)
        # アラートラベル表示
        self.lbclient.place(x = 470,y= 5)
        self.lbtrade.place(x= 540,y= 5)
        self.lbclient_alert.place(x= 500,y= 35)
        self.lbtrade_alert.place(x=550,y = 35)
        # Mulityarts date
        self.lbStrtgy.place(x=5, y=50)
        self.lbEntDate.place(x=200, y=50)
        self.lbSign.place(x=340, y=50)
        self.lbEntPrice.place(x=400, y=50)
        # 銘柄、取引区分（日中、夜間
        # self.combo1.place(x=5,y=100)
        self.lbsymbolname.place(x=5, y=100)
        self.lbsymbol.place(x=150, y=100)
        self.combo2.place(x=250, y=100)
        self.lbcurentPrice.place(x=400, y=100)
        self.rdo1.place(x=5, y=150)
        self.rdo2.place(x=100, y=150)
        self.rdo3.place(x=200, y=150)
        self.button1.place(x=310, y=150)
        self.button6.place(x=400, y=150)
        self.contract.place(x=5, y=200)
        self.orderPrice.place(x=150, y=200)

        self.lbbidPrice.place(x= 310,y=200)
        self.lbaskPrice.place(x=410, y=200)

        self.button2.place(x=10, y=250, width=50)
        self.button3.place(x=110, y=250)
        self.button4.place(x=210, y=250)
        self.button5.place(x=310, y=250, width=80)

        self.Treeview1.place(x=0+self.padX, y=300)
        self.Treeview2.place(x=0+self.padX, y=450)
        self.Statustxt.place(x=0+self.padX, y=590)
        # ---- ウィジット属性設定
        # 成行設定のときspinbox2は書き込み禁止
        self.orderPrice["state"] = DISABLED
        self.button6["state"] = DISABLED

        # self.scrollbar.place(x=400,y=550)

    # ------ ウィジット(ボタン,spinbox等)のクリックイベント ----
    def verifybtn(self):
        if self.Verifystr.get() == "検証":
            self.Verifystr.set("本番")
            # objから本番用apiパスワード取得する
            # apiPass = self.objApi['apiPassWord'][0]

            # ラベル表示
            # self.APIpass.set(apiPass)
            self.VerifyUrl = True
        else:
            self.Verifystr.set("検証")
            # objから検証用apiパスワード取得する
            # apiPass = self.objApi['apiPassWord'][1]
            # self.APIpass.set(apiPass)
            self.VerifyUrl = False

    def apiTokn(self):
        pass

    def btn6_click(self):
        pass

    def btn1_click(self):
        pass

    def btn2_click(self):
        pass

    def btn3_click(self):
        pass

    def btn4_click(self):
        # 返済発注 成行注文に固定する
        pass

    def btn5_click(self):
        # キャンセル
        pass

    def rdbutton(self):
        # ラジオボタンイベント　成行の場合price spiboxをクリアして使えなくする
        if self.rdovar.get() != 0:
            self.spinval2.set(0)
            self.orderPrice["state"] = DISABLED
        else:
            self.orderPrice["state"] = NORMAL

    def tree_select(self, event):
        pass

    def SetcurentPrice(self):
        pass


def main():
    win = Tk()
    app = formn225()
    app.mainloop()


if __name__ == '__main__':
    main()
