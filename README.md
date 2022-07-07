# KoreaNewsCrawler
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
```
이 크롤러는 아래 저작자 코드를 기반으로 수정된 프로젝트입니다.
https://github.com/lumyjuwon/KoreaNewsCrawler
```

- python3 linux / window 에서 실행가능
- main.py (or articlecrawler2.py): naver news 수집
- ContentRemover.py: 수집된 텍스트 전처리(중복 문서 제거와 불필요한 문자 제거)

## Installation

unzip project or git clone

## Steps for crawling naver news
파라미터에 들어갈 수 있는 카테고리는 '정치', '경제', '사회', '생활문화', 'IT과학', '세계', '오피니언'입니다.  
서브 카테고리는 증권-금융-부동산-산업재계-글로벌경제-경제일반-생활경제-증기벤처 입니다.

각 column은 date-category-publisher-title-body-link 이며,
경제 뉴스의 column은 date-subcategory-category-publisher-title-body-link 입니다.

* main.py: crawl 2016-07~2016-07 economy news with 8 sub categories, saving the news in this project.
`
python main.py --start-date 2016-07 --end-date 2016-07 --target 경제 --sub-target 증권-금융-부동산-산업재계-글로벌경제-경제일반-생활경제-증기벤처
`
* main.py: crawl 2010-09~2010-12 general news with 6 categories
`
python main.py --start-date 2010-09 --end-date 2010-12 --target 정치-사회-세계-생활문화-IT과학-오피니언 --sub-target 증권-금융-부동산-산업재계-글로벌경제-경제일반-생활경제-증기벤처
`
## Steps for cleaning crawled news

* ContentRemover.py: clean the news from <input_dir> to <output_dir>
`
python ContentRemover.py --input naver_news --output naver_news_preprocessed --input-delimeter \t --input-fieldnames link-date-publisher-thumbnail-title-body
`

## User Python Installation
  * **KoreaNewsCrawler**

    ``` pip install KoreaNewsCrawler ```
## Method

* **set_category(category_name)**
  
 이 메서드는 수집하려고자 하는 카테고리는 설정하는 메서드입니다.  

 파라미터는 여러 개 들어갈 수 있습니다.  
 category_name: 정치, 경제, 사회, 생활문화, IT과학, 세계, 오피니언 or politics, economy, society, living_culture, IT_science, world, opinion
  
* **set_date_range(startyear, startmonth, endyear, endmonth)**
  
 이 메서드는 수집하려고자 하는 뉴스의 기간을 의미합니다. 기본적으로 startmonth월부터 endmonth월까지 데이터를 수집합니다.
  
* **start()**
  
 이 메서드는 크롤링 실행 메서드입니다.
  
 Colum A: 기사 날짜  
 Colum B: 기사 카테고리  
 Colum C: 언론사  
 Colum D: 기사 제목  
 Colum E: 기사 본문  
 Colum F: 기사 주소  
 
 수집한 모든 데이터는 csv 확장자로 저장됩니다.  

## License
 Apache License 2.0
 
