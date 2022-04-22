
import tweepy
import pandas as pd

import os
import os.path

from Class_Data import main_data

import datetime
import time


class main_twitter: #  Class สำหรับดึงข้อมูล ของ twitter

    def __init__(self):
        
        # for authen
        self.consumer_key = "js2ZOCd2eSTnMPquV1biLL20q"
        self.consumer_secret = "e5QQIvdPeXJFgIUPBnGn7VHAdsOtIuF8VHs4nNCi5zpR3v6KAp"
        self.access_token = "1099897687208423424-mZVzBkSpdwp3Yl9BOvDipP9qSxLAm7"
        self.access_token_secret = "nWmK0RcQN0O8xnYbzh0I3puO8TUJvQWwVZhrCgJqn4Fgy"

        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)

        # for getting data form twitter
        self.q = None
        self.lang = str('th')
        self.count = 100
        self.result_type = 'recent' # recent mixed popular
        self.tweet_mode = 'extended' 
        self.items = 200 # maximum 900
        self.date = datetime.datetime.today().strftime("%Y-%m-%d")

        # location of data
        # self.parent_dir = "{}/Software dev/Twtter&News/data_csv/Twitter/".format(os.getcwd())
        self.parent_dir = "{}/data_csv/Twitter/".format(os.getcwd())
        # self.path_main = "{}/Software dev/Twtter&News/data_csv/".format(os.getcwd())
        self.path_main = "{}/data_csv/".format(os.getcwd())
        # main_data
        self.data_tw = main_data()

# ----------------------- Sub -----------------------   
    def get_text(self, tweet): # ดึง text
        try: # for extended mode
            return tweet.full_text
        except: # for compatibility mode
            return tweet.text

    def get_time(self, tweet): # get time
        date = tweet.created_at
        # date = date.strftime("%Y-%m-%d, %H:%M:%S")
        return date

    def get_numOfRetweet(self, tweet): # get number of retweet
        return tweet.retweet_count
    
    def get_tweetBy(self, tweet): # what type of tool that tweet or retweet
        return tweet.source 
 
    def get_location(self, tweet): # ดึง location
        if type(tweet) is tweepy.models.Status:
            tweet = tweet.__dict__
        # get the place from the place data inside the tweet dict
        place = tweet['user'].location
        try:
            place = place.split(', ')[-1].upper()
            return place
        except :
            return None

    def get_favCount(self, tweet): # นับจำนวน fav
        try: # if tweet is retweeted
            fav_count = tweet.retweeted_status.favorite_count # get fav at main tweet
            return fav_count
        except:
            fav_count = tweet.favorite_count
            return fav_count
    
    def get_checkTypeTw(self, tweet): # check that tweet is retweet:False or tweet:True
        tweettext = str(tweet.full_text.lower().encode('utf-8',errors='ignore'))
        if tweettext.startswith("b'rt @") == True: # ตรวจสอบถ้า tweet เป็น retweet
            return False
        else:
            return True

# ----------------------- Main -----------------------
    def write_file(self, query, lang, date):
        df = pd.DataFrame(columns= ['create_at', 'text', 'hashtag', 
                                'retweet_count', 'favourite_count', 'location',
                            'type of tweet']) 
        aday  = datetime.datetime.strptime(date, "%Y-%m-%d") # str to datetime
        # aday = aday + datetime.timedelta(days=1) # need to search tomorrow for getting today data
        aday = aday.strftime("%Y-%m-%d")
        print("Writing file..")
        start = datetime.datetime.now() # จับเวลา
        for tweet in tweepy.Cursor(self.api.search,
                                    q = query,
                                    lang =lang,
                                    count =self.count, 
                                    result_type = self.result_type, 
                                    tweet_mode = self.tweet_mode,
                                    until = aday
                                    ).items(self.items):
    
            # time of created tweet
            create_at = tweet.created_at 
            # count number ot retweeting
            re_count = tweet.retweet_count
            # hashtag
            entity_hashtag = tweet.entities.get('hashtags')
            hashtag = ""
            only_query = query.replace('#','')
            for i in range(0,len(entity_hashtag)):# check entity hashtags
                if entity_hashtag[i]['text'].lower() != only_query.lower(): # get only not equal query
                    hashtag = hashtag +"|"+entity_hashtag[i]['text']
            # get text and favorite count
            try: # ถ้า tweet เป็น retweet 
                text = tweet.retweeted_status.full_text
                fav_count = tweet.retweeted_status.favorite_count
            except:
                text = tweet.full_text
                fav_count = tweet.favorite_count
            # location
            location = self.get_location(tweet)
            if self.get_checkTypeTw(tweet) == True:
                retweet_or_not = 'tweet'
            else:
                retweet_or_not = 'retweet'
            # add to columns                                              
            new_column = pd.Series(data = [create_at,text,hashtag,re_count,fav_count,location,retweet_or_not], index=df.columns)
            df = df.append(new_column,ignore_index=True)
        if df.empty == True: # if df is empty
            finish = datetime.datetime.now() # สิ้นสุดเวลา
            print(f'    Can not get this file')
            print('     take time : ', finish-start)
            return False
        else: # df is not empty
            # nlp word
            nlp_df = self.data_tw.nlp_word(df) # retrun df
            # concat
            result = pd.concat([df, nlp_df], axis=1, join="inner") # concat df and nlp df
            # exprot to csv file
            # created main folder 
            self.created_folder(self.parent_dir,query) # /#covid
            # created sub lang folder
            path = self.parent_dir + '/' + query # /#covid/th
            self.created_folder(path ,lang)
            #save to cav'
            result.to_csv(self.parent_dir+'/'+f'{query}'+'/'+f'{lang}'+'/'+'data_'+f'{aday}.csv', index=False)
            # nlp_df.to_csv(self.parent_dir+'/'+f'{query}'+'/'+f'{self.lang}'+'/'+'words_'+f'{self.date}.csv', index=False)
            finish = datetime.datetime.now() # สิ้นสุดเวลา
            print('take time : ',finish-start)
            print("Write file done..")
            return True

    def get_trend(self):
        dict_woeid = {'th':23424960, 'us':23424977}
        print(f'Date: {self.date}')
        for wo in dict_woeid:
            trands = self.api.trends_place(dict_woeid[wo]) # WOEID
            columns = set() # get colums
            tweets_data = [] # get date
            print(f'Geting {wo} trend....')
            for trend in trands:
                keys = trend.keys()
                single_tweet_data = {}
                for k in keys:
                    single_tweet_data[k] = trend[k]
                    columns.add(k)
                tweets_data.append(single_tweet_data)
            df = pd.DataFrame(tweets_data[0]['trends'])
            df = df[['name', 'url', 'tweet_volume' ]].sort_values(by="tweet_volume", ascending= False, ignore_index = True).dropna() # dropna คือ ลบ แถวที่ไม่มีข้อมูล ออกทั้งแถว
            df.to_csv(self.path_main+f'/Trend/{wo}/'+'Top_trend_'+f'{self.date}.csv', index=False)
            print('Done....')
        return True

    def update_trend(self):
        path_file = os.path.getmtime(self.parent_dir+'/Trend/'+'Top_trend_'+f'{self.date}.csv') # get path
        now = datetime.datetime.now().strftime("%j") # current time
        modified = datetime.datetime.fromtimestamp(path_file).strftime("%j")    # last modified time
        diff = int(now) - int(modified) # difference time between current and last modeified
        if diff > 1: # ถ้าเวลาไม่ได้อัพเดจเกิน 1 วัน
            self.get_trend()
            return True

    def created_folder(self ,parent_dir ,folder):
        # Path 
        path = os.path.join(parent_dir, folder) 
        # Create the directory 
        try:  
            os.mkdir(path)
            # print("Directory '% s' created" % folder) 
            return True
        except OSError as error:   # the file already exists
            # print(error)  
            pass
    

if __name__ == "__main__":
    import plotly.express as px
    import numpy as np
    # print(os.getcwd())
    main = main_twitter()
    
    # query
    main.q = '#Onet64'
    # language
    main.lang = 'th'
    # main.date = '2000-01-01'
    # write file
    # df = main.write_file()
    print(main.write_file())
    # update file
    # print(main.update_csv())
    # get trand
    # print(main.get_trend())
    # update trend
    # print(main.update_trend())