# coding=utf-8
# from korea_news_crawler.articlecrawler import ArticleCrawler
import re
import os
import sys
import argparse
from korea_news_crawler.articlecrawler2 import ArticleCrawler

# TARGET '정치 사회 생활문화 세계 IT과학 오피니언'
TARGET = '경제'
SUB_TARGET = '증권-금융-부동산-산업재계-글로벌경제-경제일반-생활경제-증기벤처'


parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=__doc__)
parser.add_argument("--start-date", default='2017-01',
                    help="The start year-month date to crawl news")
parser.add_argument("--end-date", default='2017-02',
                    help="The end year-month date to crawl news")
parser.add_argument("--target", default='경제',
                    help="The categories to crawl news(경제-정치-사회-생활문화-세계-IT과학-오피니언)")
parser.add_argument("--sub-target", default='증권-금융-부동산-산업재계-글로벌경제-경제일반-생활경제-증기벤처',
                    help="The sub categories to crawl economy news(증권-금융-부동산-산업재계-글로벌경제-경제일반-생활경제-증기벤처)")

args = parser.parse_args()

Crawler = ArticleCrawler()  
Crawler.set_category(*tuple(re.split('-', args.target)), subcategories=re.split('-', args.sub_target))
Crawler.set_date_range(int(re.split('-', args.start_date)[0]), int(re.split('-', args.start_date)[1]),
                       int(re.split('-', args.end_date)[0]), int(re.split('-', args.end_date)[1]))
Crawler.start()
