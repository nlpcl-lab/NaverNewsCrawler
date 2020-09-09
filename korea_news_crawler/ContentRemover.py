################################################################
# 2020.09.08 articleparser2.py: articleparser.py에 sid2 고려 가능한 버전입니다.
# 경제 category일 경우 subcategory (sid2) 고려합니다.
################################################################
# -*- coding: utf-8, euc-kr -*-
import os
import re
import codecs
import sys
import argparse
import csv
from glob import glob
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

    # 2. open naver news files
    for fname in fnames:
        with codecs.open(fname, 'r', encoding='utf-8', errors='ignore') as fin:
            with codecs.open("{}/{}".format(args.output, re.split('/', fname)[-1]), 'w', encoding='utf-8', errors='ignore') as fout:
                text = fout.read()
                lines = re.split('[\r\n]+', text)
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
                    fin.write('\t'.join(tokens[:4] + [title4] + [body5]) + '\n')
