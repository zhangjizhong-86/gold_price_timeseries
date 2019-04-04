
# coding: utf-8

# In[6]:


import requests
from bs4 import BeautifulSoup
import pymysql
import json
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from logging.config import fileConfig


# In[2]:


url = 'https://data-asg.goldprice.org/dbXRates/USD,CNY'
convert_denom = 31.1030 # oz → g
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"  
LOG_FILE = 'au_ag_price.log'
LOG_MODE = 'a'  
LOG_MAX_SIZE = 1024*1024 # 1MB
LOG_MAX_FILES = 1 # 1 File only


# In[3]:


def get_price():
    response = requests.get(url)
    dict_response = json.loads(response.text)
    time = datetime.fromtimestamp(dict_response['tsj'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
    xauPrice = dict_response['items'][0]['xauPrice'] / convert_denom
    xagPrice = dict_response['items'][0]['xagPrice'] / convert_denom
    return time, xauPrice, xagPrice


# In[13]:


def to_db(time, xauPrice, xagPrice):
    conn = None
    try:
        conn = pymysql.connect(host='localhost',
                               user='root',
                               password='mysql',
                               db='test',
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        Logger.info('连接数据库成功。') 
        with conn.cursor() as c:
            insert_sql = 'insert ignore into au_ag_price values(%s,%s,%s)'
            c.execute(insert_sql, (time, round(xauPrice, 2), round(xagPrice, 2)))
            conn.commit()
            Logger.info('写数据库成功。') 
    except Exception as e:
        Logger.error('写数据库出错：' + str(e)) 
    finally:
        if conn:
            conn.close()
        Logger.info('关闭数据库。') 


# In[15]:


if __name__ == '__main__':
    # 开启日志
    formatter = logging.Formatter(LOG_FORMAT)
    handler = RotatingFileHandler(LOG_FILE, LOG_MODE, LOG_MAX_SIZE, LOG_MAX_FILES)    
    handler.setFormatter(formatter)  
    Logger = logging.getLogger()  
    Logger.setLevel(LOG_LEVEL)  
    Logger.addHandler(handler) 
    
    time, xauPrice, xagPrice = get_price()
    Logger.info('抓取价格…') 
    to_db(time, xauPrice, xagPrice)

