import pandas as pd
import os.path
import os


import re
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import datetime

import spacy
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
import emoji
import time

from pythainlp.corpus import thai_stopwords
from pythainlp.corpus.common import thai_words
from pythainlp import word_tokenize, Tokenizer
from nltk.corpus import stopwords
from pythainlp.util import normalize
from pythainlp.util import dict_trie
from textblob import Word 

import geopy.geocoders
from geopy.geocoders import Nominatim
import datetime
from textblob import TextBlob

import codecs
from Sentiment import sentiment
from geopy.extra.rate_limiter import RateLimiter


class main_data: #  Class สำหรับจัดการข้อมูลที่ได้รับมา เพื่อมาแสดงเป็นตาราง เป็นต้น

    def __init__(self):
        # self.path_tw = "{}/Software dev/Twtter&News/data_csv/Twitter/".format(os.getcwd())
        self.path_tw = "{}/data_csv/Twitter/".format(os.getcwd())
        # self.path_main = "{}/Software dev/Twtter&News/data_csv/".format(os.getcwd())
        self.path_main = "{}/data_csv/".format(os.getcwd())
        self.th_stops = self.stop_word_th() # stop word th
        self.en_stops = self.stop_word_en() # stop word en
        self.custom_dictionary_trie = self.add_word_th()
        self.sentiment = sentiment() # access sentiment

    def load_file_csv(self, query, lang, date): # if query is in data csv
        path_ = self.path_tw+'/'+f'{query}'+'/'+f'{lang}'+'/'+'data_'+f'{date}.csv'
        data = pd.read_csv(path_)
        return data
    
    def load_word_csv(self, query, lang, date):
        path_ = self.path_tw+'/'+f'{query}'+'/'+f'{lang}'+'/'+'words_'+f'{date}.csv'
        words = pd.read_csv(path_)
        return words
#---------------------------------- For cleanText
    def stop_word_th(self):
        th_stops = set(thai_stopwords()) #nltk thai # stop thai
        return th_stops
    def stop_word_en(self):
        en_stops1 = set(stopwords.words('english')) #nltk eng
        nlp = spacy.load("en_core_web_sm")
        en_stops2 = set(nlp.Defaults.stop_words)# spacy
        en_stops = en_stops1.union(en_stops2) # stop eng
        return en_stops
    def add_word_th(self):
        with codecs.open(self.path_main+'Custom_Word.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        custom_word ={e.strip() for e in lines}
        # custom_word = {'กัญชง','กรมทหาร','อนุญาติ','ดีเจมะตูม', 'ซื้อ','เราชนะ'}
        words = custom_word.union(thai_words())
        custom_dictionary_trie = dict_trie(words)
        return custom_dictionary_trie
#----------------------------------
    def cleanText(self, txt):
        # start = datetime.datetime.now() # จับเวลา

        text = normalize(txt) # ge nomal word of thai word
        
        text = ''.join([i for i in text if not i.isdigit()])  # remove digits
        text = re.sub(r'https?://\S+', '', text) # remove https
        text = re.sub(r"[^a-zA-Z0-9ก-๙]+", ' ', text)#remove special char
        text = ''.join(c for c in text if c not in emoji.UNICODE_EMOJI) # remove emoji

        token = word_tokenize(text, engine='newmm', custom_dict= self.custom_dictionary_trie) # tokenizer
        new_token = []
        for i in range(len(token)):  # remove stop word  and space
            nch = token[i].strip().lower() # change char for analize
            if (nch not in self.en_stops) and (nch not in self.th_stops): # remove eng and th stop words
                if len(nch) >= 2: # len more than 2
                    new_token.append(token[i])
        
        new_token = "|".join(new_token)
        end = datetime.datetime.now() # จับเวลา
        # take = end - start
        # print(f'new: {new_token}')
        # print(f'take time: {take}')
        return new_token

    def tokenize(self, d): # แยกคำโดยดูจากเครื่องหมาย "|"
        result = d.split("|")
        result = [x.strip(' ') for x in list(filter(None, result))] #ลบช่องว่างหน้า-หลังคำออก
        return result

    def nlp_word(self, df):

        print('Nlp and Sentiment word...')
        new_text = []
        tag = []
        for txt in df["text"]: # get clean text
            nlp_word = self.cleanText(txt)
            new_text.append(nlp_word)
            tag.append(self.sentiment.check_sentiment_nlp(nlp_word))

        nlp_df = pd.DataFrame(list(zip(new_text,tag)), columns =['word', 'tag']) # nlp dataframe
        print('done...')
        return nlp_df 

#--------------- Chart --------------------------------------------------
    def chart_word(self, df):
        
        new_text = []
        for txt in df["word"]: # get clean text
            new_text.append(txt)
        vectorizer = CountVectorizer(tokenizer=self.tokenize)
        transformed_data = vectorizer.fit_transform(new_text)

        # df
        keyword_df = pd.DataFrame(columns = ['word', 'count'])
        keyword_df['word'] = vectorizer.get_feature_names()
        keyword_df['count'] = np.ravel(transformed_data.sum(axis=0))
        keyword_df = keyword_df.sort_values(by=['count'], ascending=False, ignore_index=True)

        return keyword_df

    def chart_tag(self, df): # for sentimet count "tag"

        list_tag = []
        for tag in df["tag"].values.astype('U'):
            list_tag.append(tag)

        vectorizer = CountVectorizer(tokenizer=self.tokenize)
        transformed_data = vectorizer.fit_transform(list_tag)

        # df
        tag_df = pd.DataFrame(columns = ['tag', 'count'])
        tag_df['tag'] = vectorizer.get_feature_names()
        tag_df['count'] = np.ravel(transformed_data.sum(axis=0))
        tag_df = tag_df.sort_values(by=['count'], ascending=False, ignore_index=True)

        return tag_df

    def chart_fav(self, df):
        # df = self.load_file_csv(file_name, lang, date) #get data
        fav_cnt_df = df.drop_duplicates('text').sort_values(by = ['retweet_count'], ascending=False, ignore_index=True ).head(10)[['create_at','text','favourite_count']]
        return fav_cnt_df

    def chart_retw(self, df):
        # df = self.load_file_csv(file_name, lang, date) #get data
        retw_cnt_df = df.drop_duplicates('text').sort_values(by = ['retweet_count'], ascending=False, ignore_index=True ).head(10)[['create_at','text','retweet_count']]
        return retw_cnt_df

    def chart_retw_daily(self, df):
        # df = self.load_file_csv(file_name, lang, date) #get data
        df['date'] = pd.to_datetime(df['create_at'], errors='coerce')
        df["date"] = df["date"].dt.date
        retw_daily_cnt_df = df[['date', 'retweet_count']] # get two columns
        retw_daily_cnt_df = df.groupby(['date'])['retweet_count'].sum().reset_index(name="count") # sum retweet_count
        return retw_daily_cnt_df

    def chart_hashtag(self, df):
        # df = self.load_file_csv(file_name, lang, date) #get data
        hastag_data = df["hashtag"].dropna() # ทิ้ง rowที่มีช่องว่าง 
        vectorizer = CountVectorizer(tokenizer=self.tokenize) # แยกแต่ละคำด้่วย function slash_tokenized
        transformed_data = vectorizer.fit_transform(hastag_data) # ใส่ข้อมูลลงไป

        hash_tag_cnt_df = pd.DataFrame(columns = ['word', 'count']) 
        hash_tag_cnt_df['word'] = vectorizer.get_feature_names() # list of element
        hash_tag_cnt_df['count'] = np.ravel(transformed_data.sum(axis=0))
        hash_tag_cnt_df = hash_tag_cnt_df.sort_values(by=['count'], ascending=False, ignore_index=True).head(20)
        return hash_tag_cnt_df

    def chart_location(self, df):
        print('- sum the same location')
        # df = self.load_file_csv(file_name, lang, date) #get data
        # location_data = df["location"].values.astype('U') # ไม่ทิ้ง rowที่มีช่องว่าง
        location_data = df["location"].dropna() # ทิ้ง rowที่มีช่องว่าง 
        vectorizer = CountVectorizer(tokenizer=self.tokenize) # แยกแต่ละคำด้่วย function slash_tokenized
        transformed_data = vectorizer.fit_transform(location_data) # ใส่ข้อมูลลงไป
        location_data = pd.DataFrame(columns = ['location', 'count']) 
        location_data['location'] = vectorizer.get_feature_names() # list of element
        location_data['count'] = np.ravel(transformed_data.sum(axis=0))
        location_data = location_data.sort_values(by=['count'], ascending=False, ignore_index=True)
        return location_data

    def chart_latitude(self, df): # df is df_location
        print('- get location')
        dataset_locate = pd.read_csv("{}/Software dev/Twtter&News/data_csv/Location/data_location.csv".format(os.getcwd()), encoding='utf-8')
        geopy.geocoders.options.default_user_agent = "user_agent"
        # geopy.geocoders.options.default_timeout = 7
        geolocator = Nominatim(scheme='http')
        lat_list = []
        lon_list = []
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        start = datetime.datetime.now()
        for place in df['location']:
            place = place.strip()
            print(f'1 {place}')
            if place != (None or ''):
                if place in dataset_locate.location.values: # check if name in location
                    print('  -- Using database')
                    lat_ = dataset_locate['lat']
                    lon_ = dataset_locate['lon']
                    lat = lat_[dataset_locate.location[dataset_locate.location == place].index.tolist()] # input 'location' output "lat", 'lon'
                    lon = lon_[dataset_locate.location[dataset_locate.location == place].index.tolist()]
                    try: # if lat is not None
                        lat = (float(lat))
                        lon = (float(lon))
                    except:
                        lat = None
                        lon = None
                    print(f'2: {lat} and {lon}')
                else:    # load lat and lon in geocoder
        #-------------------------------------------------------------------------------
                    print('     -- Using geopy')
                    location = geocode(place,timeout=10)
                    try:
                        lat = location.latitude
                        lon = location.longitude
                    except:
                        lat = None
                        lon = None
                    print(f'2: {lat} and {lon}')
        #-------------------------------------------------------------------------------                      
            else:
                lat = None
                lon = None
            lat_list.append(lat)
            lon_list.append(lon) 
        end = datetime.datetime.now()
        print('take time: ',end - start)          
        df['lat'] = lat_list
        df['lon'] = lon_list
        save_location = df.drop(columns=['count']) # remove colume 'count'
        save_location = dataset_locate.append(save_location).drop_duplicates().dropna() # เพิ่ม location ใหม่โดยการลบตัวซ้ำ
        save_location.to_csv("{}/Software dev/Twtter&News/data_csv/Location/data_location.csv".format(os.getcwd()), index=False)
        return df.dropna()

    def chart_search(self, df ,columns ,input_query):
        # df = self.load_file_csv(file_name, lang, date) #get data
        # substring to be searched 
        sub = str(input_query)
        # creating and passsing series to new column 
        df["Indexes"]= df[str(columns)].str.find(sub) 
        # display 
        df = df.query('Indexes > 0').drop(columns=['Indexes']) # if there is no keyword return -1
        return df

    def chart_trend(self, date, country):
        df = pd.read_csv(self.path_main+f'/Trend/{country}/'+'Top_trend_'+f'{date}.csv')
        return df
    
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
    tw = main_data()
    print(tw.cleanText("ม็อบของสลิ่มที่หน้าหอศิลป์ค่ะเราเห็นตอนที่พี่เขาโดนล็อคคอแล้วโดนต่อยเราไม่ทราบเหตุการณ์ก่อนหน้านี้ว่าเกิดอะไรขึ้น"))
    # print(1)