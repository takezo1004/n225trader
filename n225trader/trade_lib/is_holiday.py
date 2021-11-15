# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta

import jpholiday as holiday


def is_holiday(time_now, night_end):
    time_now = time_now
    night_end_time = night_end
    #  曜日を取得する。「DayOfWeek.Saturday」となる。
    '''
        月=0,火=1, 水=2 木=3　金=4　土=5　日=6
        ライブラリ　判定方法
        jpholiday.is_holiday(datetime.date(2017, 1, 1))
    '''
    today = datetime.now().date()
    weekNumber = today.weekday()
    # 前日の日付取得する
    previous_day = (datetime.now() - timedelta(days=1)).date()  # // 前日
    # print(today,previous_day,weekNumber)

    marketClosed = False

    if weekNumber == 6:  # 日曜日は休業
        marketClosed = True
    if weekNumber == 0:   # 月曜日
        if holiday.is_holiday(today):
            marketClosed = True
        else:
            if time_now < night_end_time:  # ナイトセッションは取引しない
                marketClosed = True
    elif weekNumber == 5:  # // 土日は５時３０分から休み
        if holiday.is_holiday(previous_day):  # 前日祭日？
            marketClosed = True
        else:
            if time_now > night_end_time:
                marketClosed = True
    else:
        # 火, 水,木, 金
        if holiday.is_holiday(today):
            marketClosed = True
        else:
            if holiday.is_holiday(previous_day):  # 前日は休み
                if time_now < night_end_time:  # 夜間セッションは休み
                    marketClosed = True

    if marketClosed:
        pass
        # print('本日は休場です。')
    return marketClosed

