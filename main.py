# coding=utf-8
from korea_news_crawler.articlecrawler import ArticleCrawler

Crawler = ArticleCrawler()  
Crawler.set_category('economy', '정치', '경제', '사회', '생활문화', 'IT과학', '세계', '오피니언')  
Crawler.set_date_range(2013, 1, 2013, 2)
Crawler.start()

