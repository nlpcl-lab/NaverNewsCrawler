################################################################
# 2020.09.12 blogcrawler_old.py: 네이버 블로그 수집 코드입니다.
# 검색어 당 최대 10만개 포스팅 처리
# BeautifulSoup 파싱 안되게 막혀있다. request 하루 25000밖에 안되니 쓰지 말 것.
# 예시 및 설명: https://developers.naver.com/docs/search/blog/
# 내 일일 크롤링량, 네이버 개발자 API: https://developers.naver.com/apps/#/myapps/esIPeSYRRIJkZnqf9vgt/overview
# 참고 코드: https://github.com/xotrs/naver-blog-crawler
################################################################
#!/usr/bin/env python
# -*- coding: utf-8, euc-kr -*-
import os
import sys
import argparse
import re
import json
import math
import datetime
import requests
import codecs
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup

now = datetime.datetime.now()
naver_client_id = "esIPeSYRRIJkZnqf9vgt"
naver_client_secret = "_RkZSXRQZl"


def naver_blog_crawling(search_blog_keyword, display_count, sort_type):
    search_result_blog_page_count = get_blog_search_result_pagination_count(search_blog_keyword, display_count)
    with codecs.open('{}_{}_{}'.format(search_blog_keyword, display_count, sort_type), 'w', encoding='utf-8', errors='ignore') as writer:
        get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type, writer)


def get_blog_search_result_pagination_count(search_blog_keyword, display_count):
    encode_search_keyword = urllib.parse.quote(search_blog_keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_keyword
    request = urllib.request.Request(url)

    request.add_header("X-Naver-Client-Id", naver_client_id)
    request.add_header("X-Naver-Client-Secret", naver_client_secret)

    response = urllib.request.urlopen(request)
    response_code = response.getcode()

    if response_code is 200:
        response_body = response.read()
        response_body_dict = json.loads(response_body.decode('utf-8'))

        if response_body_dict['total'] == 0:
            blog_pagination_count = 0
        else:
            blog_pagination_total_count = math.ceil(response_body_dict['total'] / int(display_count))

            if blog_pagination_total_count >= 1000:
                blog_pagination_count = 1000
            else:
                blog_pagination_count = blog_pagination_total_count

            print("키워드 " + search_blog_keyword + "에 해당하는 포스팅 수 : " + str(response_body_dict['total']))
            print("키워드 " + search_blog_keyword + "에 해당하는 블로그 실제 페이징 수 : " + str(blog_pagination_total_count))
            print("키워드 " + search_blog_keyword + "에 해당하는 블로그 처리할 수 있는 페이징 수 : " + str(blog_pagination_count))

        return blog_pagination_count


def get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type, writer):
    encode_search_blog_keyword = urllib.parse.quote(search_blog_keyword)

    for i in range(1, search_result_blog_page_count + 1):
        url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_blog_keyword + "&display=" + str(
            display_count) + "&start=" + str(i) + "&sort=" + sort_type

        request = urllib.request.Request(url)

        request.add_header("X-Naver-Client-Id", naver_client_id)
        request.add_header("X-Naver-Client-Secret", naver_client_secret)

        response = urllib.request.urlopen(request)
        response_code = response.getcode()

        if response_code is 200:
            response_body = response.read()
            response_body_dict = json.loads(response_body.decode('utf-8'))

            for j in range(0, len(response_body_dict['items'])):
                try:
                    blog_post_url = response_body_dict['items'][j]['link'].replace("amp;", "")

                    get_blog_post_content_code = requests.get(blog_post_url, headers={'User-Agent':'Mozilla/5.0'})
                    get_blog_post_content_text = get_blog_post_content_code.text

                    return
                    ### BeautifulSoup 파싱 안되게 막혀있다. request 하루 25000밖에 안되니 쓰지 말 것.
                    get_blog_post_content_soup = BeautifulSoup(get_blog_post_content_text, 'lxml')

                    for link in get_blog_post_content_soup.select('frame#mainFrame'):
                        real_blog_post_url = "http://blog.naver.com" + link.get('src')

                        get_real_blog_post_content_code = requests.get(real_blog_post_url, headers={'User-Agent':'Mozilla/5.0'})
                        get_real_blog_post_content_text = get_real_blog_post_content_code.text

                        get_real_blog_post_content_soup = BeautifulSoup(get_real_blog_post_content_text, 'lxml')

                        for blog_post_content in get_real_blog_post_content_soup.select('div#postViewArea'):
                            blog_post_content_text = blog_post_content.get_text()

                            remove_html_tag = re.compile('<.*?>')

                            blog_post_title = re.sub(remove_html_tag, '', response_body_dict['items'][j]['title'])
                            blog_post_description = re.sub(remove_html_tag, '',
                                                           response_body_dict['items'][j]['description'])
                            blog_post_postdate = datetime.datetime.strptime(response_body_dict['items'][j]['postdate'],
                                                                            "%Y%m%d").strftime("%y.%m.%d")
                            blog_post_blogger_name = response_body_dict['items'][j]['bloggername']
                            blog_post_full_contents = str(blog_post_content_text)
                            blog_post_full_contents = re.sub('\t', '  ', blog_post_full_contents)

                            print("{} {} ({})".format(now.strftime('%Y-%m-%d %H:%M:%S'), blog_post_title, blog_post_url))
                            writer.write('{}\t{}\t{}\t{}\t{}\n'.format(blog_post_postdate, blog_post_blogger_name,
                                                                       blog_post_title, blog_post_full_contents, blog_post_description))
                            # print("포스팅 제목 : " + blog_post_title)
                            # print("포스팅 설명 : " + blog_post_description)
                            # print("포스팅 날짜 : " + blog_post_postdate)
                            # print("블로거 이름 : " + blog_post_blogger_name)
                            # print("포스팅 내용 : " + blog_post_full_contents)
                except:
                    j += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=__doc__)
    parser.add_argument("--keyword", default='가',
                        help="keyword for searching")
    parser.add_argument("--display-num", default='100', help="the number of posts per page to be displayed")
    parser.add_argument("--display-order", default='date', help="the order of pages (sim: similarity, date)")

    args = parser.parse_args()
    print("{} crawler starts.".format(now.strftime('%Y-%m-%d %H:%M:%S')))

    naver_blog_crawling(args.keyword, int(args.display_num), args.display_order)
