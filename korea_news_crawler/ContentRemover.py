################################################################
# 2020.09.08 ContentRemover.py
# input text (신한 Naver news data)에서 title과 body text를 전처리 합니다.
#   - 기자 이름, 출판사 광고, 관련 뉴스 문구 삭제
#   - 영어, 한문, 한글 외 언어, 특수 문자 제거
#   - 인터넷 매크로 문구, 불필요한 유니코드 제거
#   - 중복/빈 기사 삭제 (필터링 후 제목 일치 여부 기준)
# 실행 예제: python ContentRemover.py --input <input directory> --output preprocessed --input-delimeter \t --input-fieldnames link-date-publisher-thumbnail-title-body
# python ContentRemover.py --input D:/dataset/nnc --output nnc_preprocessed --input-delimeter , --input-fieldnames date-category-subcategory-publisher-title-body-link
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
try:
    from korea_news_crawler.articleparser import ArticleParser
except:
    from articleparser import ArticleParser


def main():
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=__doc__)
    parser.add_argument("--input", help="input directory including text files")
    parser.add_argument("--input-delimeter", default='\t', help="a delimiter which the input text contains")
    parser.add_argument("--input-fieldnames", default='link-date-publisher-thumbnail-title-body', help="a list of column names")
    parser.add_argument("--output", help="new directory name (not pathway)")
    args = parser.parse_args()
    fieldnames = re.split('-', args.input_fieldnames)
    title_idx = fieldnames.index('title')
    body_idx = fieldnames.index('body')

    # 1. list naver news list (glob)
    fnames = glob(args.input + '/*')

    with codecs.open('content_remover.log', 'w', encoding='utf-8', errors='ignore') as logwriter:
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
                        tokens = re.split(args.input_delimeter, line)
                        if len(tokens) != len(fieldnames):    # 형식에 벗어난 기사 예외 처리
                            continue
                        # 3. clear naver news text
                        title = ArticleParser.clear_headline(tokens[title_idx])
                        if not title:  # 공백일 경우 기사 제외 처리
                            continue
                        body = ArticleParser.clear_content(tokens[body_idx])
                        if not body:  # 공백일 경우 기사 제외 처리
                            continue
                        if tokens[title_idx] in news_dict:
                            duplicated_num += 1
                            TOTAL_DUPLICATED_NUM += 1

                        # 4. save clean text in dict
                        result = []
                        for i, token in enumerate(tokens):
                            if i == title_idx:
                                result.append(title)
                            elif i == body_idx:
                                result.append(body)
                            else:
                                result.append(token)
                        news_dict[tokens[title_idx]] = args.input_delimeter.join(result) + '\n'

                    # 5. write clean news texts
                    after_total_news_num = len(news_dict)
                    for _, text in news_dict.items():
                        fout.write(text)

            after_filter_news_num = initial_news_num - duplicated_num - after_total_news_num
            print("{} (initial / filtered / duplicated / preprocessed): {} / {} / {} / {}".format
                  (re.split('[/\\\\]', fname)[-1], initial_news_num, after_filter_news_num, duplicated_num, after_total_news_num))
            logwriter.write("{} (initial / filtered / duplicated / preprocessed): {} / {} / {} / {}\n".format
                            (re.split('[/\\\\]', fname)[-1], initial_news_num, after_filter_news_num, duplicated_num, after_total_news_num))

        print("Total duplicated news num: {}".format(TOTAL_DUPLICATED_NUM))
        logwriter.write("Total duplicated news num: {}".format(TOTAL_DUPLICATED_NUM))


if __name__ == "__main__":
    main()