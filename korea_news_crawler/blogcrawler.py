# prerequisite: https://chromedriver.storage.googleapis.com/index.html?path=85.0.4183.87/
# linux:
# 1. path = chromedriver 절대경로 입력(wget https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_linux64.zip)
# 2. 모든 webdriver.Chrome(path)로 변경
# 3. chrome_options로 --headless, --no-sandbox, --disable-dev-shm-usage 추가.

import re
import sys
import os
import random
import argparse
import datetime
import codecs
import pandas as pd
import platform
import time
import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

now = datetime.datetime.now()


def report(string):
    print("{} {}".format(now.strftime('%Y-%m-%d %H:%M:%S'), string))


def date_generator(start, end):
    last_date_key = '0131 0228 0331 0430 0531 0630 0731 0831 0930 1031 1130 1231'
    last_date_value = '0201 0301 0401 0501 0601 0701 0801 0901 1001 1101 1201 0101'
    last_date_key = re.split(' ', last_date_key)
    last_date_value = re.split(' ', last_date_value)
    last_date = {}
    for key, value in zip(last_date_key, last_date_value):
        last_date[key] = value

    result = []
    start = int(start)
    end = int(end)

    i = start
    assert start < end
    while i < end:
        result.append(str(i))
        if str(i)[-4:] == '1231':
            i = i + 10000 - 1130
        elif str(i)[-4:] in last_date:
            i = int(str(i)[:4] + last_date[str(i)[-4:]])
        else:
            i += 1

    return result


def get_driver():
    if str(platform.system()) == 'Windows':
        path = "chromedriver.exe"
        driver = webdriver.Chrome(path)
    else:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        path = "/home/jae4258/project/NaverNewsCrawler/korea_news_crawler/chromedriver"
        driver = webdriver.Chrome(path, chrome_options=options)
    return driver


def main(args, fout):
    # Step 1. 크롬 웹브라우저 실행
    driver = get_driver()
    # 사이트 주소는 네이버
    driver.get('http://www.naver.com')
    time.sleep(2 + 1/17 - random.randint(1, 100)/700)

    # Step 2. 네이버 검색창에 "검색어" 검색
    element = driver.find_element_by_id("query")
    element.send_keys(args.keyword)  # query_txt는 위에서 입력한 '이재용'
    element.submit()

    # Step 3. "블로그" 카테고리 선택
    driver.find_element_by_link_text("블로그").click()  # .click() 괄호 안을 눌러라는 뜻

    # Step 4. 오른쪽의 검색 옵션 버튼 클릭
    driver.find_element_by_id("_search_option_btn").click()

    # Step 5. 정렬 : "관련도순"
    # 개발자 도구에서 정렬 버튼의 id 가 보이지 않습니다.
    # 이럴 경우 쉽게 사용할 수 있는 방법이 바로 xpath 를 이용하는 방법입니다.
    # xpath는 개발자 도구에서 해당 메뉴 부분을 마우스 오른쪽 버튼을 누르고
    # copy -> copy xpath 를 선택하면 됩니다
    driver.find_element_by_xpath("""//*[@id="snb"]/div/ul/li[1]/a""").click()  # 정렬 버튼의 xpath 클릭
    driver.find_element_by_xpath("""//*[@id="snb"]/div/ul/li[1]/div/ul/li[1]/a""").click()  # 관련도순 xpath

    # Step 6. 날짜 입력
    driver.find_element_by_xpath("""//*[@id="snb"]/div/ul/li[2]/a""").click()
    time.sleep(2 + 1/11 - random.randint(1, 1000)/7000)

    # 이 부분이 아주 중요합니다.
    # 날짜 부분에 날짜를 입력할 때 입력 속도가 너무 빠를 경우 날짜가 입력이 되다가
    # 오타가 나오는 경우가 많습니다.
    # 그래서 날짜를 입력할 때 for 반복문을 사용해서 1 글자씩 입력하도록 코딩했습니다.

    # 시작 날짜 입력하기
    s_date = driver.find_element_by_xpath("""//*[@id="blog_input_period_begin"]""")
    driver.find_element_by_xpath("""//*[@id="blog_input_period_begin"]""").click()
    s_date.clear()  # 날짜 입력 부분에 기존에 입력되어 있던 날짜를 제거합니다.
    time.sleep(1 + 1/11 - random.randint(1, 1000)/7000)
    # 아래 코드가 날짜를 for 반복문으로 1 글자씩 입력하는 부분입니다.
    for c in args.start_date:
        s_date.send_keys(c)
        time.sleep(0.1)

    # 종료 날짜 입력하기
    e_date = driver.find_element_by_xpath("""//*[@id="blog_input_period_end"]""")
    driver.find_element_by_xpath("""//*[@id="blog_input_period_end"]""").click()
    e_date.clear()
    time.sleep(1 + 1/11 - random.randint(1, 1000)/7000)

    for c in args.end_date:
        e_date.send_keys(c)
        time.sleep(0.1)

    # Step7. 날짜 입력 "적용하기" 버튼을 클릭 합니다.
    driver.find_element_by_class_name("tx").click()
    time.sleep(3 + 17/97 - random.randint(1, 999)/7000)

    # # Step 8. 상세 검색버튼을 클릭 후 제외할 단어들을 설정합니다.
    # ele2 = driver.find_element_by_id("inpop3")
    # ele2.send_keys(query_txt2)
    # ele2.send_keys(',')
    # ele2.send_keys(query_txt3)
    # driver.find_element_by_css_selector(".btn_ft.ty_green._search").click( )

    ## 글 url 크롤링 시작
    report("blog crawler ready.")

    url_list = []
    title_list = []

    # ★몇개의 페이지를 크롤링할지 선택(기본 1page 당 10 blogs, 최대 1000 blogs 크롤링가능)
    total_page = 100    # max 100
    for i in tqdm(range(0, total_page)):  # 페이지 번호
        i = i * 10 + 1  # 1 page당 10 blogs
        url = "https://search.naver.com/search.naver?date_from={0}&date_option=8&date_to={1}&dup_remove=1&nso=p%3Afrom{2}to{3}post_blogurl=&post_blogurl_without=&query={4}&sm=tab_pge&srchby=all&st=sim&where=post&start={5}"\
            .format(args.start_date, args.end_date, args.start_date, args.end_date, args.keyword, i)
        driver.get(url)
        time.sleep(0.5 + 1/7 - random.randint(1, 999)/7000)

        # URL 크롤링 시작
        titles = "a.sh_blog_title._sp_each_url._sp_each_title"
        article_raw = driver.find_elements_by_css_selector(titles)
        #     article_raw

        # url 크롤링 시작
        for article in article_raw:
            url = article.get_attribute('href')
            url_list.append(url)

        # 제목 크롤링 시작
        for article in article_raw:
            title = article.get_attribute('title')
            title_list.append(title)

            # print(title)

    report('url갯수: {}'.format(len(url_list)))
    report('title갯수: {}'.format(len(title_list)))
    driver.close()
    time.sleep(3 + 17 / 97 - random.randint(1, 999) / 7000)     # 닫으면 1초정도 대기

    df = pd.DataFrame({'url': url_list, 'title': title_list})

    # ★수집할 글 갯수
    number = len(df['url'])
    for i in tqdm(range(0, number)):
        # 글 띄우기
        url = df['url'][i]
        iterative_crawling_blogs(df, url, fout)


def iterative_crawling_blogs(df, url, fout):
    try:
        driver = get_driver()
        driver.get(url)  # 글 띄우기
        time.sleep(2 + 8 / 97 - random.randint(1, 999) / 7000)
    except:
        try:
            driver.close()
            time.sleep(3 + 17/97 - random.randint(1, 999)/7000)
            driver = get_driver()
            driver.get(url)  # 글 띄우기
            time.sleep(2 + 8 / 97 - random.randint(1, 999) / 7000)
        except:
            return

    # 크롤링
    try:
        # iframe 접근
        driver.switch_to.frame('mainFrame')

        target_info = {}

        # 제목 크롤링 시작
        overlays = ".se-fs-.se-ff-"
        tit = driver.find_element_by_css_selector(overlays)  # title
        title = tit.text

        # 글쓴이 크롤링 시작
        overlays = ".nick"
        nick = driver.find_element_by_css_selector(overlays)  # nick
        nickname = nick.text
        nickname = re.sub('[\t\r\n]+', '  ', nickname)

        # 날짜 크롤링
        overlays = ".se_publishDate.pcol2"
        date = driver.find_element_by_css_selector(overlays)  # date
        _datetime = date.text

        # 내용 크롤링
        overlays = ".se-component.se-text.se-l-default"
        contents = driver.find_elements_by_css_selector(overlays)  # date

        content_list = []
        for content in contents:
            content_list.append(content.text)

        content_str = ' '.join(content_list)
        content_str = re.sub('[\t\r\n]+', '  ', content_str)

        # 글 하나는 target_info라는 딕셔너리에 담기게 되고,
        target_info['title'] = title
        target_info['nickname'] = nickname
        target_info['datetime'] = _datetime
        target_info['content'] = content_str

        report("{}: {} saved".format(i, title))
        fout.write("{}\t{}\t{}\t{}\t{}\n".format(_datetime, title, nickname, content_str, url))

        # 글 하나 크롤링 후 크롬 창 닫기
        driver.close()
        time.sleep(1 + 17 / 97 - random.randint(1, 999) / 7000)

        # 에러나면 현재 크롬창 닫고 다음 글(i+1)로 이동
    except:
        driver.close()
        time.sleep(1 + 17/97 - random.randint(1, 999)/7000)
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=__doc__)
    parser.add_argument("--keywords", default='오-가-다-어-이-아',
                        help="keywords separated by '-' for searching")
    parser.add_argument("--start", default='20200106', help="the start date to crawl blogs")
    parser.add_argument("--end", default='20200901', help="the end date to crawl blogs")
    # parser.add_argument("--display-num", default='100', help="the number of posts per page to be displayed")
    # parser.add_argument("--display-order", default='date', help="the order of pages (sim: similarity, date)")

    args = parser.parse_args()
    report("blog crawler starts.")

    for i in date_generator(args.start, args.end):
        args.start_date = i
        args.end_date = i
        for keyword in re.split('-', args.keywords):
            args.keyword = keyword
            with codecs.open('../data/blogs/Blog_{}_{}_{}.txt'.format(args.keyword, args.start_date, args.end_date), 'w', encoding='utf-8', errors='ignore') as fout:
                report('open Blog_{}_{}_{}.txt'.format(args.keyword, args.start_date, args.end_date))
                main(args, fout)
                report('close Blog_{}_{}_{}.txt'.format(args.keyword, args.start_date, args.end_date))
                time.sleep(3 - random.randint(1, 999) / 7000)
