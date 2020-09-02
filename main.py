# coding=utf-8
# from korea_news_crawler.articlecrawler import ArticleCrawler
import re
from korea_news_crawler.articlecrawler2 import ArticleCrawler

TARGET = '정치 경제 사회 생활문화 세계 IT과학 연예 스포츠 오피니언'
SUB_TARGET = '증권 금융 부동산 산업재계 글로벌경제 경제일반 생활경제 증기벤처'

Crawler = ArticleCrawler()  
Crawler.set_category(*tuple(re.split(' ', TARGET)), subcategories=re.split(' ', SUB_TARGET))
Crawler.set_date_range(2013, 1, 2013, 2)
Crawler.start()

