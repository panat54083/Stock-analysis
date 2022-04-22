
from PyQt5 import QtWidgets, QtCore
from PyQt5.Qt import Qt
# from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QDate, Qt, pyqtSignal, QThread, QObject, QThreadPool, QRunnable, pyqtSlot
from PyQt5.QtWidgets import QMenu
# from PyQt5.QtWebEngineWidgets import QWebEngineView

from DataWindow_New import Ui_TwitterAndNews # import UI

import numpy as np
import random
import datetime
import os
import os.path
import threading
import time
import sys
from functools import partial

from Class_Twitter import main_twitter
from Class_Data import main_data
from Stock import stock_data
from WebScraping import web_screping

import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot
import plotly.express as px
import plotly
import pandas as pd
import webbrowser
from datetime import date, timedelta



class dataWin(QtWidgets.QMainWindow, Ui_TwitterAndNews):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Twitter and News')
        # get two main class
        self.twitter = main_twitter()
        self.data_tw = main_data()
        self.stock = stock_data()
        self.web_screping = web_screping()

        # own paramiter # 
        self.file_ = None
        self.lang_ = None
        self.date_ = self.twitter.date

        # temp paramiter
        self.list_days = list()
        self.list_days.append(self.date_)
        self.temp_df_tw = None # for tempolary dataframe
        self.temp_df_news = None
        self.mode = False # True == Tw , False == News

        # set combo clolumns box
        self.columns_Graph = [
                        'Top Word', 
                        'Top Favorite' ,
                        'Top Retweet' ,
                        'Top Retweet Daily' ,
                        'Top Hashtag' ,
                        'Top Location'
                        ]
        self.viewGraph.addItems(self.columns_Graph)

        self.columns_lang = ['TH', 'EN']
        self.langBox.addItems(self.columns_lang)
        self.langBox_2.addItems(self.columns_lang)
        
        # set date
        self.set_date_select()

        # set function
        self.list_trend_th.clicked.connect(self.click_topTrend_th)
        self.list_trend_th.doubleClicked.connect(self.dclick_topTrend_th)
        self.list_trend_us.clicked.connect(self.click_topTrend_us)
        self.list_trend_us.doubleClicked.connect(self.dclick_topTrend_us)

        self.Search_bt_tw.clicked.connect(self.get_tw)  
        self.Search_bt_news.clicked.connect(self.get_news)
        self.stock_search.clicked.connect(self.get_stock)
        self.show_bt.clicked.connect(self.show_graph)        
        # set show     
        self.show_trend()
        self.web_screping.check_todayNews()
        # progress bar 
        '''set progress bar = 0'''
        self.prog_tw(0) 
        self.prog_news(0) 
        self.prog_locate(0) 
        self.prog_stock(0) 


    # ---- Start-up function ----        
    def set_date_select(self):  # set at QDateEdit
        now_q = QDate.currentDate() # get today
        yes_q = now_q.addDays(-1)  # get yesterday
        self.start_edit.setDate(yes_q) # set yesterday as startdate
        self.start_edit.setCalendarPopup(True)
        self.end_edit.setDate(now_q) # set today as enddate
        self.end_edit.setCalendarPopup(True)

    def show_trend(self): # show top trend automaticly
        
        # get last modified time # path ตำแหน่งของ th และ en
        path_th = self.data_tw.path_main+'/Trend/th/'+'Top_trend_'+f'{self.date_}.csv' 
        path_us = self.data_tw.path_main+'/Trend/us/'+'Top_trend_'+f'{self.date_}.csv'
        
        if os.path.isfile(path_th) and os.path.isfile(path_us): # ตรวจสอบว่าถ้ามีไฟล์
            print('Trend is already updated')
            df_th = pd.read_csv(path_th) #ดึงข้อมูลจาก database 
            df_us = pd.read_csv(path_us)
        else: #File doesn't exist 
            print('Trend is not updated')
            self.twitter.get_trend() # ดึง trend และ ดึงข้อมูลจาก database 
            df_th = pd.read_csv(path_th)
            df_us = pd.read_csv(path_us)
        # add trend to listwidget
        for i, trend in enumerate(df_th['name']): # set ให้ trand แสดงใน gui
            self.list_trend_th.insertItem(i+1, trend)
        for i, trend in enumerate(df_us['name']):
            self.list_trend_us.insertItem(i+1, trend)
        # update trend ตัวแสดงเวลาเพื่อแสดงว่า ดึงข้อมูลมาเมื่อไหร่
        path_file = os.path.getmtime(path_th) 
        modifiy = datetime.datetime.fromtimestamp(path_file)
        modifiy_time = modifiy.strftime("%d/%m/%Y, %H:%M:%S")
        # set text
        self.Update_trend_lb.setText(f"last updated time: {modifiy_time} ")
    # ---- Main function ----    
    def click_topTrend_th(self): # เมื่อกด click ที่ trend th

        trend = self.list_trend_th.currentItem() # get th trend that you clicked
        trend = trend.text()
        self.inputTxt.setText(trend) # set query in ช่องค้นหา
        # print(f'trend: {trend}')

    def click_topTrend_us(self): # เมื่อกด click ที่ trend en
        trend = self.list_trend_us.currentItem() # get us trend that you clicked
        trend = trend.text()
        self.inputTxt.setText(trend) # set query in ช่องค้นหา
        # print(f'trend: {trend}')

    def dclick_topTrend_th(self): # เมื่อกด double click ที่ trend th
        trend = self.list_trend_th.currentItem() # get th trend that you clicked
        df = self.data_tw.chart_trend(self.date_, 'th') # เรียก df

        trend = trend.text() # เก็บ trend  ที่เลือก เพื่อนำไปค้นหาใน df 
        u = df['name'].str.contains(trend)
        df = df[u].reset_index()
        url = df.url[0] # ดึง url 
        webbrowser.open(url)  # Go to webpage
        print(f'go to {trend} : {url}')

    def dclick_topTrend_us(self): # เมื่อกด double click ที่ trend en
        trend = self.list_trend_us.currentItem() # get us trend that you clicked
        df = self.data_tw.chart_trend(self.date_, 'us')

        trend = trend.text()  # เก็บ trend  ที่เลือก เพื่อนำไปค้นหาใน df 
        u = df['name'].str.contains(trend)
        df = df[u].reset_index()
        url = df.url[0] # ดึง url 
        webbrowser.open(url)  # Go to webpage
        print(f'go to {trend} : {url}')

    def get_tw(self): # Thread ดึง twitter 
        # start up
        self.prog_tw(0) # set progress bar = 0

        query = self.inputTxt.text().strip() # get query
        self.file_ = query
        if query == '': # ถ้าไม่มี query ใน input 
            print("pls, input query...")
            return False
        lang = self.langBox.currentText().lower() # get language from combo box
        # get time
        start_time = self.start_edit.date().toString(Qt.ISODate) # เลือกเวลา start # Output: 2021-02-10
        end_time = self.end_edit.date().toString(Qt.ISODate) # เลือกเวลา end
        start_datetime = datetime.datetime.strptime(start_time,"%Y-%m-%d") # str time to datetime
        end_datetime = datetime.datetime.strptime(end_time,"%Y-%m-%d") # str time to datetime
        tday = datetime.datetime.today() # get today
        if end_datetime >  tday: # ถ้าเลือกเกินวัน
            print(f'Error : Cant get data in {end_datetime}')
            return False
        if start_datetime > end_datetime: # ถ้าเวลาเริ่มต้นมากกว่าวันหลัง
            print(f'Error : Start {start_datetime} > End {end_datetime}')
            return False
        
        self.prog_tw(10) # set progress bar = 10
        # Step 1: Create a QThread object
        self.thread_1 = QThread()
        # Step 2: Create a worker object
        self.worker = Worker()
        # Step 3: Move worker to the thread
        self.worker.moveToThread(self.thread_1)
        # Step 4: Connect signals and slots
        self.thread_1.started.connect(partial(self.worker.run_tw,query, lang, start_datetime, end_datetime)) # ใส่ input ส่งไปยัง thread เพื่อเขียนไฟล์
        self.worker.finished.connect(self.thread_1.quit) # ใช้งาน thread ก็ปิด thread 
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread_1.finished.connect(self.thread_1.deleteLater)
        self.worker.progress_bar.connect(self.prog_tw) # maximum = 80 ส่งค่า progress มาเให้ gui  เพื่อ set progress bar
        # Step 5: Start the thread
        self.thread_1.start()
        # Final 
        self.Search_bt_tw.setEnabled(False) # ปิดการทำงานของปุ่ม
        self.thread_1.finished.connect(
        lambda: self.load_tw()
        ) # เมื่อทำการเขียนไฟล์เสร็จก็ดึงไฟล์มาแสดง
        self.thread_1.finished.connect(
            lambda: self.Search_bt_tw.setEnabled(True) 
        ) # ทำให้ปุ่มใช้งานได้
        return True
    
    def get_news(self): # Thread ดึง news 
        self.prog_news(0)
        # -------------- input ------------------------
        query = self.inputTxt_2.text().strip() # get query
        if query == '':
            print("pls, input query...")
            return False
        lang = self.langBox_2.currentText().lower() # get language
        # get time
        start_time = self.start_edit.date().toString(Qt.ISODate) # เลือกเวลา # Output: 2021-02-10
        end_time = self.end_edit.date().toString(Qt.ISODate)
        start_datetime = datetime.datetime.strptime(start_time,"%Y-%m-%d")# str time to datetime
        end_datetime = datetime.datetime.strptime(end_time,"%Y-%m-%d")
        tday = datetime.datetime.today() # get today
        if end_datetime >  tday: # ถ้าเลือกเกินวัน
            print(f'Error : Cant get data in {end_datetime}')
            return False
        if start_datetime > end_datetime: # ถ้าเวลาเริ่มต้นมากกว่าวันหลัง
            print(f'Error : Start {start_datetime} > End {end_datetime}')
            return False
        # show data and sentiment     

        # -------------- thread ------------------------
        # Step 1: Create a QThread object
        self.thread_2 = QThread()
        # Step 2: Create a worker object
        self.worker = Worker()
        # Step 3: Move worker to the thread
        self.worker.moveToThread(self.thread_2)
        # Step 4: Connect signals and slots
        self.thread_2.started.connect(partial(self.worker.run_news,query,lang,start_datetime,end_datetime)) # ใส่ input ส่งไปยัง thread เพื่อเขียนไฟล์
        self.worker.finished.connect(self.thread_2.quit) # ใช้งาน thread ก็ปิด thread 
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread_2.finished.connect(self.thread_2.deleteLater)
        self.worker.progress_list.connect(self.load_news) # ส่งค่าจาก thread มา gui เพื่อแสดงค่า
        self.worker.progress_bar.connect(self.prog_news) # ส่งค่า progress มาเให้ gui  เพื่อ set progress bar
        # Step 5: Start the thread
        self.thread_2.start()
        # Final resets
        self.Search_bt_news.setEnabled(False) # ปิดการทำงานของปุ่ม
        self.thread_2.finished.connect(
            lambda: self.Search_bt_news.setEnabled(True) 
        ) # ทำให้ปุ่มใช้งานได้
        self.thread_2.finished.connect(
            lambda: self.prog_news(100)
        )# ทำให้ progress bar เป็น 100%
        # -------------- thread ------------------------

    def get_stock(self): # Thread ดึง stock 
        self.prog_stock(0)
        # Input
        stock_name = self.stock_lineEdit.text() # 'STEC.BK'
        start_time = self.start_edit.date().toString(Qt.ISODate) # เลือกเวลา # Output: 2021-02-10
        end_time = self.end_edit.date().toString(Qt.ISODate)
        start_datetime = datetime.datetime.strptime(start_time,"%Y-%m-%d")# str time to datetime
        end_datetime = datetime.datetime.strptime(end_time,"%Y-%m-%d")
        tday = datetime.datetime.today() # get today
        if end_datetime >  tday: # ถ้าเลือกเกินวัน
            print(f'Error : Cant get data in {end_datetime}')
            return False
        if start_datetime > end_datetime: # ถ้าเวลาเริ่มต้นมากกว่าวันหลัง
            print(f'Error : Start {start_datetime} > End {end_datetime}')
            return False
        # -------------- thread ------------------------
        # Step 1: Create a QThread object
        self.thread_3 = QThread()
        # Step 2: Create a worker object
        self.worker = Worker()
        # Step 3: Move worker to the thread
        self.worker.moveToThread(self.thread_3)
        # Step 4: Connect signals and slots
        self.thread_3.started.connect(partial(self.worker.run_stock,stock_name,start_time,end_time))
        self.worker.finished.connect(self.thread_3.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread_3.finished.connect(self.thread_3.deleteLater)
        self.worker.progress.connect(self.plot_stock) # ส่งค่าจาก thread มา gui เพื่อแสดงค่า
        self.worker.progress_bar.connect(self.prog_stock)  # ส่งค่า progress มาเให้ gui  เพื่อ set progress bar
        # Step 5: Start the thread
        self.thread_3.start()
        # Final resets
        self.stock_search.setEnabled(False) # ปิดการทำงานของปุ่ม
        self.thread_3.finished.connect(
            lambda: self.stock_search.setEnabled(True) 
        ) # ทำให้ปุ่มใช้งานได้
        self.thread_3.finished.connect(
            lambda: self.prog_stock(100)
        ) # ทำให้ progress bar เป็น 100%
        # -------------- thread ------------------------

    # ---- Sub-function ----  
    def show_graph(self): # เป็นเพียงส่วนที่แสดงกราฟ
        df = self.temp_df_tw # load file df จากที่เราเรียกล่าสุด
        type_ = self.viewGraph.currentText()

        if type_ == self.columns_Graph[0]: # top word
            df_word = self.data_tw.chart_word(df) # turn df to chart word
            # remove keyword
            word = self.file_ # keyword that want to remove
            word = word.replace('#','').strip().lower() #get keyword
            df_lower = pd.DataFrame(columns = ['word'])
            df_lower['word'] = df_word['word'].str.lower()
            index = df_word.index[df_lower['word'] == word].tolist() # return index of keyword (list)
            
            df_word = df_word.drop(index).head(10) # remove keyword by index

            fig = px.bar(df_word, x="word", y=["count"],title="Top word")
            fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
            raw_html = self.plot_plotlyGraph(fig)
            self.GraphView.setHtml(raw_html)
            

        elif type_ == self.columns_Graph[1]: # top favorite 
            df = self.data_tw.chart_fav(df)
            # model = pandasModel(df) # create Table
            # self.tableView.setModel(model)
            fig = self.plot_table(df, type_)
            raw_html = self.plot_plotlyGraph(fig)
            self.TwView.setHtml(raw_html)  
            self.GraphView.setHtml('')

        elif type_ == self.columns_Graph[2]: # top Retweet 
            df = self.data_tw.chart_retw(df)
            # model = pandasModel(df) # create Table
            # self.tableView.setModel(model)
            fig = self.plot_table(df, type_)
            raw_html = self.plot_plotlyGraph(fig)
            self.TwView.setHtml(raw_html)              
            self.GraphView.setHtml('')

        elif type_ == self.columns_Graph[3]: # top Retweet Daily
            df = self.data_tw.chart_retw_daily(df) # get chart
            # --------------plot chart----------------
            # plot
            fig = px.bar(df, x="date", y=["count"], title="Top Retweet Daily")
            raw_html = self.plot_plotlyGraph(fig)
            self.GraphView.setHtml(raw_html)

        elif type_ == self.columns_Graph[4]: # top Hashtag 
            df = self.data_tw.chart_hashtag(df) # get chart hashtag

            fig = px.bar(df, x="word", y=["count"], title="Top Hashtag ")       #  plot
            
            raw_html = self.plot_plotlyGraph(fig)
            self.GraphView.setHtml(raw_html)

            
        elif type_ == self.columns_Graph[5]: # top location
            self.prog_locate(0)
            # -------------- thread ------------------------
            # Step 2: Create a QThread object
            self.thread_4 = QThread()
            # Step 3: Create a worker object
            self.worker = Worker()
            # Step 4: Move worker to the thread
            self.worker.moveToThread(self.thread_4)
            # Step 5: Connect signals and slots
            self.thread_4.started.connect(partial(self.worker.run_locate, df))
            self.worker.finished.connect(self.thread_4.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread_4.finished.connect(self.thread_4.deleteLater)
            self.worker.progress_bar.connect(self.prog_locate) # set progress bar
            self.worker.progress.connect(self.plot_location) # get df from thread to plot location
            
            # Step 6: Start the thread
            self.thread_4.start()
            # Final resets
            self.show_bt.setEnabled(False)
            self.thread_4.finished.connect(
                lambda: self.show_bt.setEnabled(True) 
            )
            # -------------- thread ------------------------

    def show_sent_tw(self): #เป็นเพียงส่วนที่แสดงกราฟ
        df = self.temp_df_tw # get temp
        df_sent = self.data_tw.chart_tag(df)
        # load data
        fig = px.pie(df_sent, values='count', names='tag',color='tag'
                                ,color_discrete_map={
                                'pos':'green',
                                'neu':'gray',
                                'neg':'red',
                                })
        # del whitespace
        fig.update_layout(
                            margin=dict(
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=4
                            )
                        )

        # fig.show()
        raw_html = self.plot_plotlyGraph(fig)
        self.SentView_tw.setHtml(raw_html)

    def show_sent_news(self): # #เป็นเพียงส่วนที่แสดงกราฟ
            df = self.temp_df_news
            df = self.data_tw.chart_tag(df) # get chart of sentiment news
            # load data
            fig = px.pie(df, values='count', names='tag',color='tag'
                                    ,color_discrete_map={
                                    'pos':'green',
                                    'neu':'gray',
                                    'neg':'red',
                                    })

            # del whitespace
            fig.update_layout(
                                margin=dict(
                                    l=0,
                                    r=0,
                                    b=0,
                                    t=0,
                                    pad=4
                                )
                            )                
            # fig.show()
            raw_html = self.plot_plotlyGraph(fig)
            self.SentView_news.setHtml(raw_html)

    def plot_plotlyGraph(self, fig): # ส่วนเสริมของ  plotly เพื่อแสดงกราฟ
        raw_html = '<html><head><meta charset="utf-8" />'
        raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html += '<body style= "zoom:100%;"  >'
        raw_html += plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
        raw_html += '</body></html>'
        return raw_html    

    def plot_table(self, df, type_): # ส่วนของการสร้างตาราง
        
        # print(df.columns)
        if type_ == 'twitter_chart':
            fig = go.Figure(data=[go.Table(
                header=dict(values=['Date', 'Tweet'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df.create_at, df.text],
                        fill_color='lavender',
                        align='left'))
            ])
        elif type_ == 'news_chart':
            fig = go.Figure(data=[go.Table(
                header=dict(values=['Date', 'Headline','Sentiment'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df.date, df.headline, df.tag],
                        fill_color='lavender',
                        align='left'))
            ])
        elif type_ == 'Top Word':
            fig = go.Figure(data=[go.Table(
                header=dict(values=['Word', 'Count'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df.keys, df.values],
                        fill_color='lavender',
                        align='left'))
            ])
        elif type_ == 'Top Favorite':
            fig = go.Figure(data=[go.Table(
                header=dict(values=['Create at','Text', 'Favorite count'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df.create_at,df.text, df.favourite_count],
                        fill_color='lavender',
                        align='left'))
            ])
        elif type_ == 'Top Retweet':
            fig = go.Figure(data=[go.Table(
                header=dict(values=['Create at','Text', 'Retweet count'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df.create_at,df.text, df.retweet_count],
                        fill_color='lavender',
                        align='left'))
            ])    
        elif type_ == 'Top Retweet Daily':
            fig = go.Figure(data=[go.Table(
                header=dict(values=['Date', 'Retweet count'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df.date, df.count],
                        fill_color='lavender',
                        align='left'))
            ])     
        elif type_ == 'Top Hashtag':
            fig = go.Figure(data=[go.Table(
                header=dict(values=['Word', 'Count'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df.word, df.count],
                        fill_color='lavender',
                        align='left'))
            ])            
        elif type_ == 'Top Location':
            fig = go.Figure(data=[go.Table(
                header=dict(values=['Location', 'Latitude', 'Longitude'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df.location, df.lat, df.lon],
                        fill_color='lavender',
                        align='left'))
            ])                                                              

        fig.update_layout(
                            margin=dict(
                                l=0,
                                r=0,
                                b=0,
                                t=0
                            )
                        )
        # fig.show()
        return fig          

    def load_tw(self): # นำข้อมูลมาแสดงลง gui
        query = self.inputTxt.text().strip() # get query
        lang = self.langBox.currentText().lower() # get language
        # get time
        start_time = self.start_edit.date().toString(Qt.ISODate) # เลือกเวลา # Output: 2021-02-10
        end_time = self.end_edit.date().toString(Qt.ISODate)
        start_datetime = datetime.datetime.strptime(start_time,"%Y-%m-%d")# str time to datetime
        end_datetime = datetime.datetime.strptime(end_time,"%Y-%m-%d")
        # concat data
        list_data_tw = list() # save data of tw
        list_days = list()
        # for loop for save data
        delta = end_datetime - start_datetime     # as timedelta (range)
        loop_day = delta.days + 1
        # ------------- progress bar -------------
        per = 20 / (int(delta.days)+1)
        twenty = 80
        # ----------------------------------------
        if query != '': # ถ้าไม่ใช่ช่องว่าง 
            print(f'Query: {query}')
            for i in range(loop_day):
                day = end_datetime - datetime.timedelta(days=i)
                day = day.strftime("%Y-%m-%d") # current day
                list_days.append(str(day)) # add for get days for update
                try:
                    print(f'    - show the {day} data')
                    df_tw = self.data_tw.load_file_csv(query, lang, day) # load twitter each day
                except: # df is empty
                    print(f'    - there is no the {day} data')
                    df_tw = None
                list_data_tw.append(df_tw) # save data to list for concat
                # ------------- progress bar -------------
                twenty += per
                self.prog_tw(int(twenty))
                # ----------------------------------------
                # print(df_tw)
            print('Done...')
            self.list_days = list_days # set list days
            try: # all in list_data_tw are not None
                concat_df_tw = pd.concat(list_data_tw).sort_values(by="create_at") # concat data
                # print(concat_df_tw)
                concat_df_tw['create_at'] = pd.to_datetime(concat_df_tw['create_at']) # tranform datetime
                #greater than the start date and smaller than the end date
                mask = (concat_df_tw['create_at'] > start_datetime) & (concat_df_tw['create_at'] <= (end_datetime+ datetime.timedelta(days=1)))
                concat_df_tw = concat_df_tw.loc[mask]# Select the sub-DataFrame
                concat_df_tw['create_at'] = concat_df_tw['create_at'].dt.strftime("%d-%m-%Y, %H:%M:%S") # turn created_at to string
                # print(concat_df_tw)
                fig = self.plot_table(concat_df_tw, 'twitter_chart')
                raw_html = self.plot_plotlyGraph(fig)
                self.TwView.setHtml(raw_html)
                # model = pandasModel(concat_df_tw) # set chart
                # self.tableView.setModel(model)
                self.temp_df_tw = concat_df_tw #save for plot graph

            except: # if there is no data
                raw_html = "Data is empty"
                self.TwView.setHtml(raw_html)
                print('A data frame of twitter is emplty.')
            try: 
                self.show_sent_tw() # show sentiment of twitter
            except: # if there is no file twitter
                raw_html = "Data is empty"
                self.SentView_tw.setHtml(raw_html)
                print('there is no file twitter, i cant show sentiment of twitter.')
        # ------------- progress bar -------------
        self.prog_tw(100) 
        # ----------------------------------------

    def load_news(self, df_list): # นำข้อมูลมาแสดงลง gui
        list_data_news = df_list
        try: # if df_news is not empty
            concat_df_news = pd.concat(list_data_news).sort_values(by="date") #รวมไฟล์
            fig = self.plot_table(concat_df_news, 'news_chart')
            raw_html = self.plot_plotlyGraph(fig)
            self.NewsView.setHtml(raw_html)
            # model_news = pandasModel(concat_df_news)
            # self.tableView_2.setModel(model_news)
            self.temp_df_news = concat_df_news
        except: 
            raw_html = "Data is empty"
            self.NewsView.setHtml(raw_html)
            print('a data frame of news is emplty.')
        try: 
            self.show_sent_news() # show sentiment of News
        except: # if there is no file twitter
            raw_html = "Data is empty"
            self.SentView_news.setHtml(raw_html)
            print('there is no file News, i cant show sentiment of News.')

    def plot_stock(self, data): # นำข้อมูลมาแสดงลง gui
        stock_name = self.stock_lineEdit.text() # 'STEC.BK'
        try:

            # data = stock.get_data(stock_name,start_time,end_time) # get dataframe
            list_d = data.index # get index
            date_set = set(list_d[0] + timedelta(x) for x in range((list_d[-1] - list_d[0]).days)) # get set of date
            missing = sorted(date_set - set(list_d)) # find missing date
            list_date = []
            # print(missing)
            for miss in missing: # prev missing data = current missing data
                list_date.append(miss)
            # print(list_date)

            # plot
            fig = go.Figure()

            fig.add_trace(go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high = data['High'],
                                        low=data['Low'],
                                        close=data['Close'],
                                        name = 'market data'))

            fig.update_layout(
                title= f'{stock_name} live share price evolution',
                yaxis_title='Stock price (USE per Shares)',
                # xaxis=dict(type="log"),
                margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=0,
                            pad=4
                                )
                                )

            # hide dates with no values
            fig.update_xaxes(rangebreaks=[dict(values=list_date)])

            raw_html = self.plot_plotlyGraph(fig) # get html to plot

            self.StockView.setHtml(raw_html)
        except:
            self.StockView.setHtml("No data")

    def plot_location(self, df): # นำข้อมูลมาแสดงลง gui

        fig = self.plot_table(df, "Top Location") #plot chart
        raw_html = self.plot_plotlyGraph(fig)
        self.TwView.setHtml(raw_html)
        #plot graph        
        fig = px.scatter_geo(df,
                            lat=df['lat'],
                            lon=df['lon'],
                            hover_name="location"
                            )
        # del whitespace
        fig.update_layout(
                            margin=dict(
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=4
                            )
                        )
        
        raw_html = self.plot_plotlyGraph(fig) # get html to plot
        self.GraphView.setHtml(raw_html)
        self.prog_locate(100)

    # ---- Progress bar ----
    def prog_tw(self, i): 
        if i == 0: # hide ถ้า progress bar มีค่าเป็น 0
            self.progressBar_tw.setVisible(False)
        elif i == 100: # hide ถ้า progress bar มีค่าเป็น 100
            self.progressBar_tw.setValue(i)
            self.progressBar_tw.setVisible(False)
        else:  # show progress bar
            self.progressBar_tw.setValue(i)
            self.progressBar_tw.setVisible(True)

    def prog_news(self, i):
        if i == 0:  # hide ถ้า progress bar มีค่าเป็น 0
            self.progressBar_news.setVisible(False)
        elif i == 100: # hide ถ้า progress bar มีค่าเป็น 100
            self.progressBar_news.setValue(i)
            self.progressBar_news.setVisible(False)
        else:  # show progress bar
            self.progressBar_news.setValue(i)
            self.progressBar_news.setVisible(True)

    def prog_locate(self, i):
        if i == 0:  # hide ถ้า progress bar มีค่าเป็น 0
            self.progressBar_locate.setVisible(False)
        elif i == 100:  # hide ถ้า progress bar มีค่าเป็น 100
            self.progressBar_locate.setValue(i)
            self.progressBar_locate.setVisible(False)
        else:  # show progress bar
            self.progressBar_locate.setValue(i)
            self.progressBar_locate.setVisible(True)

    def prog_stock(self, i):
        if i == 0:
            self.progressBar_stock.setVisible(False)
        elif i == 100:
            self.progressBar_stock.setValue(i)
            self.progressBar_stock.setVisible(False)
        else: 
            self.progressBar_stock.setValue(i)
            self.progressBar_stock.setVisible(True)
# ------------------------------ Worker Thread -----------------------------
   
class Worker(QObject):
    
    progress_bar = pyqtSignal(int)
    progress = pyqtSignal(pd.core.frame.DataFrame)
    progress_list = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self,parent=None):
        QObject.__init__(self, parent)

        self.stock = stock_data()
        self.data_tw = main_data()
        self.web_screping = web_screping()
        self.twitter = main_twitter()
        # get argument
    
    def run_tw(self, query, lang, start_datetime, end_datetime): # ดึงไฟล์ข่้อมูล twitter 
        start = datetime.datetime.now() # จับเวลา 
        print(f'Check {query}')
        delta = end_datetime - start_datetime     # as timedelta (range)
        print(int(delta.days))
        # ------------- progress bar -------------
        per = 70 / (int(delta.days)+1) # maximun in this process is 80%
        bar = 10
        # ----------------------------------------
        for j,i in enumerate(range(delta.days + 1)): # นำช่วงเวลามาค้นหาไฟล์
            day = end_datetime - datetime.timedelta(days=i)
            day = day.strftime("%Y-%m-%d") # current day
            print(f'{j+1}. find the {day} data')
            try: # if file is existed
                self.data_tw.load_file_csv(query,lang,day) # load twitter ถ้่ามีไฟล์
                print(f'    {j+1}.1. there is  the data')
            except:
                # ------------------------------
                print(f'    {j+1}.1. there is no the data')
                # ------------------------------
                self.twitter.write_file(query, lang, day) # ทำการเขียนไฟล์ใหม่
                # ------------------------------
            # ------------- progress bar -------------
            bar += per
            self.progress_bar.emit(int(bar))
            # ----------------------------------------
        end = datetime.datetime.now() # จับเวลา
        take = end - start
        print(f'take time: {take}')        
        print("Thread done...")
        print('-----------------')
        self.finished.emit()
    
    def run_stock(self,name, start_date, end_date): # ดึง stock 
        start = datetime.datetime.now() # จับเวลา
        data = self.stock.get_data(name,start_date,end_date)  # ดึง stock 

        end = datetime.datetime.now() # จับเวลา
        take = end - start
        print(f'take time: {take}')        
        print("3. Thread done...")
        print('-----------------')
        self.progress.emit(data)
        self.progress_bar.emit(50)
        self.finished.emit()

    def run_locate(self, df): # ดึงไฟล์ข่้อมูล location with geopy 
        # ------------- progress bar -------------
        per = 35
        bar = 0
        # ----------------------------------------        
        start = datetime.datetime.now() # จับเวลา

        df = self.data_tw.chart_location(df) # get location
        bar += per
        self.progress_bar.emit(int(bar)) # เพิ่มค่าใน process bar
        df = self.data_tw.chart_latitude(df) # turn location ot 
        bar += per
        self.progress_bar.emit(int(bar))
        end = datetime.datetime.now() # จับเวลา
        take = end - start
        print(f'take time: {take}')        
        print("3. Thread done...")
        print('-----------------')
        self.progress.emit(df)
        self.finished.emit()
 
    def run_news(self, query, lang, start_datetime, end_datetime): # ดึงไฟล์ข่้อมูล news 

        # --------------------input--------------------
        delta = end_datetime - start_datetime     # as timedelta (range)
        list_data_news = list() # save data of news
        list_days = list()
        # ------------- progress bar -------------
        per = 80 / (int(delta.days)+1) # maximun in this process is 80%
        bar = 0
        # --------------------Work--------------------
        start = datetime.datetime.now() # จับเวลา 
        for i in range(delta.days + 1):
            day = end_datetime - datetime.timedelta(days=i)
            day = day.strftime("%Y-%m-%d") # current day
            list_days.append(str(day)) # add for get days for update
            print(f'getting the data of {day}')
            print('News...')
            try: # if file is existed
                df_news = self.web_screping.load_news_withKey(query, lang, day) # load news
                print('done.')
            except:
                df_news = None
                print('there is no file.')

            list_data_news.append(df_news) # finished 
            bar += per
            self.progress_bar.emit(int(bar))
        end = datetime.datetime.now() # จับเวลา
        take = end - start
        print(f'take time: {take}')        
        print("3. Thread done...")
        print('-----------------')
        self.progress_list.emit(list_data_news)
        self.finished.emit()




def main():
    app = QtWidgets.QApplication(sys.argv)
    main = dataWin()
    main.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()