################################################################
# 2020.09.08 ContentRemover.py
# 신한 Naver news data에서 title과 body text를 전처리 합니다.
#   - 기자 이름, 출판사 광고, 관련 뉴스 문구 삭제
#   - 영어, 한문, 한글 외 언어, 특수 문자 제거
#   - 인터넷 매크로 문구, 불필요한 유니코드 제거
#   - 중복 기사 삭제 (필터링 후 제목 일치 여부 기준)
################################################################
# -*- coding: utf-8, euc-kr -*-
import os
import re
import codecs
import sys
import argparse
import csv
from glob import glob
from collections import OrderedDict
from korea_news_crawler.articleparser import ArticleParser

fieldnames = ['link', 'date', 'publisher', 'thumbnail', 'title', 'body']

def main():
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=__doc__)
    parser.add_argument("input", help="wiki directory")
    parser.add_argument("output", help="output file name")
    args = parser.parse_args()

    # 1. list naver news list (glob)
    fnames = glob(args.input + '/*')

    try:
        if not (os.path.isdir(args.output)):
            os.makedirs(os.path.join(args.output))
    except OSError as e:
        print("Failed to create directory")
        raise

    TOTAL_DUPLICATED_NUM = 0
    # 2. open naver news files
    for fname in fnames:
        news_dict = OrderedDict()
        duplicated_num = 0
        with codecs.open(fname, 'r', encoding='utf-8', errors='ignore') as fin:
            with codecs.open("{}/{}/{}".format('/'.join(re.split('/', args.input)[:-1]), args.output,
                                               re.split('[/\\\\]', fname)[-1]), 'w', encoding='utf-8',
                             errors='ignore') as fout:
                text = fin.read()
                lines = re.split('[\r\n]+', text)
                initial_news_num = len(lines)
                lines = [x for x in lines if x]
                for line in lines:
                    tokens = re.split('\t', line)
                    # 3. clear naver news text
                    title4 = ArticleParser.clear_headline(tokens[4])
                    if not title4:  # 공백일 경우 기사 제외 처리
                        continue
                    body5 = ArticleParser.clear_content(tokens[5])
                    if not body5:  # 공백일 경우 기사 제외 처리
                        continue
                    if tokens[4] in news_dict:
                        duplicated_num += 1
                        TOTAL_DUPLICATED_NUM += 1
                    news_dict[tokens[4]] = '\t'.join(tokens[:4] + [title4] + [body5]) + '\n'

                # 4. write clean news texts
                after_total_news_num = len(news_dict)
                for _, text in news_dict.items():
                    fout.write(text)

        after_filter_news_num = initial_news_num - duplicated_num - after_total_news_num
        print("{} (initial / filtered / duplicated / preprocessed): {} / {} / {} / {}".format
              (re.split('[/\\\\]', fname)[-1], initial_news_num, after_filter_news_num, duplicated_num, after_total_news_num))

    print("Total duplicated news num: {}".format(TOTAL_DUPLICATED_NUM))

    # 중복 기사 제거 기능 없음, 빠른 처리속도
    """
    for fname in fnames:
        with codecs.open(fname, 'r', encoding='utf-8', errors='ignore') as fin:
            with codecs.open("{}/{}/{}".format('/'.join(re.split('/', args.input)[:-1]), args.output, re.split('[/\\\\]', fname)[-1]), 'w', encoding='utf-8', errors='ignore') as fout:
                text = fin.read()
                lines = re.split('[\r\n]+', text)
                lines = [x for x in lines if x]
                for line in lines:
                    tokens = re.split('\t', line)
                    # 3. clear naver news text
                    title4 = ArticleParser.clear_headline(tokens[4])
                    if not title4:  # 공백일 경우 기사 제외 처리
                        continue
                    body5 = ArticleParser.clear_content(tokens[5])
                    if not body5:  # 공백일 경우 기사 제외 처리
                        continue
                    # 4. write clean news texts
                    fout.write('\t'.join(tokens[:4] + [title4] + [body5]) + '\n')
    """


if __name__ == "__main__":
    main()