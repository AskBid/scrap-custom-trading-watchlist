import time
import requests
from bs4 import BeautifulSoup as bs
import sys
import os, errno
import re #used to get rid of all the characters which are not numbers or dashes
import sqlite3
import argparse

def getTimestamp(h_m):
    hours = int(h_m.split(":")[0])
    minutes = int(h_m.split(":")[1])
    tot_mins = (hours * 60) + minutes
    return tot_mins

date = time.strftime('%Y-%m-%d')
hour = time.strftime('%H:%M')
timestamp = getTimestamp(hour)
day = time.strftime('%a')

logfile = None

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

def makeDicArr(dic): #to avoid problems with older versions of Python where dictionary order is messed up we need to convert dictionary in array to preserve order
    arr = []

    arr.append(dic['Ticker'])
    arr.append(dic['last'])
    arr.append(dic['priorSettle'])
    arr.append(dic['open'])
    arr.append(dic['high'])
    arr.append(dic['low'])
    arr.append(dic['volume'])
    arr.append(dic['openInterest'])
    arr.append(dic['blockTrades'])

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

    dictCDS = []

    for row in rows:
        dictRow = getDataFormatCDS()

        name = row.find("td",{"class": lambda x: x and 'Nome' in x})
        name = name.text.replace(' ','').replace('\n','').replace('\t','')

        value = row.find("td",{"class": lambda x: x and 'Rendimento' in x})
        value = value.text.replace(' ','').replace('\n','').replace('\t','')

        dictRow['Name'] = name
        dictRow['Value'] = value
        dictRow['Unit'] = 'Spread'

        dictCDS.append(dictRow)

    return dictCDS  #ritorna una lista di dizionari 'dataFormatGlobalCDS'

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
        logfile.write('{}: {} table CDS column gathering did not work...\n'.format(hour, address))

    dictCDS = []

    for i in range(0,len(names)):
        if 'n.a.' not in values[i].text:
            dictRow = getDataFormatCDS()

            dictRow['Name'] = names[i].text
            dictRow['Value'] = values[i].text
            dictRow['Unit'] = unit[i].text

            dictCDS.append(dictRow)

    return dictCDS  #ritorna una lista di dizionari 'dataFormatGlobalCDS'

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
        print("Yield was not found _YC")
        logfile.write('{}: {} Yield was not found _YC...\n'.format(hour, address))
    #check that we get today Yield and not a past one

    maturity = []
    yields = []

    for n, row in enumerate(rows):
        if n > 0:
            selectedCELLS = row.find_all("td")
            maturity.append(durataTranslator(selectedCELLS[1].text))
            yields.append(float(selectedCELLS[yieldIndex].text.replace('%','')))

    return maturity, yields

def scrapCmegroup(address):
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

        totalValues = {'totalOI': "",
                       'totalVol': "",
                       'totalBT': ""}

        try:
            #the id of the tag in the first TD has the ticker of the instrument i.e. quotesFuturesProductTable1_6EQ7_change
            data["Ticker"] = selectedCELLS[0].get('id').split("_")[1]
            if not data["Ticker"][-1].isdigit():  #small check to see if we actualy got a ticker code
                print("'{}' No 'Ticker' CME cus last character was not digit".format(address))
                logfile.write("{}: '{}' No 'Ticker' CME cus last character was not digit...\n".format(hour, address))
        except:
            print("'{}' No 'Ticker' CME".format(address))
            logfile.write("{}: '{}' No 'Ticker' CME...\n".format(hour, address))

        for j, cell in enumerate(selectedCELLS):

            try:
                label = cell.get('id').split("_")[2] ###taking all the labels: quotesFuturesProductTable1_6EQ7_open ::here we take only 'open'
            except:
                print("'{}' No 'label' CME '_' split did not work".format(address))
                logfile.write("{}: '{}' No 'label' CME '_' split did not work...\n".format(hour, address))

            for key in data:
                if key == label: ## if one of the label from the dictonary matches any of the labels just gathered, then add value to that dic_key
                    try:
                        stringValue = cell.text.replace("-","").replace(",","").replace("'",".")
                        if stringValue != "":
                            float(stringValue)
                    except:
                        print("'{}' No 'float' CME with {}".format(address, stringValue))
                        logfile.write("{}: '{}' No 'float' CME with {}...\n".format(hour, address, stringValue))

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
        totalValues['totalOI'] = cells[colNumOpenInterest].text.replace(',','')
        totalValues['totalVol'] = cells[colNumVolume].text.replace(',','')
        totalValues['totalBT'] = cells[colNumBlockTrades].text.replace(',','')
    else:
        print("'{}' No 'Totals' CME tag was found".format(address))
        logfile.write("{}: '{}' No 'Totals' CME tag was found...\n".format(hour, address))
    #// from now if switch is on we scrap OpenInterest and maybe OIchange for each month

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

    maxVol = 0
    maxDic = {}
    for dic in table:
        if int(dic['volume']) >= maxVol:
            maxVol = int(dic['volume'])
            maxDic = dic

    arrTable = []
    for dic in table:
        arr = makeDicArr(dic)
        arrTable.append(arr)

    return (totalValues, makeDicArr(maxDic), arrTable)

def scrapMarketwatch(address):
    #creating formatting data from scrapdata
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    lab = sup.find_all("small",{"class": 'kv__label'})
    val = sup.find_all("span",{"class": 'kv__value kv__primary '})

    data = getDataFormat()

    if not len(lab) == len(val):
        toCull = len(lab) - len(val)
        if toCull > 0:
            for i in range(0,toCull):
                lab.pop()
        else:
            for i in range(0,toCull):
                val.pop()
        print("'{}' labels and values mismatch was fixed".format(address))
        logfile.write("{}: '{}' labels and values mismatch was fixed...\n".format(hour, address))
        # for i, item in enumerate(val):
        #     print("{}:  {}".format(i, item))
        # print('')
        # for i, item in enumerate(lab):
        #     print("{}:  {}".format(i, item))


    scrapData = {}
    #we create a dictionary of scraped data with labels as key and val as values
    for i, key in enumerate(lab):
        string = re.sub("[^0-9. -]", "", val[i].text)
        scrapData[key.text.replace(" ","")] = string.replace('\n', '')


    data["date"] = date
    data["time"] = hour
    data["day"] = day

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
    except Exception as e:
        print(str(e))
        print("'{}' No 'Price'".format(address))
        logfile.write("{}: '{}' No 'Price'...\n {} \n".format(hour, address, str(e)))

    try:
        div = sup.find("div",{"class": lambda x: x and 'intraday__close' in x})
        data["yclose"] = re.sub("[^0-9. -]", "", div.find('tbody').text)
    except Exception as e:
        print(str(e))
        print("'{}' No 'yClose'".format(address))
        logfile.write("{}: '{}' No 'yClose'...\n {} \n".format(hour, address, str(e)))

    try:
        data["open"] = scrapData["Open"].replace(" ","")
    except Exception as e:
        print(str(e))
        print("'{}' No 'Open'".format(address))
        logfile.write("{}: '{}' No 'Open'...\n {} \n".format(hour, address, str(e)))

    try:
        data["dayh"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["dayl"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except Exception as e:
        print(str(e))
        print("'{}' No 'DayRange'".format(address))
        logfile.write("{}: '{}' No 'DayRange'...\n {} \n".format(hour, address, str(e)))

    try:
        data["h52"] = scrapData["52WeekRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["l52"] = scrapData["52WeekRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except Exception as e:
        print(str(e))
        print("'{}' No '52WeekRange'".format(address))
        logfile.write("{}: '{}' No '52WeekRange'...\n {} \n".format(hour, address, str(e)))

    try:
        data["vol"] = str(mkTranslator(sup.find("span",{"class":"volume last-value"}).text))
    except Exception as e:
        if 'index' not in address:
            print("'{}' No 'Volume'".format(address))
            logfile.write("{}: '{}' No 'Volume'...\n {} \n".format(hour, address, str(e)))

    try:
        data["oi"] = scrapData["OpenInterest"].replace(" ","")
    except Exception as e:
        if 'index' not in address:
            print("'{}' No 'OpenInterest'".format(address))
            logfile.write("{}: '{}' No 'OpenInterest'...\n".format(hour, address))

    return data

def scrapBloomberg(address):
    #creating/formatting data from scrapdata
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    lab = sup.find_all("div",{"class": lambda x: x and 'cell__label' in x})
    val = sup.find_all("div",{"class": lambda x: x and 'value' in x})

    data = getDataFormat()

    if not len(lab) == len(val):
        toCull = len(lab) - len(val)
        if toCull > 0:
            for i in range(0,toCull):
                lab.pop()
        else:
            for i in range(0,toCull):
                val.pop()
        print("'{}' labels and values mismatch was fixed".format(address))
        logfile.write("{}: '{}' labels and values mismatch was fixed...\n".format(hour, address))
        # for i, item in enumerate(val):
        #     print("{}:  {}".format(i, item))
        # print('')
        # for i, item in enumerate(lab):
        #     print("{}:  {}".format(i, item))

    scrapData = {}
    #we create a dictionary of scraped data with labels as key and val as values
    for i, key in enumerate(lab):
        scrapData[key.text.replace(" ","")] = re.sub("[^0-9. -]", "", val[i].text)

    data["date"] = date
    data["time"] = hour
    data["day"] = day

    try:
        data["price"] = sup.find("div",{"class":"price"}).text.replace(",","").replace(" ","")
    except Exception as e:
        print(str(e))
        print("'{}' No 'Price'".format(address))
        logfile.write("{}: '{}' No 'Price'...\n {} \n".format(hour, address, str(e)))

    try:
        data["open"] = scrapData["Open"].replace(" ","")
    except Exception as e:
        print(str(e))
        print("'{}' No 'Open'".format(address))
        logfile.write("{}: '{}' No 'Open'...\n {} \n".format(hour, address, str(e)))

    try:
        data["yclose"] = scrapData["PreviousClose"].replace(" ","")
    except Exception as e:
        print(str(e))
        print("'{}' No 'yClose'".format(address))
        logfile.write("{}: '{}' No 'yClose'...\n {} \n".format(hour, address, str(e)))

    try:
        data["dayh"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["dayl"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except Exception as e:
        print(str(e))
        print("'{}' No 'DayRange'".format(address))
        logfile.write("{}: '{}' No 'DayRange'...\n {} \n".format(hour, address, str(e)))

    try:
        data["h52"] = scrapData["52WkRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["l52"] = scrapData["52WkRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except Exception as e:
        print(str(e))
        print("'{}' No '52WkRange'".format(address))
        logfile.write("{}: '{}' No '52WkRange'...\n {} \n".format(hour, address, str(e)))


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

def writeit(csvFile, db):
    global logfile
    logfile = open('logs/' + date + '_' + db.split('/')[-1] + '_log.txt', 'a+')

    conn = sqlite3.connect(db)
    c = conn.cursor()

    csvlist = open(csvFile, 'r')
    count = 0

    c.execute("""CREATE TABLE IF NOT EXISTS MARKETS(
        name text,
        date text,
        time text,
        timestamp integer,
        day text,
        price real,
        yclose real,
        open real,
        dayh real,
        dayl real,
        h52 real,
        l52 real,
        vol integer,
        oi integer)""")
    conn.commit()

    c.execute("""CREATE TABLE IF NOT EXISTS CME(
        name text,
        date text,
        time text,
        timestamp integer,
        day text,
        totalVol integer,
        totalOI integer,
        totalBT integer,
        Ticker_max text,
        price_max real,
        yclose_max real,
        open_max real,
        dayh_max real,
        dayl_max real,
        vol_max integer,
        oi_max integer,
        bt_max integer,
        tableFutures text)""")
    conn.commit()

    c.execute("""CREATE TABLE IF NOT EXISTS YELDS(
        name text,
        date text,
        time text,
        timestamp integer,
        day text,
        maturity text,
        yields text)""")
    conn.commit()

    c.execute("""CREATE TABLE IF NOT EXISTS CDS(
        name text,
        date text,
        time text,
        timestamp integer,
        day text,
        value integer,
        unit text)""")
    conn.commit()

    logfile.write("\n--------------------------\n")
    logfile.write("--------- Time: ----------\n")
    logfile.write("--------- {}   ----------\n".format(hour))
    logfile.write("--------- START ----------\n")
    logfile.write("--------------------------\n\n")

    for line in csvlist:
        if line.split(',')[0] != "": #avoids completely empty rows in spreadsheet
            fileName = line.split(',')[0]
            address = line.split(',')[1]
            addressFutures = line.split(',')[2].replace('\n','')

            try:
                print('\n:::::::::::')
                logfile.write('\n:::::::::::')
                print("Start to write DataBase for {}...".format(fileName))
                logfile.write("Start to write DataBase for {}...\n".format(fileName))

                if address != 'empty' and fileName.split('_')[1] in 'F S Y i':
                    this_dic = selector(address)

                    c.execute("""INSERT INTO MARKETS VALUES (
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
                        fileName,
                        this_dic['date'],
                        time.strftime('%H:%M'),
                        timestamp,
                        this_dic['day'],
                        this_dic['price'],
                        this_dic['yclose'],
                        this_dic['open'],
                        this_dic['dayh'],
                        this_dic['dayl'],
                        this_dic['h52'],
                        this_dic['l52'],
                        this_dic['vol'],
                        this_dic['oi']))
                    conn.commit()      # we take all the main/first adresses unless we have an .Fr file.

                if addressFutures != 'empty':
                    arr = selector(addressFutures)
                    dic_totals = arr[0]
                    max_Contract = arr[1]
                    table_futures = arr[2]

                    c.execute("""INSERT INTO CME VALUES (
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
                        fileName + '_cme',
                        date,
                        time.strftime('%H:%M'),
                        timestamp,
                        day,
                        dic_totals['totalVol'],
                        dic_totals['totalOI'],
                        dic_totals['totalBT'],
                        max_Contract[0],
                        max_Contract[1],
                        max_Contract[2],
                        max_Contract[3],
                        max_Contract[4],
                        max_Contract[5],
                        max_Contract[6],
                        max_Contract[7],
                        max_Contract[8],
                        str(table_futures)))
                    conn.commit()      # then if the cme address is not empty we scrap it

                if '_YC' in fileName:
                    arr = selector(address)
                    maturity = arr[0]
                    yields = arr[1]

                    c.execute("""INSERT INTO YELDS VALUES (
                    ?,?,?,?,?,?,?)""", (
                        fileName,
                        date,
                        time.strftime('%H:%M'),
                        timestamp,
                        day,
                        str(maturity),
                        str(yields)))
                    conn.commit()

                if '_d' in fileName:

                    arr = selector(address)

                    for dictCDS in arr:
                        regex = re.compile('[^a-zA-Z ]')
                        name = regex.sub('', dictCDS['Name'])
                        tablename = 'CDS_' + name.replace(' ','_')

                        c.execute("""INSERT INTO CDS VALUES
                        (?,?,?,?,?,?,?)""",(
                            tablename,
                            date,
                            time.strftime('%H:%M'),
                            timestamp,
                            day,
                            dictCDS['Value'],
                            dictCDS['Unit']))
                        conn.commit()

                print("End writing DataBase for {}.".format(fileName))
                logfile.write("End writing DataBase for {}\n.".format(fileName))
                print('///////////')
                logfile.write('///////////\n')

                count += 1

            except Exception as e:
                print(str(e))
                print("Writing DataBase for {} did not work because of: {}".format(fileName, e))
                print("X X X X X X")
                logfile.write('{}: Writing DataBase for {} did not work...\n{} \n'.format(hour, fileName, str(e)))
                logfile.write("X X X X X X\n")

    logfile.write("\n--------------------------\n")
    logfile.write("---------  END  ----------\n")
    logfile.write("--------------------------\n\n")

    c.close()
    conn.close()

    csvlist.close

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("file_csv", help = "file where to read all the instruments to scrap from")
    # parser.add_argument("db", help = "main database")
    # args = parser.parse_args()
    #
    # writeit(args.file_csv, args.db)
    scrapBloomberg('https://www.bloomberg.com/quote/SX5E:IND')

try:
    logfile.close()
except:
    pass
