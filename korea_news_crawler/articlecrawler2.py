#!/usr/bin/env python
# -*- coding: utf-8, euc-kr -*-

from time import sleep
from bs4 import BeautifulSoup
from multiprocessing import Process
from korea_news_crawler.exceptions import *
from korea_news_crawler.articleparser import ArticleParser
from korea_news_crawler.writer import Writer
import os
import platform
import calendar
import requests
import re
import random
import logging
import datetime

logger = logging.getLogger(__name__)
now = datetime.datetime.now()
TARGET = '정치 사회' # 생활문화 세계 IT과학 오피니언'
SUB_TARGET = '증권 금융 부동산 산업재계 글로벌경제 경제일반 생활경제 증기벤처'


class ArticleCrawler(object):
    def __init__(self):
        self.categories = {'정치': 100, '경제': 101, '사회': 102, '생활문화': 103, '세계': 104, 'IT과학': 105, '연예': 106, '스포츠': 107,
                           '오피니언': 110}
        self.subcategories = {'증권': 258, '금융': 259, '부동산': 260, '산업재계': 261, '글로벌경제': 262, '경제일반': 263,
                              '생활경제': 310, '증기벤처': 771}
        self.selected_categories = []
        self.selected_subcategories = []
        self.date = {'start_year': 0, 'start_month': 0, 'end_year': 0, 'end_month': 0}
        self.user_operating_system = str(platform.system())
        logger.info("Start article crawler")
        print("{} Start article crawler".format(now.strftime('%Y-%m-%d %H:%M:%S')))

    def set_category(self, *args, subcategories=[]):
        for key in args:
            if self.categories.get(key) is None:
                raise InvalidCategory(key)
        self.selected_categories = args
        self.selected_subcategories = subcategories

    def set_date_range(self, start_year, start_month, end_year, end_month):
        # args = [start_year, start_month, end_year, end_month]
        args = {'start_year': start_year, 'start_month': start_month, 'end_year': end_year, 'end_month': end_month}
        if start_year > end_year:
            raise InvalidYear(start_year, end_year)
        if start_month < 1 or start_month > 12:
            raise InvalidMonth(start_month)
        if end_month < 1 or end_month > 12:
            raise InvalidMonth(end_month)
        if start_year == end_year and start_month > end_month:
            raise OverbalanceMonth(start_month, end_month)
        self.date = args
        # for key, date in zip(self.date, args):
        #     self.date[key] = date
        print(self.date)

    @staticmethod
    def make_news_page_url(category_url, start_year, end_year, start_month, end_month):
        made_urls = []
        for year in range(start_year, end_year + 1):
            if start_year == end_year:
                year_startmonth = start_month
                year_endmonth = end_month
            else:
                if year == start_year:
                    year_startmonth = start_month
                    year_endmonth = 12
                elif year == end_year:
                    year_startmonth = 1
                    year_endmonth = end_month
                else:
                    year_startmonth = 1
                    year_endmonth = 12

            for month in range(year_startmonth, year_endmonth + 1):
                for month_day in range(1, calendar.monthrange(year, month)[1] + 1):
                    if len(str(month)) == 1:
                        month = "0" + str(month)
                    if len(str(month_day)) == 1:
                        month_day = "0" + str(month_day)

                    # 날짜별로 Page Url 생성
                    url = category_url + str(year) + str(month) + str(month_day)

                    # totalpage는 네이버 페이지 구조를 이용해서 page=10000으로 지정해 totalpage를 알아냄
                    # page=10000을 입력할 경우 페이지가 존재하지 않기 때문에 page=totalpage로 이동 됨 (Redirect)
                    totalpage = ArticleParser.find_news_totalpage(url + "&page=10000")
                    for page in range(1, totalpage + 1):
                        made_urls.append(url + "&page=" + str(page))
        return made_urls

    @staticmethod
    def get_url_data(url, max_tries=10):
        remaining_tries = int(max_tries)
        while remaining_tries > 0:
            try:
                return requests.get(url)
            except requests.exceptions:
                sleep(55 + random.randint(1, 77) / 8)
            remaining_tries = remaining_tries - 1
        raise ResponseTimeout()

    def crawling(self, category_name, subcategory_name=''):
        if subcategory_name:
            writer = Writer(category_name=category_name, date=self.date, subcategory_name=subcategory_name)

            # 기사 URL 형식
            url = "http://news.naver.com/main/list.nhn?mode=LSD&mid=sec" + "&sid2=" + str(self.subcategories.get(subcategory_name))
            + "&sid1=" + str(self.categories.get(category_name)) + "&date="

            # start_year년 start_month월 ~ end_year의 end_month 날짜까지 기사를 수집합니다.
            day_urls = self.make_news_page_url(url, self.date['start_year'], self.date['end_year'],
                                               self.date['start_month'], self.date['end_month'])
            logger.info(category_name + "(PID: {}) Urls are generated ({}) & the crawler starts".format(str(os.getpid()), day_urls[:3]))
            print(now.strftime('%Y-%m-%d %H:%M:%S') + ' ' + category_name + "(PID: {}) Urls are generated ({}) & the crawler starts".format(str(os.getpid()), day_urls[:3]))

            for URL in day_urls:
                regex = re.compile("date=(\d+)")
                news_date = regex.findall(URL)[0]

                request = self.get_url_data(URL)

                document = BeautifulSoup(request.content, 'html.parser')

                # html - newsflash_body - type06_headline, type06
                # 각 페이지에 있는 기사들 가져오기
                post_temp = document.select('.newsflash_body .type06_headline li dl')
                post_temp.extend(document.select('.newsflash_body .type06 li dl'))

                # 각 페이지에 있는 기사들의 url 저장
                post = []
                for line in post_temp:
                    post.append(line.a.get('href'))  # 해당되는 page에서 모든 기사들의 URL을 post 리스트에 넣음
                del post_temp

                for content_url in post:  # 기사 URL
                    # 크롤링 대기 시간
                    sleep(0.01 + random.randint(1, 777) / 71425)

                    # 기사 HTML 가져옴
                    request_content = self.get_url_data(content_url)
                    try:
                        document_content = BeautifulSoup(request_content.content, 'html.parser')
                    except:
                        continue

                    try:
                        # 기사 제목 가져옴
                        tag_headline = document_content.find_all('h3', {'id': 'articleTitle'}, {'class': 'tts_head'})
                        text_headline = ''  # 뉴스 기사 제목 초기화
                        text_headline = text_headline + ArticleParser.clear_headline(
                            str(tag_headline[0].find_all(text=True)))
                        if not text_headline:  # 공백일 경우 기사 제외 처리
                            continue

                        # 기사 본문 가져옴
                        tag_content = document_content.find_all('div', {'id': 'articleBodyContents'})
                        text_sentence = ''  # 뉴스 기사 본문 초기화
                        text_sentence = text_sentence + ArticleParser.clear_content(
                            str(tag_content[0].find_all(text=True)))
                        if not text_sentence:  # 공백일 경우 기사 제외 처리
                            continue

                        # 기사 언론사 가져옴
                        tag_company = document_content.find_all('meta', {'property': 'me2:category1'})
                        text_company = ''  # 언론사 초기화
                        text_company = text_company + str(tag_company[0].get('content'))
                        if not text_company:  # 공백일 경우 기사 제외 처리
                            continue

                        # CSV 작성
                        wcsv = writer.get_writer_csv()
                        wcsv.writerow(
                            [news_date, category_name, subcategory_name, text_company, text_headline, text_sentence, content_url])

                        del text_company, text_sentence, text_headline
                        del tag_company
                        del tag_content, tag_headline
                        del request_content, document_content

                    except Exception as ex:  # UnicodeEncodeError ..
                        # wcsv.writerow([ex, content_url])
                        del request_content, document_content
                        pass

            writer.close()
        else:
            writer = Writer(category_name=category_name, date=self.date)

            # 기사 URL 형식
            url = "http://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=" + str(
                self.categories.get(category_name)) + "&date="

            # start_year년 start_month월 ~ end_year의 end_month 날짜까지 기사를 수집합니다.
            day_urls = self.make_news_page_url(url, self.date['start_year'], self.date['end_year'],
                                               self.date['start_month'], self.date['end_month'])
            logger.info(category_name + "(PID: {}) Urls are generated ({}) & the crawler starts".format(str(os.getpid()), day_urls[:3]))
            print(now.strftime('%Y-%m-%d %H:%M:%S') + ' ' + category_name + "(PID: {}) Urls are generated ({}) & the crawler starts".format(str(os.getpid()), day_urls[:3]))

            for URL in day_urls:
                regex = re.compile("date=(\d+)")
                news_date = regex.findall(URL)[0]

                request = self.get_url_data(URL)

                document = BeautifulSoup(request.content, 'html.parser')

                # html - newsflash_body - type06_headline, type06
                # 각 페이지에 있는 기사들 가져오기
                post_temp = document.select('.newsflash_body .type06_headline li dl')
                post_temp.extend(document.select('.newsflash_body .type06 li dl'))

                # 각 페이지에 있는 기사들의 url 저장
                post = []
                for line in post_temp:
                    post.append(line.a.get('href'))  # 해당되는 page에서 모든 기사들의 URL을 post 리스트에 넣음
                del post_temp

                for content_url in post:  # 기사 URL
                    # 크롤링 대기 시간
                    sleep(0.01 + random.randint(1, 777) / 71425)

                    # 기사 HTML 가져옴
                    request_content = self.get_url_data(content_url)
                    try:
                        document_content = BeautifulSoup(request_content.content, 'html.parser')
                    except:
                        continue

                    try:
                        # 기사 제목 가져옴
                        tag_headline = document_content.find_all('h3', {'id': 'articleTitle'}, {'class': 'tts_head'})
                        text_headline = ''  # 뉴스 기사 제목 초기화
                        text_headline = text_headline + ArticleParser.clear_headline(
                            str(tag_headline[0].find_all(text=True)))
                        if not text_headline:  # 공백일 경우 기사 제외 처리
                            continue

                        # 기사 본문 가져옴
                        tag_content = document_content.find_all('div', {'id': 'articleBodyContents'})
                        text_sentence = ''  # 뉴스 기사 본문 초기화
                        text_sentence = text_sentence + ArticleParser.clear_content(str(tag_content[0].find_all(text=True)))
                        if not text_sentence:  # 공백일 경우 기사 제외 처리
                            continue

                        # 기사 언론사 가져옴
                        tag_company = document_content.find_all('meta', {'property': 'me2:category1'})
                        text_company = ''  # 언론사 초기화
                        text_company = text_company + str(tag_company[0].get('content'))
                        if not text_company:  # 공백일 경우 기사 제외 처리
                            continue

                        # CSV 작성
                        wcsv = writer.get_writer_csv()
                        wcsv.writerow([news_date, category_name, text_company, text_headline, text_sentence, content_url])

                        del text_company, text_sentence, text_headline
                        del tag_company
                        del tag_content, tag_headline
                        del request_content, document_content

                    except Exception as ex:  # UnicodeEncodeError ..
                        # wcsv.writerow([ex, content_url])
                        del request_content, document_content
                        pass
            writer.close()

        logger.info("End article crawler ({})".format(category_name))
        print("{} End article crawler ({})".format(now.strftime('%Y-%m-%d %H:%M:%S'), category_name))

    def start(self):
        # MultiProcess 크롤링 시작
        for category_name in self.selected_categories:
            if category_name == '경제':
                for subcategory_name in self.selected_subcategories:
                    proc = Process(target=self.crawling, args=(category_name, subcategory_name))
                    proc.start()
            else:
                proc = Process(target=self.crawling, args=(category_name,))
                proc.start()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
    )
    Crawler = ArticleCrawler()
    Crawler.set_category(*tuple(re.split(' ', TARGET)), subcategories=re.split(' ', SUB_TARGET))
    # Crawler.set_category("경제", "IT과학", subcategories=['금융', '증권'])
    Crawler.set_date_range(2017, 1, 2017, 2)
    Crawler.start()
