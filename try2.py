
import requests
from bs4 import BeautifulSoup as bs


def scrapMarketwatch(address):
    #creating formatting data from scrapdata
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")
    print(sup.find_all("div")[0])


scrapMarketwatch('http://www.marketwatch.com/investing/future/sp%20500%20futures')

print('\n\n\n PRIMOOOOOOOO \n\n PRIMOOOOOOOO \n\n\n')

scrapMarketwatch('https://www.bloomberg.com/quote/USDJPY:CUR')
