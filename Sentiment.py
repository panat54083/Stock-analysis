# เครื่องมือในการ build sentiment เพื่อใช้ใน pythainlp
# เวชั่น 0.2
# 2017/08/17
# เขียนโดย นาย วรรณพงษ์  ภัททิยไพบูลย์
# ใช้ประกอบบทความใน python3.wannaphong.com
# cc-by 3.0 Thai Sentiment Text https://github.com/wannaphongcom/lexicon-thai/tree/master/ข้อความ/
# อ่านบทความได้ที่ https://python3.wannaphong.com/2017/02/ทำ-sentiment-analysis-ภาษาไทยใน-python.html
import nltk
from nltk import NaiveBayesClassifier as nbc
from nltk.corpus import stopwords
from pythainlp import tokenize
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.util import normalize
from textblob import Word
from textblob import TextBlob

import re
import spacy
import emoji

import pandas
import pickle
import codecs
from itertools import chain
import datetime
import os
from langdetect import detect 

class sentiment():
    def __init__(self):
        # load stopword
        self.th_stops = self.stop_word_th() # stop word th
        self.en_stops = self.stop_word_en() # stop word en

        # self.path_pickle = '{}/Software dev/Twtter&News/Pickle/'.format(os.getcwd())
        self.path_pickle = '{}/Pickle/'.format(os.getcwd())
        file = open(self.path_pickle+'sentiment.data', 'rb')
        file_2 = open(self.path_pickle+'vocabulary.data', 'rb')
        # dump information to that file
        self.sentiment = pickle.load(file)
        self.vocabulary = pickle.load(file_2)
        # close the file
        file.close()
        file_2.close()
        

    def stop_word_th(self):
        th_stops = set(thai_stopwords()) #nltk thai # stop thai
        return th_stops

    def stop_word_en(self):
        en_stops1 = set(stopwords.words('english')) #nltk eng
        nlp = spacy.load("en_core_web_sm")
        en_stops2 = set(nlp.Defaults.stop_words)# spacy
        en_stops = en_stops1.union(en_stops2) # stop eng
        return en_stops
#----------------------------------
    def cleanText(self, txt): # nlp ข้อมูล
        text = normalize(txt) # ge nomal word of thai word
        
        text = ''.join([i for i in text if not i.isdigit()])  # remove digits
        text = re.sub(r'https?://\S+', '', text) # remove https
        text = re.sub(r"[^a-zA-Z0-9ก-๙]+", ' ', text)#remove special char
        text = ''.join(c for c in text if c not in emoji.UNICODE_EMOJI) # remove emoji

        token = word_tokenize(text, engine='newmm') # tokenizer
        new_token = []
        for i in range(len(token)):  # remove stop word  and space
            nch = token[i].strip().lower() # change char for analize
            if (nch not in self.en_stops) and (nch not in self.th_stops): # remove eng and th stop words
                if len(nch) >= 2: # len more than 2
                    new_token.append(token[i])
        
        new_token = "|".join(new_token)
        new_token = new_token.split('|')
        return new_token
    
    def train_data(self): # เทรนข้อมูล
        start = datetime.datetime.now() # จับเวลา

        path_word = '{}/Software dev/Twtter&News/Word/edit/'.format(os.getcwd())
        path_pickle = '{}/Software dev/Twtter&News/Pickle/'.format(os.getcwd())
        # ---------------th part-----------------
        # pos.txt
        with codecs.open(path_word + 'pos.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        listpos=[e.strip() for e in lines]
        del lines
        f.close() # ปิดไฟล์
        # neg.txt
        with codecs.open(path_word + 'neg.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        listneg =[e.strip() for e in lines]
        f.close() # ปิดไฟล์
        # neutral.txt
        with codecs.open(path_word + 'neutral.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        listneutral =[e.strip() for e in lines]
        f.close() # ปิดไฟล
        # neutral.txt
        # ---------------en part-----------------
        with codecs.open(path_word + 'pos_en.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        listpos_en =[e.strip() for e in lines]
        f.close() # ปิดไฟล
        # neutral.txt
        with codecs.open(path_word + 'neg_en.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        listneg_en =[e.strip() for e in lines]
        f.close() # ปิดไฟล
        # neutral.txt
        with codecs.open(path_word + 'neutral_en.txt', 'r', "utf-8", errors='ignore') as f:
            lines = f.readlines()
        listneutral_en =[e.strip() for e in lines]
        f.close() # ปิดไฟล

        print(1,' load data done...')
        # th part
        pos1=['pos']*len(listpos[:1000])
        neg1=['neg']*len(listneg[:1000])
        neu1=['neu']*len(listneutral[:1000])
        # en part
        pos2=['pos']*len(listpos_en[:1000])
        neg2=['neg']*len(listneg_en[:1000])
        neu2=['neu']*len(listneutral_en[:1000])
        print(2,' get number of tag done...') 
        # sum data
        training_data = list(zip(listpos,pos1)) + list(zip(listneg,neg1)) + list(zip(listneutral,neu1))+ list(zip(listpos_en,pos2))+ list(zip(listneg_en,neg2))+ list(zip(listneutral_en,neu2)) # Ex. [('ชอบกินข้าว','pos')]
        print('len of training data = ', len(training_data))
        print(3, 'zip data done...')
        vocabulary = set(chain(*[(set(self.cleanText(i[0]))-self.th_stops-self.en_stops) for i in training_data]))
        print(vocabulary)
        print(3.1 ,' delate stopword done...')
        feature_set = [({i:(i in self.cleanText(sentence)) for i in vocabulary},tag) for sentence, tag in training_data]
        print(4, 'tokenize done...')
        classifier = nbc.train(feature_set) # fo     train data
        print(5, ' train done...')
        with open(path_pickle+'vocabulary.data', 'wb') as out_strm: 
            pickle.dump(vocabulary,out_strm)
        out_strm.close()
        with open(path_pickle+'sentiment.data', 'wb') as out_strm: 
            pickle.dump(classifier,out_strm)
        out_strm.close()
        end = datetime.datetime.now() # จับเวลา
        time_ = end-start
        print(f'OK pickel done : take {time_}')

    def tokenize_data(self): # ส่วนของการแยกคำ
        start = datetime.datetime.now() # จับเวลา
        print(1,' load data')
        path_word = '{}/Software dev/Twtter&News/Word/many/'.format(os.getcwd())
        path_pickle = '{}/Software dev/Twtter&News/Pickle/'.format(os.getcwd())
        # ---------------th part-----------------
        # pos.txt
        with codecs.open(path_word + 'pos.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        listpos=[e.strip() for e in lines]
        del lines
        f.close() # ปิดไฟล์
        # neg.txt
        with codecs.open(path_word + 'neg.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        listneg =[e.strip() for e in lines]
        f.close() # ปิดไฟล์
        # neutral.txt
        with codecs.open(path_word + 'neutral.txt', 'r', "utf-8") as f:
            lines = f.readlines()
        listneutral =[e.strip() for e in lines]
        f.close() # ปิดไฟล
        # neutral.txt

        print('     load data done...')
        print(2,' get number of tag') 
        # th part
        pos1=['pos']*len(listpos)
        neg1=['neg']*len(listneg)
        neu1=['neu']*len(listneutral)    
        # sum data
        training_data = list(zip(listpos,pos1)) + list(zip(listneg,neg1)) + list(zip(listneutral,neu1)) # Ex. [('ชอบกินข้าว','pos')]
        print('     len of training data = ', len(training_data))
        print(3, 'delate stopword')
        vocabulary = set(chain(*[(set(self.cleanText(i[0]))-self.th_stops-self.en_stops) for i in training_data]))
        print(vocabulary)
        print('     delate stopword done...')
        print(4,' tokenizing data')
        feature_set = [({i:(i in self.cleanText(sentence)) for i in vocabulary},tag) for sentence, tag in training_data]
        print(' tokenize done...')
        print(5, 'saving data into pickle')
        with open(path_pickle+'tokenize.data', 'wb') as out_strm: 
            pickle.dump(feature_set,out_strm)
        out_strm.close()
        with open(path_pickle+'vocabulary.data', 'wb') as out_strm: 
            pickle.dump(vocabulary,out_strm)
        out_strm.close()
        end = datetime.datetime.now() # จับเวลา
        time_ = end-start
        print(f'OK pickel done : take {time_}')

    def train_dataTok(self): # train data โดยใช้ input ที่ผ่าน tokenize แล้ว
        start = datetime.datetime.now() # จับเวลา
        path_pickle = '{}/Software dev/Twtter&News/Pickle/'.format(os.getcwd())

        file = open(path_pickle+'tokenize.data', 'rb')
        feature_set = pickle.load(file)
        file.close()
        print('training data...')
        classifier = nbc.train(feature_set) # fo     train data
        print(5, ' train done...')
        with open(path_pickle+'sentiment.data', 'wb') as out_strm: 
            pickle.dump(classifier,out_strm)
        out_strm.close()
        end = datetime.datetime.now() # จับเวลา
        time_ = end-start
        print(f'OK train done : take {time_}')

    def check_sentiment(self, text): # ตรวจสอบ sentiment

        lang = detect(text) # return 'th' or 'en'
        # start = datetime.datetime.now() # จับเวลา
        print("test_sent: ",text)
        if lang == 'th':
            # nlp_word = self.cleanText(text) # slow
            nlp_word = word_tokenize(text, engine='newmm') #fast

            featurized_test_sentence =  {i:(i in nlp_word) for i in self.vocabulary}
            tag = self.sentiment.classify(featurized_test_sentence)
            # print(featurized_test_sentence)
            print("tag: ",tag) # ใช้โมเดลที่ train ประมวลผล
        else:
            tag = self.check_sentiment_en(text)
            print("tag: ",tag) # ใช้โมเดลที่ train ประมวลผล            
        # end = datetime.datetime.now() # จับเวลา
        # take = end - start
        # print(f'take time: {take}')
        return tag
        
    def check_sentiment_nlp(self, nlp_word):# ตรวจสอบ sentiment โดยinput เป็น nlp word # input Ex. ['I','love','you']

        start = datetime.datetime.now() # จับเวลา
        lang = self.check_lang_nlp(nlp_word)
        if lang == 'th':
            featurized_test_sentence =  {i:(i in nlp_word) for i in self.vocabulary}
            # print("tag: ",sentiment.classify(featurized_test_sentence)) # ใช้โมเดลที่ train ที่ประมวลผล
            tag = self.sentiment.classify(featurized_test_sentence)
        else: # lang = 'en'
            # print('1',nlp_word)
            try:
                listToStr = nlp_word.split('|')
                # print('2',listToStr)
                listToStr = ' '.join(map(str, listToStr))
                # print('3',listToStr)
            except:
                listToStr = ' '.join(map(str, nlp_word))
                # print('2',listToStr)
            tag = self.check_sentiment_en(listToStr)

        end = datetime.datetime.now() # จับเวลา
        take = end - start
        # print(f'take time: {take}')
        return tag

    def check_sentiment_en(self, text): # sentiment ของ english
        testimonial = TextBlob(text)
        polar = testimonial.sentiment.polarity
        if polar > 0 :
            return 'pos'
        elif polar < 0 :
            return 'neg'
        else:
            return 'neu'

    def check_lang_nlp(self, nlp): # detect language
        listToStr = ' '.join(map(str, nlp))

        return detect(listToStr)
if __name__ == '__main__':
    sen = sentiment()
    # sen.tokenize_data()
    # sen.train_dataTok()
    
    # sen.train_dataWithTok()
    s = datetime.datetime.now() # สิ้นสุดเวลา
    sen.check_sentiment("ฉันมีความสุข")
    sen.check_sentiment("I love you")
    f = datetime.datetime.now() # สิ้นสุดเวลา
    print(f-s)

    # print(sen.check_sentiment_nlp(['I','love','you']))
    # print(sen.check_sentiment_nlp('เจ|โน่ผม|ดำ|xiaoyan|nct|NCT|JENO'))
    # while  True:
    #     text = str(input(">>>>> "))
    #     sen.check_sentiment(text)
