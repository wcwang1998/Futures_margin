import streamlit as st
import requests
from lxml import etree
import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(
    page_title="期貨保證金查詢",
    page_icon="random",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Created by Jack Wang.\n Likedin: https://www.linkedin.com/in/weichieh1998/"
     }
)

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# ---------------------------------- 爬蟲程式 --------------------------------- #

@st.cache(suppress_st_warning=True)
def Taiwan_ETF():
    #建構爬取網站及參數
    url = 'https://www.taifex.com.tw/cht/5/stockMargining'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }

    res = requests.post(url=url, headers=header)
    res.encoding='utf-8'

    #建立ETF類表格
    TW_ETF = pd.DataFrame(columns=['股票期貨英文代碼','股票期貨標的證券代號','股票期貨中文簡稱','股票期貨標的證券','結算保證金','維持保證金','原始保證金'], dtype='str')
    en_code = []
    tw_code = []
    tw_name = []
    tw_full_name = []
    clearing = []
    maintainance = []
    initial = []

    #用etree爬取商品別及保證金
    tree = etree.HTML(res.text)
    path = tree.xpath('/html/body/div[1]/div[4]/div[2]/div/div[2]/div[1]/table[2]/tbody/tr')

    for futures in path[1:len(path)]:
        td = futures.xpath('.//td')
        temp_en_code = td[1].text.replace(" ", "")
        temp_tw_code = td[2].text.replace(" ", "")
        temp_tw_name = td[3].text.replace(" ", "")
        temp_tw_full_name = td[4].text.replace(" ", "")
        temp_clearing = td[5].text.replace(" ", "")
        temp_maintainance = td[6].text.replace(" ", "")
        temp_initial = td[7].text.replace(" ", "")
        
        en_code.append(temp_en_code)
        tw_code.append(temp_tw_code)
        tw_name.append(temp_tw_name)
        tw_full_name.append(temp_tw_full_name)
        clearing.append(temp_clearing)
        maintainance.append(temp_maintainance)
        initial.append(temp_initial)

    #將list寫入TW_Index
    TW_ETF['股票期貨英文代碼'] = en_code
    TW_ETF['股票期貨標的證券代號'] = tw_code
    TW_ETF['股票期貨中文簡稱'] = tw_name
    TW_ETF['股票期貨標的證券'] = tw_full_name
    TW_ETF['結算保證金'] = clearing
    TW_ETF['維持保證金'] = maintainance
    TW_ETF['原始保證金'] = initial

    return TW_ETF

@st.cache(suppress_st_warning=True)
def Taiwan_Index():
    #建構爬取網站及參數
    url = 'https://www.taifex.com.tw/cht/5/indexMarging'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }
    data = {
        'origin': 'https://www.taifex.com.tw',
        'referer': 'https://www.taifex.com.tw/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
        }

    res = requests.post(url=url, headers=header, data=data)
    res.encoding='utf-8'

    #建立股價指數類表格
    TW_Index = pd.DataFrame(columns=['代碼','商品別','結算保證金','維持保證金','原始保證金'])
    name_id = []
    clearing = []
    maintainance = []
    initial = []

    #用etree爬取商品別及保證金
    tree = etree.HTML(res.text)
    path = tree.xpath('/html//div[@name="printhere"]//tr')

    #爬取後存入list
    for futures in path[1:len(path)]: 
        td = futures.xpath('./td') 
        temp_name_id = td[0].text 
        temp_clearing = td[1].text
        temp_maintainance = td[2].text
        temp_initial = td[3].text
        
        name_id.append(temp_name_id)
        clearing.append(temp_clearing)
        maintainance.append(temp_maintainance)
        initial.append(temp_initial)

    #期貨代碼list
    code_list = ['TX','MTX','*****','*****','*****','TE','ZEF','*****','*****','TF','ZFF','*****','*****','XIF','GTF','G2F','E4F','BTF','SOF','SHF','TJF','UDF','SPF','UNF','F1F']

    #將list寫入TW_Index
    TW_Index['商品別'] = name_id
    TW_Index['結算保證金'] = clearing
    TW_Index['維持保證金'] = maintainance
    TW_Index['原始保證金'] = initial
    TW_Index['代碼'] = code_list

    return TW_Index

@st.cache(suppress_st_warning=True)
def Taiwan_Stock():

    #建構爬取網站及參數
    url = 'https://www.taifex.com.tw/cht/5/stockMargining'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }

    res = requests.post(url=url, headers=header)
    res.encoding='utf-8'

    #建立股票類表格
    TW_Stock = pd.DataFrame(columns=['股票期貨英文代碼','股票期貨標的證券代號','股票期貨中文簡稱','股票期貨標的證券','保證金所屬級距','結算保證金適用比例','維持保證金適用比例','原始保證金適用比例'], dtype='str')
    en_code = []
    tw_code = []
    tw_name = []
    tw_full_name = []
    margin_level = []
    clearing_ptg = []
    maintainance_ptg = []
    initial_ptg = []

    #用etree爬取商品別及保證金
    tree = etree.HTML(res.text)
    path = tree.xpath('/html/body/div[1]/div[4]/div[2]/div/div[2]/div[1]/table[1]/tbody/tr')
        
    #爬取後存入list
    for futures in path[1:len(path)]: 
        td = futures.xpath('.//td') 
        temp_en_code = td[1].text.replace(" ", "")
        temp_tw_code = td[2].text.replace(" ", "")
        temp_tw_name = td[3].text.replace(" ", "")
        temp_tw_full_name = td[4].text.replace(" ", "")
        temp_margin_level = td[5].text.replace("\r\n                ", "")
        temp_clearing_ptg = td[6].text.replace(" ", "")
        temp_maintainance_ptg = td[7].text.replace(" ", "")
        temp_initial_ptg = td[8].text.replace(" ", "")
        
        en_code.append(temp_en_code)
        tw_code.append(temp_tw_code)
        tw_name.append(temp_tw_name)
        tw_full_name.append(temp_tw_full_name)
        margin_level.append(temp_margin_level)
        clearing_ptg.append(temp_clearing_ptg)
        maintainance_ptg.append(temp_maintainance_ptg)
        initial_ptg.append(temp_initial_ptg)

    #將list寫入TW_Index
    TW_Stock['股票期貨英文代碼'] = en_code
    TW_Stock['股票期貨標的證券代號'] = tw_code
    TW_Stock['股票期貨中文簡稱'] = tw_name
    TW_Stock['股票期貨標的證券'] = tw_full_name
    TW_Stock['保證金所屬級距'] = margin_level
    TW_Stock['結算保證金適用比例'] = clearing_ptg
    TW_Stock['維持保證金適用比例'] = maintainance_ptg
    TW_Stock['原始保證金適用比例'] = initial_ptg
    TW_Stock.loc[TW_Stock['保證金所屬級距'] == '', '保證金所屬級距'] = '*****' #把空白取代成*****

    return TW_Stock

@st.cache(suppress_st_warning=True)
def currency_rate():
    #爬外幣匯率
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"

    resp = requests.get(url)
    resp.encoding = 'utf-8'

    html = BeautifulSoup(resp.text, "lxml")
    rate_table = html.find('table', attrs={'title':'牌告匯率'}).find('tbody').find_all('tr')

    buy_list = []
    sell_list= []
    currency_list = []

    for rate in rate_table:
        prices = rate.find_all("td")
        buy_list.append(prices[1].text)
        sell_list.append(prices[2].text)

        currency_name = rate.find_all(class_="visible-phone print_hide")
        currency_list.append(currency_name[1].text.strip())

    df = pd.DataFrame()
    df["貨幣"] = currency_list
    df["即期買入"] = buy_list
    df["即期賣出"] = sell_list
    # display(df)

    return df

df = currency_rate()

@st.cache(suppress_st_warning=True)
def oversea_USA_EUROPE():

    #建構爬取網站及參數
    url = 'https://www.capitalfutures.com.tw/product/deposit.asp?xy=2&xt=2'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }

    res = requests.get(url=url, headers=header)
    res.encoding = res.apparent_encoding

    # print(res.text)
    
    #建立USA_EUROPE表格
    USA_EUROPE = pd.DataFrame(columns=['代號','商品種類','幣別','原始保證金','維持保證金','當沖保證金','原始保證金(台幣)'], dtype='str')
    en_code = []
    tw_name = []
    currency = []
    initial = []
    maintainance = []
    daytrade = []
    tw_money = []

    #用正則表達式爬取

    patt = r'<tr bgcolor=".*?">.*?<td align="center">(.*?)</td>.*?<td align="center">(.*?)</td>.*?<td align=center>(.*?)</td>.*?<td align=right>(.*?)</td>.*?<td align=right>(.*?)</td>.*?<td align=right>(.*?)</td>.*?</tr>'
    res_1 = re.findall(pattern=patt, string=res.text, flags=re.S)
    
    for futures in res_1:
        temp_en_code = futures[0].replace(" ", "")
        temp_tw_name = futures[1].replace(" ", "")
        temp_currency = futures[2].replace(" ", "")
        temp_initial = futures[3].replace(" ", "")
        temp_maintainance = futures[4].replace(" ", "")
        temp_daytrade = futures[5].replace(" ", "")

        #將保證金計算為台幣

        if temp_currency == 'USD':
            temp_tw_money = int(temp_initial) * float(df.iloc[0,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[2,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'JPY':
            temp_tw_money = int(temp_initial) * float(df.iloc[7,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'EUR':
            temp_tw_money = int(temp_initial) * float(df.iloc[14,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[6,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'AUD':
            temp_tw_money = int(temp_initial) * float(df.iloc[3,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'CHF':
            temp_tw_money = int(temp_initial) * float(df.iloc[6,2])
            temp_tw_money_int = int(temp_tw_money)

        en_code.append(temp_en_code)
        tw_name.append(temp_tw_name)
        currency.append(temp_currency)
        initial.append(temp_initial)
        maintainance.append(temp_maintainance)
        daytrade.append(temp_daytrade)
        tw_money.append(str(temp_tw_money_int))

    #將list寫入TW_Index
    USA_EUROPE['代號'] = en_code
    USA_EUROPE['商品種類'] = tw_name
    USA_EUROPE['幣別'] = currency
    USA_EUROPE['原始保證金'] = initial
    USA_EUROPE['維持保證金'] = maintainance
    USA_EUROPE['當沖保證金'] = daytrade
    USA_EUROPE['原始保證金(台幣)'] = tw_money

    return USA_EUROPE

@st.cache(suppress_st_warning=True)
def oversea_Singapore():

    #建構爬取網站及參數
    url = 'https://www.capitalfutures.com.tw/product/deposit_sp.asp?xy=2&xt=4'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }

    res = requests.get(url=url, headers=header)
    res.encoding = res.apparent_encoding

    # print(res.text)

    #建立USA_EUROPE表格
    db_singapore = pd.DataFrame(columns=['代號','商品種類','幣別','原始保證金','維持保證金','當沖保證金','原始保證金(台幣)'], dtype='str')
    en_code = []
    tw_name = []
    currency = []
    initial = []
    maintainance = []
    daytrade = []
    tw_money = []

    #用正則表達式爬取

    patt = r'<tr bgcolor=".*?">.*?<td align="center">(.*?)</td>.*?<td align="center">(.*?)</td>.*?<td align=center>(.*?)</td>.*?<td align=right>(.*?)</td>.*?<td align=right>(.*?)</td>.*?<td align=right>(.*?)</td>.*?</tr>'
    res_1 = re.findall(pattern=patt, string=res.text, flags=re.S)
    
    for futures in res_1:
        temp_en_code = futures[0].replace(" ", "")
        temp_tw_name = futures[1].replace(" ", "")
        temp_currency = futures[2].replace(" ", "")
        temp_initial = futures[3].replace(",", "")
        temp_maintainance = futures[4].replace(",", "")
        temp_daytrade = futures[5].replace(",", "")
        
        #將保證金計算為台幣

        if temp_currency == 'USD':
            temp_tw_money = int(temp_initial) * float(df.iloc[0,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[2,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'JPY':
            temp_tw_money = int(temp_initial) * float(df.iloc[7,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'EUR':
            temp_tw_money = int(temp_initial) * float(df.iloc[14,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[6,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'AUD':
            temp_tw_money = int(temp_initial) * float(df.iloc[3,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'SGD':
            temp_tw_money = int(temp_initial) * float(df.iloc[5,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'RMB':
            temp_tw_money = int(temp_initial) * float(df.iloc[18,2])
            temp_tw_money_int = int(temp_tw_money)
            
        en_code.append(temp_en_code)
        tw_name.append(temp_tw_name)
        currency.append(temp_currency)
        initial.append(temp_initial)
        maintainance.append(temp_maintainance)
        daytrade.append(temp_daytrade)
        tw_money.append(str(temp_tw_money_int))

    #將list寫入TW_Index
    db_singapore['代號'] = en_code
    db_singapore['商品種類'] = tw_name
    db_singapore['幣別'] = currency
    db_singapore['原始保證金'] = initial
    db_singapore['維持保證金'] = maintainance
    db_singapore['當沖保證金'] = daytrade
    db_singapore['原始保證金(台幣)'] = tw_money

    return db_singapore

@st.cache(suppress_st_warning=True)
def oversea_HongKong():

    #建構爬取網站及參數
    url = 'https://www.capitalfutures.com.tw/product/deposit-hk.asp?xy=2&xt=5'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }

    res = requests.get(url=url, headers=header)
    res.encoding = res.apparent_encoding

    # print(res.text)

    #建立USA_EUROPE表格
    db_hongkong = pd.DataFrame(columns=['代號','商品種類','幣別','原始保證金','維持保證金','當沖保證金','原始保證金(台幣)'], dtype='str')
    en_code = []
    tw_name = []
    currency = []
    initial = []
    maintainance = []
    daytrade = []
    tw_money = []

    #用正則表達式爬取

    patt = r'<tr bgcolor=".*?">.*?<td align="center">(.*?)</td>.*?<td align="center">(.*?)</td>.*?<td align=center>(.*?)</td>.*?<td align=right>(.*?)</td>.*?<td align=right>(.*?)</td>.*?<td align=right>(.*?)</td>.*?</tr>'
    res_1 = re.findall(pattern=patt, string=res.text, flags=re.S)
    
    for futures in res_1:
        temp_en_code = futures[0].replace(" ", "")
        temp_tw_name = futures[1].replace(" ", "")
        temp_currency = futures[2].replace(" ", "")
        temp_initial = futures[3].replace(",", "")
        temp_maintainance = futures[4].replace(",", "")
        temp_daytrade = futures[5].replace(",", "")
        
        #將保證金計算為台幣

        if temp_currency == 'USD':
            temp_tw_money = int(temp_initial) * float(df.iloc[0,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[2,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'JPY':
            temp_tw_money = int(temp_initial) * float(df.iloc[7,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'EUR':
            temp_tw_money = int(temp_initial) * float(df.iloc[14,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[6,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'AUD':
            temp_tw_money = int(temp_initial) * float(df.iloc[3,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'SGD':
            temp_tw_money = int(temp_initial) * float(df.iloc[5,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'RMB':
            temp_tw_money = int(temp_initial) * float(df.iloc[18,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'HKD':
            temp_tw_money = int(temp_initial) * float(df.iloc[1,2])
            temp_tw_money_int = int(temp_tw_money)
            
        en_code.append(temp_en_code)
        tw_name.append(temp_tw_name)
        currency.append(temp_currency)
        initial.append(temp_initial)
        maintainance.append(temp_maintainance)
        daytrade.append(temp_daytrade)
        tw_money.append(str(temp_tw_money_int))

    #將list寫入TW_Index
    db_hongkong['代號'] = en_code
    db_hongkong['商品種類'] = tw_name
    db_hongkong['幣別'] = currency
    db_hongkong['原始保證金'] = initial
    db_hongkong['維持保證金'] = maintainance
    db_hongkong['當沖保證金'] = daytrade
    db_hongkong['原始保證金(台幣)'] = tw_money

    # display(db_hongkong)

    return db_hongkong

@st.cache(suppress_st_warning=True)
def oversea_Japan_TOCOM():

    #建構爬取網站及參數
    url = 'https://www.capitalfutures.com.tw/product/deposit-jp.asp?xy=2&xt=3'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }

    res = requests.get(url=url, headers=header)
    res.encoding = res.apparent_encoding

    # print(res.text)

    #建立TOCOM表格
    db_Tocom = pd.DataFrame(columns=['代號','商品種類','幣別','原始保證金','維持保證金','原始保證金(台幣)'], dtype='str')
    en_code = []
    tw_name = []
    currency = []
    initial = []
    maintainance = []
    tw_money = []

    #用正則表達式爬取TOCOM

    patt = r'<TR bgcolor=".*?">.*?<TD align=middle rowSpan=2 width="70">(.*?)</TD>.*?<TD align=middle rowSpan=2 width="69">(.*?)</TD>.*?<TD align=middle rowSpan=2 width="70">(.*?)</TD>.*?<TD align=middle width="122">.*?</TD>.*?<td align="right" width="81">(.*?)</td>.*?<td align="right" width="85">(.*?)</td>.*?</TR>'
    res_1 = re.findall(pattern=patt, string=res.text, flags=re.S)
    
    for futures in res_1:
        temp_en_code = futures[0].replace(" ", "")
        temp_tw_name = futures[1].replace(" ", "")
        temp_currency = futures[2].replace(" ", "")
        temp_initial = futures[3].replace(",", "")
        temp_maintainance = futures[4].replace(",", "")
        
        #將保證金計算為台幣

        if temp_currency == 'USD':
            temp_tw_money = int(temp_initial) * float(df.iloc[0,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[2,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'JPY':
            temp_tw_money = int(temp_initial) * float(df.iloc[7,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'EUR':
            temp_tw_money = int(temp_initial) * float(df.iloc[14,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[6,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'AUD':
            temp_tw_money = int(temp_initial) * float(df.iloc[3,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'SGD':
            temp_tw_money = int(temp_initial) * float(df.iloc[5,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'RMB':
            temp_tw_money = int(temp_initial) * float(df.iloc[18,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'HKD':
            temp_tw_money = int(temp_initial) * float(df.iloc[1,2])
            temp_tw_money_int = int(temp_tw_money)
            
        en_code.append(temp_en_code)
        tw_name.append(temp_tw_name)
        currency.append(temp_currency)
        initial.append(temp_initial)
        maintainance.append(temp_maintainance)
        tw_money.append(str(temp_tw_money_int))
    
    #將list寫入TW_Index
    db_Tocom['代號'] = en_code
    db_Tocom['商品種類'] = tw_name
    db_Tocom['幣別'] = currency
    db_Tocom['原始保證金'] = initial
    db_Tocom['維持保證金'] = maintainance
    db_Tocom['原始保證金(台幣)'] = tw_money

    # display(db_Tocom)

    return db_Tocom

@st.cache(suppress_st_warning=True)
def oversea_Japan_OSE():

    #建構爬取網站及參數
    url = 'https://www.capitalfutures.com.tw/product/deposit-jp.asp?xy=2&xt=3'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }

    res = requests.get(url=url, headers=header)
    res.encoding = res.apparent_encoding

    #建立OSE表格
    db_OSE = pd.DataFrame(columns=['代號','商品種類','幣別','原始保證金','維持保證金','當沖保證金','原始保證金(台幣)'], dtype='str')
    en_code_2 = []
    tw_name_2 = []
    currency_2 = []
    initial_2 = []
    maintainance_2 = []
    daytrade_2 = []
    tw_money_2 = []

    #用正則表達式爬取

    patt_2 = r'<tr bgcolor=".*?">.*?<td align="center">(.*?)</td>.*?<td align="center">(.*?)</td>.*?<td align=center>(.*?)</td>.*?<td align=right>(.*?)</td>.*?<td align=right>(.*?)</td>.*?<td align=right>(.*?)</td>.*?</tr>'
    res_2 = re.findall(pattern=patt_2, string=res.text, flags=re.S)

    for futures in res_2:
        temp_en_code = futures[0].replace(" ", "")
        temp_tw_name = futures[1].replace(" ", "")
        temp_currency = futures[2].replace(" ", "")
        temp_initial = futures[3].replace(",", "")
        temp_maintainance = futures[4].replace(",", "")
        temp_daytrade = futures[5].replace(",", "")
        
        #將保證金計算為台幣

        if temp_currency == 'USD':
            temp_tw_money = int(temp_initial) * float(df.iloc[0,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[2,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'JPY':
            temp_tw_money = int(temp_initial) * float(df.iloc[7,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'EUR':
            temp_tw_money = int(temp_initial) * float(df.iloc[14,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'GBP':
            temp_tw_money = int(temp_initial) * float(df.iloc[6,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'AUD':
            temp_tw_money = int(temp_initial) * float(df.iloc[3,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'SGD':
            temp_tw_money = int(temp_initial) * float(df.iloc[5,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'RMB':
            temp_tw_money = int(temp_initial) * float(df.iloc[18,2])
            temp_tw_money_int = int(temp_tw_money)
        elif temp_currency == 'HKD':
            temp_tw_money = int(temp_initial) * float(df.iloc[1,2])
            temp_tw_money_int = int(temp_tw_money)
            
        en_code_2.append(temp_en_code)
        tw_name_2.append(temp_tw_name)
        currency_2.append(temp_currency)
        initial_2.append(temp_initial)
        maintainance_2.append(temp_maintainance)
        daytrade_2.append(temp_daytrade)
        tw_money_2.append(str(temp_tw_money_int))

    #將list寫入TW_Index
    db_OSE['代號'] = en_code_2
    db_OSE['商品種類'] = tw_name_2
    db_OSE['幣別'] = currency_2
    db_OSE['原始保證金'] = initial_2
    db_OSE['維持保證金'] = maintainance_2
    db_OSE['當沖保證金'] = daytrade_2
    db_OSE['原始保證金(台幣)'] = tw_money_2

    # display(db_OSE)

    return db_OSE

@st.cache(suppress_st_warning=True)
def today():
    mask = '%Y/%m/%d'
    dte = datetime.now().strftime(mask)
    fname = "資料日期：{}".format(dte)

    return fname

# ---------------------------------- sidebar --------------------------------- #

st.sidebar.title("請選擇欲查詢的保證金")

region = st.sidebar.selectbox(
    '國家或區域：',
    ['Taiwan', 'USA and Europe', 'Singapore', 'Hongkong', 'Japan'])

if region == 'Taiwan':
    option = st.sidebar.selectbox(
            '類別：',
            ['指數期貨', '股票期貨', 'ETF期貨'])
elif region == 'USA and Europe':
    option = st.sidebar.selectbox(
            '類別：',
            ['USA and Europe'])
elif region == 'Singapore':
    option = st.sidebar.selectbox(
            '類別：',
            ['Singapore'])
elif region == 'Hongkong':
    option = st.sidebar.selectbox(
            '類別：',
            ['Hongkong'])
elif region == 'Japan':
    option = st.sidebar.selectbox(
            '類別：',
            ['TOCOM', 'OSE'])

# ---------------------------------- body --------------------------------- #

TW_etf = Taiwan_ETF()
TW_index = Taiwan_Index()
TW_stock = Taiwan_Stock()
USA_Europe = oversea_USA_EUROPE()
Singapore = oversea_Singapore()
Hongkong = oversea_HongKong()
Japan_Tocom = oversea_Japan_TOCOM()
Japan_OSE = oversea_Japan_OSE()
today_date = today()

st.title("期貨保證金查詢")

if option == '指數期貨':
    st.subheader(option+"：")

    input = st.text_input('快速查詢（請輸入代碼並注意大小寫）：')

    database = TW_index
    if input not in database['代碼'].values:
        st.error('請輸入正確代碼!')
    else:
        filt = (database['代碼'] == input)
        new = database.loc[filt]
        name = new.iloc[0,1]
        clear = new.iloc[0,2]
        maintain = new.iloc[0,3]
        initial = new.iloc[0,4]
        st.write('* 商品別：'+name) 
        st.write('* 結算保證金：'+clear)
        st.write('* 維持保證金：'+maintain)
        st.write('* 原始保證金：'+initial)
        st.success('查詢成功!')
    
    st.dataframe(TW_index,2000,1000)
    st.caption(today_date)

elif option == '股票期貨':
    st.subheader(option+"：")

    input = st.text_input('快速查詢（請輸入股票證券代號）：')

    database = TW_stock
    if input not in database['股票期貨標的證券代號'].values:
        st.error('請輸入正確證券代號!')
    else:
        filt = (database['股票期貨標的證券代號'] == input)
        new = database.loc[filt]
        en_code = new.iloc[0,0]
        name = new.iloc[0,2]
        level = new.iloc[0,4]
        clear = new.iloc[0,5]
        maintain = new.iloc[0,6]
        initial = new.iloc[0,7]
        st.write('* 股票期貨名稱：'+name)
        st.write('* 股票期貨英文代碼：'+en_code) 
        st.write('* 保證金所屬級距：'+level) 
        st.write('* 結算保證金適用比例：'+clear)
        st.write('* 維持保證金適用比例：'+maintain)
        st.write('* 原始保證金適用比例：'+initial)
        st.success('查詢成功!')

    st.dataframe(TW_stock,2000,1000)
    st.caption(today_date)
elif option == 'ETF期貨':
    st.subheader(option+"：")

    input = st.text_input('快速查詢（請輸入股票證券代號）：')

    database = TW_etf
    if input not in database['股票期貨標的證券代號'].values:
        st.error('請輸入正確證券代號!')
    else:
        filt = (database['股票期貨標的證券代號'] == input)
        new = database.loc[filt]
        en_code = new.iloc[0,0]
        name = new.iloc[0,2]
        clear = new.iloc[0,4]
        maintain = new.iloc[0,5]
        initial = new.iloc[0,6]
        st.write('* 股票期貨名稱：'+name)
        st.write('* 股票期貨英文代碼：'+en_code) 
        st.write('* 結算保證金：'+clear)
        st.write('* 維持保證金：'+maintain)
        st.write('* 原始保證金：'+initial)
        st.success('查詢成功!')

    st.dataframe(TW_etf,2000,1000)
    st.caption(today_date)
elif option == 'USA and Europe':
    st.subheader(option+" 期貨：")

    input = st.text_input('快速查詢（請輸入英文代號並注意大小寫）：')

    database = USA_Europe
    if input not in database['代號'].values:
        st.error('請輸入正確英文代號並注意大小寫!')
    else:
        filt = (database['代號'] == input)
        new = database.loc[filt]
        en_code = new.iloc[0,0]
        name = new.iloc[0,1]
        currency = new.iloc[0,2]
        daytrade = new.iloc[0,5]
        maintain = new.iloc[0,4]
        initial = new.iloc[0,3]
        TW_dollar = new.iloc[0,6]
        st.write('* 商品名稱：'+name)
        st.write('* 幣別：'+currency) 
        st.write('* 原始保證金：'+currency+" "+initial)
        st.write('* 維持保證金：'+currency+" "+maintain)
        st.write('* 當沖保證金：'+currency+" "+daytrade)
        st.write('* 原始保證金（以今日匯率計算台幣）： NTD'+" "+TW_dollar)
        
        st.success('查詢成功!')
    
    st.dataframe(USA_Europe,2000,1000)
    st.caption(today_date)
elif option == 'Singapore':
    st.subheader(option+" 期貨：")

    input = st.text_input('快速查詢（請輸入英文代號並注意大小寫）：')

    database = Singapore
    if input not in database['代號'].values:
        st.error('請輸入正確英文代號並注意大小寫!')
    else:
        filt = (database['代號'] == input)
        new = database.loc[filt]
        en_code = new.iloc[0,0]
        name = new.iloc[0,1]
        currency = new.iloc[0,2]
        daytrade = new.iloc[0,5]
        maintain = new.iloc[0,4]
        initial = new.iloc[0,3]
        TW_dollar = new.iloc[0,6]
        st.write('* 商品名稱：'+name)
        st.write('* 幣別：'+currency) 
        st.write('* 原始保證金：'+currency+" "+initial)
        st.write('* 維持保證金：'+currency+" "+maintain)
        st.write('* 當沖保證金：'+currency+" "+daytrade)
        st.write('* 原始保證金（以今日匯率計算台幣）： NTD'+" "+TW_dollar)
        
        st.success('查詢成功!')
    
    st.dataframe(Singapore,2000,1000)
    st.caption(today_date)
elif option == 'Hongkong':
    st.subheader(option+" 期貨：")

    input = st.text_input('快速查詢（請輸入英文代號並注意大小寫）：')

    database = Hongkong
    if input not in database['代號'].values:
        st.error('請輸入正確英文代號並注意大小寫!')
    else:
        filt = (database['代號'] == input)
        new = database.loc[filt]
        en_code = new.iloc[0,0]
        name = new.iloc[0,1]
        currency = new.iloc[0,2]
        daytrade = new.iloc[0,5]
        maintain = new.iloc[0,4]
        initial = new.iloc[0,3]
        TW_dollar = new.iloc[0,6]
        st.write('* 商品名稱：'+name)
        st.write('* 幣別：'+currency) 
        st.write('* 原始保證金：'+currency+" "+initial)
        st.write('* 維持保證金：'+currency+" "+maintain)
        st.write('* 當沖保證金：'+currency+" "+daytrade)
        st.write('* 原始保證金（以今日匯率計算台幣）： NTD'+" "+TW_dollar)
        
        st.success('查詢成功!')

    st.dataframe(Hongkong,2000,1000)
    st.caption(today_date)
elif option == 'TOCOM':
    st.subheader(option+" 期貨：")

    input = st.text_input('快速查詢（請輸入英文代號並注意大小寫）：')

    database = Japan_Tocom
    if input not in database['代號'].values:
        st.error('請輸入正確英文代號並注意大小寫!')
    else:
        filt = (database['代號'] == input)
        new = database.loc[filt]
        en_code = new.iloc[0,0]
        name = new.iloc[0,1]
        currency = new.iloc[0,2]
        maintain = new.iloc[0,4]
        initial = new.iloc[0,3]
        TW_dollar = new.iloc[0,5]
        st.write('* 商品名稱：'+name)
        st.write('* 幣別：'+currency) 
        st.write('* 原始保證金：'+currency+" "+initial)
        st.write('* 維持保證金：'+currency+" "+maintain)
        st.write('* 原始保證金（以今日匯率計算台幣）： NTD'+" "+TW_dollar)
        
        st.success('查詢成功!')

    st.dataframe(Japan_Tocom,2000,1000)
    st.caption(today_date)
elif option == 'OSE':
    st.subheader(option+" 期貨：")

    input = st.text_input('快速查詢（請輸入英文代號並注意大小寫）：')

    database = Japan_OSE
    if input not in database['代號'].values:
        st.error('請輸入正確英文代號並注意大小寫!')
    else:
        filt = (database['代號'] == input)
        new = database.loc[filt]
        en_code = new.iloc[0,0]
        name = new.iloc[0,1]
        currency = new.iloc[0,2]
        daytrade = new.iloc[0,5]
        maintain = new.iloc[0,4]
        initial = new.iloc[0,3]
        TW_dollar = new.iloc[0,6]
        st.write('* 商品名稱：'+name)
        st.write('* 幣別：'+currency) 
        st.write('* 原始保證金：'+currency+" "+initial)
        st.write('* 維持保證金：'+currency+" "+maintain)
        st.write('* 當沖保證金：'+currency+" "+daytrade)
        st.write('* 原始保證金（以今日匯率計算台幣）： NTD'+" "+TW_dollar)
        
        st.success('查詢成功!')

    st.dataframe(Japan_OSE,2000,1000)
    st.caption(today_date)
