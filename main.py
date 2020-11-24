import requests
from bs4 import BeautifulSoup


def get_news():
    req = requests.get(golestan_news_source)
    soup = BeautifulSoup(req.content,'html.parser')
    news = soup.find('div',class_='newsitm')
    newsDict = {}
    news_title = news('span','newsitmtitle')[1].b.get_text()
    newsDict['title'] = str(news_title)
    news_dateText = str(news.find('span','newsitmpubdate').get_text())
    pat = r'\d+/\d+/\d+'
    date = re.findall(pat,news_dateText)[0]
    newsDict['date'] = date
    news_body = news.find('div','newsitmbody').div.p
    newsDict['body'] = str(news_body)
    return newsDict