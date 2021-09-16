from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import urllib
import bs4

def time_news() :
    time_news_txt = []
    time_news_new = []
    url = 'https://www.daum.net/'
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    for name in soup.find("ol", {"class":"list_hotissue issue_row"}).find_all("a", {"tabindex":"-1"}):
        name = name.text
        time_news_txt.append(name)
    # for name in soup.find("ol", {"class":"lst_realtime_srch _tab_area"}).find_all("em", {"class":"rank new"}):
    #     name = name.text
    #     time_news_new.append(name)
    return time_news_txt
temp = time_news()
print(temp)
