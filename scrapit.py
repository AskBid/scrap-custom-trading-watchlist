import time
import requests
from bs4 import BeautifulSoup as bs
import sys
import os, errno
import re
import sqlite3



dateFormat = '%Y-%m-%d'
timeFormat = '%H:%M'
dayFormat = '%a'
date = time.strftime(dateFormat)
hour = time.strftime(timeFormat)
day = time.strftime(dayFormat)

# try:
#     os.makedirs("logs/logs_" + period)
# except OSError as e:
#     if e.errno != errno.EEXIST:
#         raise

# 01 +-0.5~
# 03 +-0.5~
# 05 +-0.5~
# 07 +-0.5~
# 09 +-0.5~
# 11 +-0.5~
# 13 +-0.5~
# 15 +-0.5~
# 17 +-0.5~
# 19 +-0.5~
# 21 +-0.5~
# 23 +-0.5~


##### start/divert all prints to a log file
# old_stdout = sys.stdout
#
# log_file = open("logs/logs_" + period + "/" + date + ".log","a+")
#
# sys.stdout = log_file
##### start\divert all prints to a log file


#data shared format between Marketwatch and Bloomberg
def getDataFormat():
    dataFormat = {
        "date": "",
        "time": "",
        "day": "",
        "price": "",
        "yclose": "",
        "open": "",
        "dayh": "",
        "dayl": "",
        "h52": "",
        "l52": "",
        "vol": "",
        "oi": "",
        "ticker": ""}
    return dataFormat

def getDataFormatCDS():
    dataFormatCDS = {
        'Name': '',
        'Value': '',
        'Unit': '',}
    return dataFormatCDS

def getDataFormatCME(): #careful if you change this dic labels cus they are actually functional in finding values from the website during scraping process
    dataFormatCME = {
        "Ticker": "",
        "last": "",
        "priorSettle": "",
        "open": "",
        "high": "",
        "low": "",
        "volume": "",
        "openInterest": "",
        "blockTrades": ""}
    return dataFormatCME

def makeDicArr(dic):
    arr = []
    for key in dic:
        arr.append(dic[key])

    return arr

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
#/ scraping functions
##

def scrapSovereignCDS(address):
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    table = sup.find("table",{"id": lambda x: x and 'TitoliStato' in x})
    table = table.find('tbody')
    rows = table.find_all("tr")

    sovereignCDS = [date]

    for row in rows:
        dictRow = getDataFormatCDS()

        name = row.find("td",{"class": lambda x: x and 'Nome' in x})
        name = name.text.replace(' ','').replace('\n','').replace('\t','')

        value = row.find("td",{"class": lambda x: x and 'Rendimento' in x})
        value = value.text.replace(' ','').replace('\n','').replace('\t','')

        dictRow['Name'] = name
        dictRow['Value'] = value
        dictRow['Unit'] = 'Spread'

        sovereignCDS.append(dictRow)

    return sovereignCDS  #ritorna una lista di dizionari 'dataFormatGlobalCDS'

def scrapWsj(address):
    #CDS indexes and big movers for bonds and corporate
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    iframes = sup.find_all("iframe")

    # finds the address where the  table is kept, the real content of iframe
    # and checks if is the only address where markit appears, if not things changed in the page
    src4iframe = 'none'
    for iframe in iframes:
        try:
            src = iframe.attrs['src']
            if 'markit' in src:              #crucial if website changes
                if src4iframe == 'none':
                    src4iframe = src
        except:
            pass
    #check finished we now have an address (srcJust) or 'none'
    html = requests.get(src4iframe).text
    soup = bs(html,'html.parser')
    soup = soup.find('table',{"id": 'CdsIndexTable'})
    soup = soup.find('tbody')

    #take values for all of the tables  ### crucial if website change
    try:
        names = soup.find_all("td",{"class": lambda x: x and 'col1' in x})
        values = soup.find_all("td",{"class": lambda x: x and 'col2' in x})
        unit = soup.find_all("td",{"class": lambda x: x and 'col3' in x})
        bptChange = soup.find_all("td",{"class": lambda x: x and 'col5' in x})
    except:
        print("table CDS column gathering did not work")

    dictCDS = [date]

    for i in range(0,len(names)):
        if 'n.a.' not in values[i].text:
            dictRow = getDataFormatCDS()

            dictRow['Name'] = names[i].text
            dictRow['Value'] = values[i].text
            dictRow['Unit'] = unit[i].text

            dictCDS.append(dictRow)


    return dictCDS

def scrapWorldgovernmentbonds(address):
    #for yeld curves
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

    return date, maturity, yields

def scrapCmegroup(address, ):
    maxRows = 30,
    switchOI4eachMonth = True

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

        data = getDataFormatCME()

        totalValues = {'totalOpenInterest': "",
                       'totalVolume': "",
                       'totalBlockTrades': ""}

        try:
            #the id of the tag in the first TD has the ticker of the instrument i.e. quotesFuturesProductTable1_6EQ7_change
            data["Ticker"] = selectedCELLS[0].get('id').split("_")[1]
            if not data["Ticker"][-1].isdigit():  #small check to see if we actualy got a ticker code
                print("'{}' No 'Ticker' CME".format(address))
        except:
            print("'{}' No 'Ticker' CME".format(address))

        for j, cell in enumerate(selectedCELLS):

            try:
                label = cell.get('id').split("_")[2] ###taking all the labels: quotesFuturesProductTable1_6EQ7_open ::here we take only 'open'
            except:
                print("'{}' No 'label' CME '_' split did not work".format(address))

            for key in data:
                if key == label: ## if one of the label from the dictonary matches any of the labels just gathered, then add value to that dic_key
                    try:
                        stringValue = cell.text.replace("-","").replace(",","").replace("'",".")
                        if stringValue != "":
                            float(stringValue)
                    except:
                        print("'{}' No 'float' CME with {}".format(address,stringValue))

                    data[key] = stringValue

        table.append(data)

    #// from here down Volume page to get Total and OpenInterest

    r = requests.get(address.replace('.html','_quotes_volume_voi.html'))    ### crucial if website change
    c = r.content
    sup = bs(c,"html.parser")

    tableSup = sup.find("tbody")
    rows = tableSup.find_all("tr")

    colNumOpenInterest = 10     ### crucial if website change
    colNumVolume = 3     ### crucial if website change
    colNumBlockTrades = 4     ### crucial if website change

    if rows[-1].find('th').text == 'Totals':   ##last row of the table
        cells = rows[-1].find_all('td')
        totalValues['totalOpenInterest'] = cells[colNumOpenInterest].text.replace(',','')
        totalValues['totalVolume'] = cells[colNumVolume].text.replace(',','')
        totalValues['totalBlockTrades'] = cells[colNumBlockTrades].text.replace(',','')
    else:
        print("'{}' No 'Totals' CME tag was found".format(address))
    #// from now if switch is on we scrap OpenInterest and maybe OIchange for each month

    print(table)

    ioTable = []
    if switchOI4eachMonth:
        mapMonths = {'JAN': 'F', 'FEB': 'G', 'MAR': 'H', 'APR': 'J',
                     'MAY': 'K', 'JUN': 'M', 'JUL': 'N', 'AUG': 'Q',
                     'SEP': 'U', 'OCT': 'V', 'NOV': 'X', 'DEC': 'Z',}

        for row in rows:
            tag = row.find('th').text                          #there is only one th per row and is the ticker text: SEP 17
            for key in mapMonths:                              #
                if tag.split(' ')[0] == key:                   #SEP
                    yearLastDigit = tag.split(' ')[-1][-1]     #7
                    tag = mapMonths[key] + yearLastDigit       #U+7

                    for dic in table:                          #in this for cycle we look at every dic in tabel and when ticker matches our tag, we add open interest and block trades
                        thisTableMonth = dic['Ticker'][-2] + dic['Ticker'][-1]     #GEU7  ---> U+7
                        if thisTableMonth == tag:
                            cells = row.find_all('td')
                            dic['openInterest'] = cells[colNumOpenInterest].text.replace(',','')
                            dic['blockTrades'] = cells[colNumBlockTrades].text.replace(',','')

    arrTable = []
    for dic in table:
        arr = makeDicArr(dic)
        arrTable.append(arr)

    print(table)

    return (' // ' + str(makeDicArr(totalValues)) + ' // ' + str(arrTable))  #ritorna una stringa pronta ad essere scritta sul file .csv

def scrapMarketwatch(address):
    #creating formatting data from scrapdata
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    lab = sup.find_all("small",{"class": 'kv__label'})
    val = sup.find_all("span",{"class": 'kv__value kv__primary '})

    data = getDataFormat()

    if not len(lab) == len(val):
        print("'{}' labels and values mismatch".format(address))
        return data

    scrapData = {}
    #we create a dictionary of scraped data with labels as key and val as values
    for i, key in enumerate(lab):
        string = re.sub("[^0-9. -]", "", val[i].text)
        scrapData[key.text.replace(" ","")] = string.replace('\n', '')


    data["date"] = date
    data["time"] = hour
    data["day"] = day

    try:
        data["ticker"] = sup.find("span",{"class": "company__ticker"}).text.replace(' ','')
    except:
        print("'{}' No 'Ticker'".format(address))

    try:
        priceTab = sup.find("h3",{"class": lambda x: x and 'intraday__price' in x})
        if priceTab.find('bg-quote') != None:
            bgquote = priceTab.find('bg-quote')
            data["price"] = bgquote.text.replace(",","").replace(" ","")
            if data["price"] == '' or data["price"] == None:
                data["price"] = bgquote.get('data-last-raw', [])
                print(bgquote.get('data-last-raw', []))
                print(bgquote)
        else:
            data["price"] = priceTab.find("span",{"class":"value"}).text.replace(",","").replace(" ","")
        float(data["price"]) #check that an actual number was found for Price
    except:
        print("'{}' No 'Price'".format(address))

    try:
        div = sup.find("div",{"class": lambda x: x and 'intraday__close' in x})
        data["yclose"] = re.sub("[^0-9. -]", "", div.find('tbody').text)
    except:
        print("'{}' No 'yClose'".format(address))

    try:
        data["open"] = scrapData["Open"].replace(" ","")
    except:
        print("'{}' No 'Open'".format(address))

    try:
        data["dayh"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["dayl"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        print("'{}' No 'DayRange'".format(address))

    try:
        data["h52"] = scrapData["52WeekRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["l52"] = scrapData["52WeekRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        print("'{}' No '52WeekRange'".format(address))

    try:
        data["vol"] = str(mkTranslator(sup.find("span",{"class":"volume last-value"}).text))
    except:
        if 'index' not in address:
            print("'{}' No 'Volume'".format(address))

    try:
        data["oi"] = scrapData["OpenInterest"].replace(" ","")
    except:
        if 'index' not in address:
            print("'{}' No 'OpenInterest'".format(address))

    return data

def scrapBloomberg(address):
    #creating/formatting data from scrapdata
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    lab = sup.find_all("div",{"class": lambda x: x and 'cell__label' in x})
    val = sup.find_all("div",{"class": lambda x: x and 'cell__value' in x})

    data = getDataFormat()

    if not len(lab) == len(val):
        print("'{}' labels and values mismatch".format(address))
        return data

    scrapData = {}
    #we create a dictionary of scraped data with labels as key and val as values
    for i, key in enumerate(lab):
        scrapData[key.text.replace(" ","")] = re.sub("[^0-9. -]", "", val[i].text)

    data["date"] = date
    data["time"] = hour
    data["day"] = day

    try:
        data["ticker"] = sup.find("div",{"class": "ticker"}).text.replace(' ','')
    except:
        print('{}' "No 'Ticker'".format(address))

    try:
        data["price"] = sup.find("div",{"class":"price"}).text.replace(",","").replace(" ","")
    except:
        print("'{}' No 'Price'".format(address))

    try:
        data["open"] = scrapData["Open"].replace(" ","")
    except:
        print("'{}' No 'Open'".format(address))

    try:
        data["yclose"] = scrapData["PreviousClose"].replace(" ","")
    except:
        print("'{}' No 'yClose'".format(address))

    try:
        data["dayh"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["dayl"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        print("'{}' No 'DayRange'".format(address))

    try:
        data["h52"] = scrapData["52WkRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["l52"] = scrapData["52WkRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        print("'{}' No '52WkRange'".format(address))

    try:
        data["vol"] = scrapData["Volume"].replace(" ","")
    except:
        pass

    return data;

##
#\ scraping functions
##


def selector(address):
    if address == 'empty':
        return ('[' + date + ',None]')

    if 'marketwatch' in address:
        return scrapMarketwatch(address)

    if 'bloomberg' in address:
        return scrapBloomberg(address)

    if 'worldgovernmentbonds.com/country' in address:
        return scrapWorldgovernmentbonds(address)

    if 'sovereign-cds' in address:
        return scrapSovereignCDS(address)

    if 'wsj.com' in address:
        return scrapWsj(address)

    if 'cmegroup' in address:
        return scrapCmegroup(address)

def writeit(csvFile):

    conn = sqlite3.connect('scrapData.db')
    c = conn.cursor()

    csvlist = open(csvFile, 'r')
    for line in csvlist:
        if line.split(',')[0] != "": #avoids completely empty rows in spreadsheet
            fileName = line.split(',')[0]
            address = line.split(',')[1]
            addressFutures = line.split(',')[2].replace('\n','')

            # we take all the main/first adresses unless we have an .Fr file.
            if address != 'empty' and 'd' not in fileName and 'YC' not in fileName:
                this_dic = selector(address)

                c.execute("""CREATE TABLE IF NOT EXISTS {tablename}(
                            date text,
                            time text,
                            day text,
                            price real,
                            yclose real,
                            open real,
                            dayh real,
                            dayl real,
                            h52 real,
                            l52 real,
                            vol integer,
                            oi integer,
                            ticker text)""".format(tablename = fileName))
                conn.commit()

                c.execute("""INSERT INTO {tablename} VALUES (
                :date,
                :time,
                :day,
                :price,
                :yclose,
                :open,
                :dayh,
                :dayl,
                :h52,
                :l52,
                :vol,
                :oi,
                :ticker)""".format(tablename = fileName),

                {'date': this_dic['date'],
                'time': this_dic['time'],
                'day': this_dic['day'],
                'price': this_dic['price'],
                'yclose': this_dic['yclose'],
                'open': this_dic['open'],
                'dayh': this_dic['dayh'],
                'dayl': this_dic['dayl'],
                'h52': this_dic['h52'],
                'l52': this_dic['l52'],
                'vol': this_dic['vol'],
                'oi': this_dic['oi'],
                'ticker': this_dic['ticker']}),


            # then if the cme address is not empty we scrap it
            if addressFutures != 'empty':
                this_dic = selector(addressFutures)

                c.execute("""CREATE TABLE IF NOT EXISTS {tablename}(
                            totalVolume integer,
                            totalOpenInterest integer,
                            totalBlockTrades integer,
                            tableFutures text)""".format(tablename = fileName + '_cme'))
                conn.commit()
            #     fileDataF = open('data/dataF_' + period + '/' + fileName + '.csv', 'a+')
            #     fileDataF.write(date)
            #     fileDataF.write(str(selector(addressFutures)))
            #     fileDataF.write('\n')
            #     fileDataF.close()

            # except:
            #     print('file write not working for {}'.format(fileName))

    csvlist.close

if __name__ == '__main__':
    writeit('macrowatchlist.csv')

##### end/divert all prints to a log file
# sys.stdout = old_stdout
#
# log_file.close()
##### end\divert all prints to a log file
