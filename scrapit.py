import time
import requests
from bs4 import BeautifulSoup as bs

dataFormatGlobal = {"Ticker": "","FullName": "","Date": "",
                    "Price": "","Open": "",
                    "DayH": "","DayL": "","52H": "","52L": "","Volume": "","OpenInterest": "",
                    "datacheck": "TNPODD55VI"}

def durataTranslator(text):
    text = text.replace(' ','').replace('\n','')
    multiplier = 0
    numbers = []
    letters = []

    for l in text:
        if l.isdigit():
            numbers.append(l)
        else:
            letters.append(l)
    if letters[0] == 'm' or letters[0] == 'M':
        multiplier = 1
    if letters[0] == 'y' or letters[0] == 'Y':
        multiplier = 12

    nstr = ''

    for i in numbers:
        nstr = nstr + i

    months = int(nstr) * multiplier

    return months

def mkTranslator(text):
    string = ""
    multiplier = 1

    for char in text:
        if char.isdigit() or char == ".":
            string += char

        if char == "B" or char == "b":
            multiplier = 1000000000
        if char == "M" or char == "m":
            multiplier = 1000000
        if char == "K" or char == "k":
            multiplier = 1000

    num = float(string)
    num = num * multiplier

    return int(num)

##
#/ scraping function
##

def scrapWgb(address):

    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    tableSup = sup.find_all("table")[-1]
    rows = tableSup.find_all("tr")

    #check that we get today Yield and not a past one
    headerCELLS = rows[0].find_all("th")
    yieldIndex = 2
    alert = False
    for i, th in enumerate(headerCELLS):
        if th.text == "Yield":
            yieldIndex = 2
            alert = True
    if not alert:
        print("Yield was not found")
    #check that we get today Yield and not a past one

    maturity = []
    yields = []

    for n, row in enumerate(rows):
        if n > 0:
            selectedCELLS = row.find_all("td")
            maturity.append(durataTranslator(selectedCELLS[1].text))
            yields.append(float(selectedCELLS[yieldIndex].text.replace('%','')))

    return maturity, yields

def scrapCmegroup(address, maxRows = 30, switchOI4eachMonth = True):

    #creating/formatting data from scrapdata
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    tableSup = sup.find("tbody")
    rows = tableSup.find_all("tr")

    table = []

    for i, row in enumerate(rows):

        if i == maxRows:
            break

        selectedCELLS = row.find_all("td",{"id": lambda x: x and 'quotesFuturesProductTable1' in x})

        data = {"Ticker": "",
                "last": "","priorSettle": "","open": "","high": "","low": "","volume": "",
                "datacheck": "OK"}

        totalValues = {'totalOpenInterest': "",'totalVolume': "",'totalBlockTrades': ""}

        try:
            data["Ticker"] = selectedCELLS[0].get('id').split("_")[1]
        except:
            data["datacheck"] = "-NO_ticker-"
            print("'{}' No 'Ticker' CME".format(address))

        for j, cell in enumerate(selectedCELLS):

            try:
                label = cell.get('id').split("_")[2]
            except:
                data["datacheck"] += "-NO_label-"
                print("'{}' No 'label' CME".format(address))

            for key in data:
                if key == label:
                    try:
                        stringValue = cell.text.replace(",","")
                        if stringValue != "-":
                            float(stringValue)
                    except:
                        data["datacheck"] += "-NO_float-"
                        print("'{}' No 'float' CME".format(address))

                    data[key] = stringValue

        table.append(data)

    #// from now Volume page to get Total and OpenInterest

    r = requests.get(address.replace('.html','_quotes_volume_voi.html'))    ### crucial if website change
    c = r.content
    sup = bs(c,"html.parser")

    tableSup = sup.find("tbody")
    rows = tableSup.find_all("tr")

    totalOpenInterest = '--'
    totalVolume = '--'
    totalBlockTrades = '--'

    colNumOpenInterest = 10     ### crucial if website change
    colNumVolume = 3     ### crucial if website change
    colNumBlockTrades = 4     ### crucial if website change

    if rows[-1].find('th').text == 'Totals':
        cells = rows[-1].find_all('td')
        totalOpenInterest = cells[colNumOpenInterest].text.replace(',','')
        totalVolume = cells[colNumVolume].text.replace(',','')
        totalBlockTrades = cells[colNumBlockTrades].text.replace(',','')



    #// from now if switch is on we scrap OpenInterest and maybe OIchange for each month
    ioTable = []

    if switchOI4eachMonth:
        mapMonths = {'JAN': 'F', 'FEB': 'G', 'MAR': 'H', 'APR': 'J',
                     'MAY': 'K', 'JUN': 'M', 'JUL': 'N', 'AUG': 'Q',
                     'SEP': 'U', 'OCT': 'V', 'NOV': 'X', 'DEC': 'Z',}

        for row in rows:

            tag = row.find('th').text
            for key in mapMonths:
                if tag.split(' ')[0] == key:
                    yearLastDigit = tag.split(' ')[1][1]
                    tag = mapMonths[key] + yearLastDigit
                    for dic in table:
                        thisTableMonth = dic['Ticker'][-2] + dic['Ticker'][-1]
                        if thisTableMonth == tag:
                            cells = row.find_all('td')
                            oiData = {'Ticker': dic['Ticker'],
                                      'openInterest': cells[colNumOpenInterest].text.replace(',',''),
                                      'blockTrades': cells[colNumBlockTrades].text.replace(',','')}
                            ioTable.append(oiData)
        #// we now add Open Interest and Block Trades to table{}

    return totalValues, table, ioTable

def scrapMarketwatch(address):
    #creating/formatting data from scrapdata
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    lab = sup.find_all("small",{"class": 'kv__label'})
    val = sup.find_all("span",{"class": 'kv__value kv__primary '})

    data = dataFormatGlobal

    if not len(lab) == len(val):
        print('labels and values mismatch')
        string = ""
        for char in data["datacheck"]:
            string += "-"
        data["datacheck"] = string
        return data

    scrapData = {}

    for i, key in enumerate(lab):
        scrapData[key.text.replace(" ","")] = val[i].text.replace(",","").replace("%","").replace("$","").replace("£","").replace("€","")
    print(scrapData)

    data["Date"] = time.strftime("%Y/%m/%d %H:%M %a")

    try:
        data["Ticker"] = sup.find("span",{"class": "company__ticker"}).text.replace(' ','')
    except:
        data["datacheck"] = data["datacheck"].replace("T","-")
        print("'{}' No 'Ticker'".format(address))

    try:
        data["FullName"] = sup.find("span",{"class":"company__market"}).text.replace(' ','')
    except:
        data["datacheck"] = data["datacheck"].replace("N","-")
        print("'{}' No 'FullName'".format(address))

    try:
        data["Price"] = sup.find("span",{"class":"value"}).text.replace(",","").replace(" ","")
        int_try = float(data["Price"]) #check that an actual number was found for Price
    except:
        data["datacheck"] = data["datacheck"].replace("P","-")
        print("'{}' No 'Price'".format(address))

    try:
        data["Open"] = scrapData["Open"].replace(" ","")
    except:
        data["datacheck"] = data["datacheck"].replace("O","-")
        print("'{}' No 'Open'".format(address))

    try:
        data["DayH"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["DayL"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        data["datacheck"] = data["datacheck"].replace("D","-")
        print("'{}' No 'DayRange'".format(address))

    try:
        data["52H"] = scrapData["52WeekRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["52L"] = scrapData["52WeekRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        data["datacheck"] = data["datacheck"].replace("5","-")
        print("'{}' No '52WeekRange'".format(address))

    try:
        data["Volume"] = str(mkTranslator(sup.find("span",{"class":"volume last-value"}).text))
    except:
        data["datacheck"] = data["datacheck"].replace("V","-")
        print("'{}' No 'Volume'".format(address))

    try:
        data["OpenInterest"] = scrapData["OpenInterest"].replace(" ","")
    except:
        data["datacheck"] = data["datacheck"].replace("I","-")
        print("'{}' No 'OpenInterest'".format(address))

    return data;

def scrapBloomberg(address):
    #creating/formatting data from scrapdata
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    lab = sup.find_all("div",{"class": lambda x: x and 'cell__label' in x})
    val = sup.find_all("div",{"class": lambda x: x and 'cell__value' in x})

    data = dataFormatGlobal

    if not len(lab) == len(val):
        print('labels and values mismatch')
        string = ""
        for char in data["datacheck"]:
            string += "-"
        data["datacheck"] = string
        return data

    scrapData = {}

    for i, key in enumerate(lab):
        scrapData[key.text.replace(" ","")] = val[i].text.replace(",","").replace("%","").replace("$","").replace("£","").replace("€","")
    print(scrapData)

    data["Date"] = time.strftime("%Y/%m/%d %H:%M %a")

    try:
        data["Ticker"] = sup.find("div",{"class": "ticker"}).text.replace(' ','')
    except:
        data["datacheck"] = data["datacheck"].replace("T","-")
        print("No 'Ticker' for '{}'".format(address))

    try:
        data["FullName"] = sup.find("h1",{"class":"name"}).text.replace(' ','')
    except:
        data["datacheck"] = data["datacheck"].replace("N","-")
        print("No 'FullName' for '{}'".format(address))

    try:
        data["Price"] = sup.find("div",{"class":"price"}).text.replace(",","").replace(" ","")
    except:
        data["datacheck"] = data["datacheck"].replace("P","-")
        print("No 'Price' for '{}'".format(address))

    try:
        data["Open"] = scrapData["Open"].replace(" ","")
    except:
        data["datacheck"] = data["datacheck"].replace("O","-")
        print("No 'Open' for '{}'".format(address))

    try:
        data["DayH"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["DayL"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        data["datacheck"] = data["datacheck"].replace("D","-")
        print("No 'DayRange' for '{}'".format(address))

    try:
        data["52H"] = scrapData["52WkRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["52L"] = scrapData["52WkRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        data["datacheck"] = data["datacheck"].replace("5","-")
        print("No '52WkRange' for '{}'".format(address))

    try:
        data["Volume"] = scrapData["Volume"].replace(" ","")
    except:
        data["datacheck"] = data["datacheck"].replace("V","-")
        print("No 'Volume' for '{}'".format(address))

    ''' in Bloomberg non ce mai Oi
    try:
        data["OpenInterest"] = scrapData["OpenInterest"].replace(" ","")
    except:
        data["datacheck"] = data["datacheck"].replace("I","-")
        print("No 'OpenInterest' for '{}'".format(address))
    '''

    return data;

##
#\ scraping function
##

print(scrapWgb('http://www.worldgovernmentbonds.com/country/germany/'))
