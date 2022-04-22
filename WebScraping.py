from pandas.io.parsers import read_csv
import requests
from bs4 import BeautifulSoup
import pandas as pd

from urllib.parse import urlparse 
from Sentiment import sentiment
import datetime
import os
from pythainlp import word_tokenize

class web_screping(): #  Class สำหรับดึงข้อมูล ของ Web
    def __init__(self):
        self.sentiment = sentiment()
        # self.path = "{}/Software dev/Twtter&News/data_csv/Web/".format(os.getcwd()) # path
        self.path = "{}/data_csv/Web/".format(os.getcwd()) # path

    def screp_news(self, url): # input url # output เป็น dataframe (ใช้ดึงข่าว กับเนื้อข่าว)
        
        # create columns
        df = pd.DataFrame(columns= ['date','headline', 'link','content','tag']) 

        # web screping
        try:
            web_data = requests.get(url) # รับ url
        except:
            print(f'error url: {url}')
            return None
        print(f'url: {url}')
        soup = BeautifulSoup(web_data.text, 'html.parser') # แปลงเป็น html
        a_tag = soup.find_all('a') # find a tag
        tday = datetime.datetime.today().strftime("%Y-%m-%d") # สร้างตัวแปรเก็บค่าตัวนี้
        for i in a_tag: # each element in a_tag
            try: # ถ้า text ให้ค่าเป็น None
                headline = i.text.replace('\n', '').strip().split('  ')[0] # get headline
                if headline == '':  #skip if there is no head
                    continue
                if len(headline.strip())>20: # get only long sentence
                    # ----- link part ------
                    link = i['href'] # get link
                    domain = self.get_domain(url) # get domain url
                    link = link.replace('http:', 'https:') # use https instead of http
                    if ('https:') not in link:# if https not in link ex '//www.example.com/local'
                        
                        if (domain not in link) : # if domain not in link ex. "/news/local/22165"
                            link = 'https://'  + domain + link
                        else: # there is domain
                            link = 'https:' + link # add https
                    # ----- end link part -----
                    if url in link: #เพื่อไม่ให้ออกไปยัง Domain อื่น
                        content = self.get_content(link) # get content of headline
                        if content != '':
                            nlp_word = self.sentiment.cleanText(content) # nlp content
                            tag_sent = self.sentiment.check_sentiment_nlp(nlp_word) # นำ content ไปทำ sentiment
                            # add to columns                                              
                            new_column = pd.Series(data = [tday,headline, link, content,tag_sent], index=df.columns) #สร้าง row
                            df = df.append(new_column,ignore_index=True) #รวม row
                            df = df.dropna().drop_duplicates(subset=['headline']) # delete nan ลบแถวที่มีช่องว่าง
            except:
                pass
        return df  
    # use for run Web Screping 
    def write_WebSc(self): # ใช้เป็น function หลัก เพื่อดึงข่าวจากหลายๆ เว็บ
        start = datetime.datetime.now() # จับเวลา
        # url
        dic_url = self.direc_minor_news()
        threads = list()
        #     ---------------------------------------path----------------------------------------

        # path = r'C:/Users/pc/Documents/Python/Software dev/Twtter&News/data_csv/Web/'
        tday = datetime.datetime.today().strftime("%Y-%m-%d") # today
        print(f'Writing News {tday}')
        # writing
        for i,lang in enumerate(dic_url): # get lang
            list_concat = [] # list for saving df for concat
            for url in dic_url[lang]: # get url in spacific lang
                df = self.screp_news(url)
                list_concat.append(df)

            df_concat = pd.concat(list_concat, ignore_index=True) # concat df
            
            # df_concat = df_concat.drop_duplicates() # remove duplicates 
            df_concat = df_concat.loc[df_concat.astype(str).drop_duplicates().index] # remove duplicates  

            df_concat.to_csv(self.path+ f'/{lang}' + f'/{tday}.csv',index=False)
            print(f'web screping {lang} done : {tday}')
        end = datetime.datetime.now() # จับเวลา
        print('take time : ',end-start)
        print('Write done...')
        return True

    def load_news_withKey(self, query, lang, date): # จะทำการ return df ที่มี keyword ในนั้น โดยรวมถึง วันที่
        query = query.strip()

        df  = pd.read_csv(self.path + f'/{lang}' + f'/{date}.csv') # load file
        df = self.chart_search(df, 'headline', query) # search headlines by query
        return df

    def check_todayNews(self): # ตรวจสอบว่าวันนี้ได้ทำการ update ยัง
        tday = datetime.datetime.today().strftime("%Y-%m-%d")
        if os.path.isfile(self.path + '/th' + f'/{tday}.csv'): # ถ้ามีไฟล์ของวันนี้อยู๋
            print ("News is already updated")
            print("-----------------")
        else: # ถ้าไม่มีไฟล์วันนี้
            self.write_WebSc()
            print("-----------------")
            
    def get_minor_web(self, url): # ใช้ดึงเว็บย่อยๆในโดเมนหลัก
        list_all = []
        # web screping
        web_data = requests.get(url)
        soup = BeautifulSoup(web_data.text, 'html.parser') # แปลงเป็น html
        home_tag = soup.find_all('a',href=True) # find a tag
        for i in home_tag: # each element in a_tag
            text = i.text.replace('\n', '').strip() # get headline
            token = word_tokenize(text, engine='newmm') # tokenizer
            if text == '' or len(token) > 3:  # ตรวจสอบถ้ามีคำมากกว่า 3 คำ ก็ไม่เอา
                continue
            link = i['href'] # get link
            domain = self.get_domain(url) # get domain url
            link = link.replace('http:', 'https:') # use https instead of http
            if ('https:') not in link:# if https not in link ex '//www.example.com/local'

                if (domain not in link) : # if domain not in link ex. "/news/local/22165"
                    link = 'https://'  + domain + link
                else: # there is domain
                    link = 'https:' + link # add https
            # ----- end link part ----
            if ('#' in link) or (url not in link): # ถ้าไม่มี domain ใน minor ก็ไม่เอา
                continue
        #     print(text)
        #     print(link)
            list_all.append(link)
        list_all = list( dict.fromkeys(list_all) )
        return list_all #ให้ค่าเป็น list
    # ----------------------- sub-function -----------------------

    def dirac_Main_news(self): # save โดเมนหลัก 
        dir_news = {
        'th' :  [
            'https://www.thairath.co.th/',
            'https://www.sanook.com/',
            'https://www.posttoday.com/',
            'https://www.pptvhd36.com/',
            'https://www.prachachat.net/',
            'https://www.amarintv.com/',
            'https://www.matichon.co.th/',
            'https://www.bangkokbiznews.com/',
            'https://www.komchadluek.net/',
            'https://www.khaosod.co.th/',
            'https://www.posttoday.com/',
            'https://www.banmuang.co.th/',
            'https://www.thaipost.net/',
            'https://www.thansettakij.com/',
            'https://www.kaohoon.com/',
            'https://www.innnews.co.th/',
            'https://www.mcot.net/',
            'https://www.siamrath.co.th/',
            'https://www.chiangmainews.co.th/',
            'https://www.dailynews.co.th/',
            'https://www.marketingoops.com/',
            'https://www.msn.com/',
            'https://www.one31.net/',
            'https://www.stock2morrow.com/',
            'https://www.thunhoon.com/',
            
            
               ],
        'en' : [
            'https://www.bbc.com/',
            'https://news.yahoo.com/',
            'https://www.bangkokpost.com/',
            'https://www.nationthailand.com/',
            'https://www.nbcnews.com/',
            'https://www.nytimes.com/',
            'https://apnews.com/',
            'https://www.reuters.com/',
            'https://www.foxnews.com/',
            'https://abcnews.go.com/',
            'https://www.cnet.com/',
            'https://www.ft.com/',
            'https://www.time.com',
            'https://www.vogue.co.uk/',
            'https://www.elitedaily.com/',
            'https://www.news.google.com/',
            'https://www.al.com/',
            'https://www.bostonglobe.com/',
            'https://www.businessinsider.com/',
            'https://www.cbsnews.com/',
            'https://www.chron.com/',
            'https://www.cnbc.com/',
            'https://www.cnet.com/',
            'https://www.dailymail.co.uk/',
            'https://www.engadget.com/',
            'https://www.freep.com/',
            'https://www.marketwatch.com/',
            'https://www.mlive.com/',
            'https://www.nj.com/',
            'https://www.npr.org/',
            'https://www.nydailynews.com/',
            'https://www.sfgate.com/',
            'https://www.telegraph.co.uk/',
            'https://www.theatlantic.com/',
            'https://www.theblaze.com/',
            'https://www.thedailybeast.com/',
            'https://www.theguardian.com/',
            'https://www.upworthy.com/',
            'https://www.usatoday.com/',
            'https://www.vice.com/',
            'https://www.vox.com/',
            
        ]
        }
        return dir_news

    def direc_minor_news(self): # get minor news
        dic_url = self.dirac_Main_news()
        minordict = dict()
        print('Getting minor webs from domian webs...')
        for lang in dic_url: # get lang
            count = 0
            list_concat = [] # list for saving df for concat
            for j,url in enumerate(dic_url[lang]): # get url in spacific lang
                print(f'{j+1}.Main domain link: ', url)
                list_minor = self.get_minor_web(url)
                count += len(list_minor) # ตรวจสอบจำนวน minor link 
                list_concat.append(list_minor)
        #         print(list_concat)
            list_concat = sum(list_concat,[]) # รวม list minor link เข้าด้วยกัน
            print(f'len minor domain {lang} = {count}')
            minordict[lang] = list_concat

        return minordict # dict ที่รวมค minor ของ like domain ต่างๆ

    def chart_search(self, df ,columns ,keyword): # ใช้ค้นหา df ที่มี keyword
        # substring to be searched 
        sub = str(keyword).lower()
        # new
        df["lower"] = df[str(columns)].str.lower() # turn to lowercase
        df["Indexes"]= df["lower"].str.find(sub)  # find keyword in lowercase
        df = df.query('Indexes > 0').drop(columns=['Indexes', "lower"]) # if there is no keyword return -1
        return df

    def get_domain(self, url): # for return domain
        #https://stackoverflow.com/questions/44113335/extract-domain-from-url-in-python
        domain = urlparse(url).netloc
        return domain  # --> www.example.test
    
    def get_content(self, link): # ดึงเนื่อหา
        content = ''
        try:
            # web screping
            web_data = requests.get(link)
            soup = BeautifulSoup(web_data.text, 'html.parser') # แปลงเป็น html
            p_tag = soup.find_all('p') # find p tag
            for i in p_tag: # each element in p_tag
                text = i.text.replace('\n', '') # get headline
                content += text.strip(' ')+' '
        #     print(content)
            return content.strip()
        except:
            return None

if __name__ == '__main__':
    ws = web_screping()
    ws.write_WebSc()