import time
import requests
from bs4 import BeautifulSoup as bs
##### start/divert all prints to a log file
import sys
old_stdout = sys.stdout

log_file = open("message.log","w")

sys.stdout = log_file
##### start\divert all prints to a log file


#data shared format between Marketwatch and Bloomberg
dataFormatGlobal = {
    "Ticker": "",
    "FullName": "",
    "Date": "",
    "Price": "",
    "Open": "",
    "DayH": "",
    "DayL": "",
    "52H": "",
    "52L": "",
    "Volume": "",
    "OpenInterest": ""}

dataFormatGlobalCDS = {
    'Name': '',
    'Value': '',
    'Unit': '',
    'bptChange': ''}

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

    sovereignCDS = []

    for row in rows:
        dictRow = dataFormatGlobalCDS

        name = row.find("td",{"class": lambda x: x and 'Nome' in x})
        name = name.text.replace(' ','').replace('\n','').replace('\t','')

        value = row.find("td",{"class": lambda x: x and 'Rendimento' in x})
        value = value.text.replace(' ','').replace('\n','').replace('\t','')

        dictRow['Name'] = name
        dictRow['Value'] = value
        dictRow['Unit'] = 'Spread'
        dictRow['bptChange'] = ''

        sovereignCDS.append(dictRow)

    return sovereignCDS  #ritorna una lista di dizionari 'dataFormatGlobalCDS'

def scrapWsj(address):
    #CDS indexes and big movers for bonds and corporate
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    iframes = sup.find_all("iframe")

    # finds the address where the real table is kept, the real content of iframe
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

    #take values for all of the tables  ### crucial if website change
    try:
        names = soup.findAll("td",{"class": lambda x: x and 'col1' in x})
        values = soup.findAll("td",{"class": lambda x: x and 'col2' in x})
        unit = soup.findAll("td",{"class": lambda x: x and 'col3' in x})
        bptChange = soup.findAll("td",{"class": lambda x: x and 'col5' in x})
    except:
        print("table CDS column gathering did not work")

    dictCDS = []
    dictCDSbondsBM = []   #BM as in Big Movers
    dictCDSstockBM = []

    for i in range(0,12):
        if 'n.a.' not in values[i].text:
            dictRow = dataFormatGlobalCDS

            dictRow['Name'] = names[i].text
            dictRow['Value'] = values[i].text
            dictRow['Unit'] = unit[i].text
            dictRow['bptChange'] = ''

            dictCDS.append(dictRow)

    #tigheners/wideners bonds (last 20 rows we take first ten)
    for i in range(-20,-10):
        dictRow = dataFormatGlobalCDS

        dictRow['Name'] = names[i].text
        dictRow['Value'] = values[i].text
        dictRow['Unit'] = 'Spread'
        dictRow['bptChange'] = bptChange[i].text

        dictCDSbondsBM.append(dictRow)

    #tigheners/wideners bonds (last 20 rows we take first ten)
    for i in range(-10,0):
        dictRow = dataFormatGlobalCDS

        dictRow['Name'] = names[i].text
        dictRow['Value'] = values[i].text
        dictRow['Unit'] = 'Spread'
        dictRow['bptChange'] = bptChange[i].text

        dictCDSstockBM.append(dictRow)

    return dictCDS, dictCDSbondsBM, dictCDSstockBM  #ritorna tre liste di dizionari 'dataFormatGlobalCDS'

def scrapWgb(address):
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

        data = {"Ticker": "",
                "last": "",
                "priorSettle": "",
                "open": "",
                "high": "",
                "low": "",
                "volume": "",
                "openInterest": "",
                "blockTrades": ""}

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
                label = cell.get('id').split("_")[2] ###taking all teb labels: quotesFuturesProductTable1_6EQ7_open
            except:
                print("'{}' No 'label' CME '_' split did not work".format(address))

            for key in data:
                if key == label: ## if one of the label from the dictonary matches any of the labe just gathrrd, then add value to that key
                    try:
                        stringValue = cell.text.replace("-","").replace(",","")
                        if stringValue != "":
                            float(stringValue)
                    except:
                        print("'{}' No 'float' CME".format(address))

                    data[key] = stringValue

        table.append(data)

    #// from here down Volume page to get Total and OpenInterest

    r = requests.get(address.replace('.html','_quotes_volume_voi.html'))    ### crucial if website change
    c = r.content
    sup = bs(c,"html.parser")

    tableSup = sup.find("tbody")
    rows = tableSup.find_all("tr")

    totalOpenInterest = ''
    totalVolume = ''
    totalBlockTrades = ''

    colNumOpenInterest = 10     ### crucial if website change
    colNumVolume = 3     ### crucial if website change
    colNumBlockTrades = 4     ### crucial if website change

    if rows[-1].find('th').text == 'Totals':   ##last row of the table
        cells = rows[-1].find_all('td')
        totalOpenInterest = cells[colNumOpenInterest].text.replace(',','')
        totalVolume = cells[colNumVolume].text.replace(',','')
        totalBlockTrades = cells[colNumBlockTrades].text.replace(',','')
    else:
        print("'{}' No 'Totals' CME tag was found".format(address))
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

    return totalValues, table  #ritorna un piccolo dizionario ed una lista di dizionari (un dizionari for every expiry)

def scrapMarketwatch(address):
    #creating formatting data from scrapdata
    r = requests.get(address)
    c = r.content
    sup = bs(c,"html.parser")

    lab = sup.find_all("small",{"class": 'kv__label'})
    val = sup.find_all("span",{"class": 'kv__value kv__primary '})

    data = dataFormatGlobal

    if not len(lab) == len(val):
        print("'{}' labels and values mismatch".format(address))
        return data

    scrapData = {}

    for i, key in enumerate(lab):
        scrapData[key.text.replace(" ","")] = val[i].text.replace(",","").replace("%","").replace("$","").replace("£","").replace("€","")
    print(scrapData)

    data["Date"] = time.strftime("%Y/%m/%d %H:%M %a")

    try:
        data["Ticker"] = sup.find("span",{"class": "company__ticker"}).text.replace(' ','')
    except:
        print("'{}' No 'Ticker'".format(address))

    try:
        data["FullName"] = sup.find("span",{"class":"company__market"}).text.replace(' ','')
    except:
        print("'{}' No 'FullName'".format(address))

    try:
        data["Price"] = sup.find("span",{"class":"value"}).text.replace(",","").replace(" ","")
        int_try = float(data["Price"]) #check that an actual number was found for Price
    except:
        print("'{}' No 'Price'".format(address))

    try:
        data["Open"] = scrapData["Open"].replace(" ","")
    except:
        print("'{}' No 'Open'".format(address))

    try:
        data["DayH"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["DayL"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        print("'{}' No 'DayRange'".format(address))

    try:
        data["52H"] = scrapData["52WeekRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["52L"] = scrapData["52WeekRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        print("'{}' No '52WeekRange'".format(address))

    try:
        data["Volume"] = str(mkTranslator(sup.find("span",{"class":"volume last-value"}).text))
    except:
        print("'{}' No 'Volume'".format(address))

    try:
        data["OpenInterest"] = scrapData["OpenInterest"].replace(" ","")
    except:
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
        print("'{}' labels and values mismatch".format(address))
        return data

    scrapData = {}
    #we create a dictionary of scraped data with labels as key and val as values
    for i, key in enumerate(lab):
        scrapData[key.text.replace(" ","")] = val[i].text.replace(",","").replace("%","").replace("$","").replace("£","").replace("€","")

    data["Date"] = time.strftime("%Y/%m/%d %H:%M %a")

    try:
        data["Ticker"] = sup.find("div",{"class": "ticker"}).text.replace(' ','')
    except:
        print('{}' "No 'Ticker'".format(address))

    try:
        data["FullName"] = sup.find("h1",{"class":"name"}).text.replace(' ','')
    except:
        print("'{}' No 'FullName'".format(address))

    try:
        data["Price"] = sup.find("div",{"class":"price"}).text.replace(",","").replace(" ","")
    except:
        print("'{}' No 'Price'".format(address))

    try:
        data["Open"] = scrapData["Open"].replace(" ","")
    except:
        print("'{}' No 'Open'".format(address))

    try:
        data["DayH"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["DayL"] = scrapData["DayRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        print("'{}' No 'DayRange'".format(address))

    try:
        data["52H"] = scrapData["52WkRange"].replace(" - ",";;").replace(" ","").split(";;")[1]
        data["52L"] = scrapData["52WkRange"].replace(" - ",";;").replace(" ","").split(";;")[0]
    except:
        print("'{}' No '52WkRange'".format(address))

    try:
        data["Volume"] = scrapData["Volume"].replace(" ","")
    except:
        print("'{}' No 'Volume'".format(address))

    ''' in Bloomberg non ce mai Oi
    try:
        data["OpenInterest"] = scrapData["OpenInterest"].replace(" ","")
    except:
        data["datacheck"] = data["datacheck"].replace("I","-")
        print("No 'OpenInterest' for '{}'".format(address))
    '''

    return data;

##
#\ scraping functions
##

##### end/divert all prints to a log file
sys.stdout = old_stdout

log_file.close()
##### end\divert all prints to a log file
t = scrapCmegroup('http://www.cmegroup.com/trading/metals/base/copper.html')[1]
for ti in t:
    print(ti)
