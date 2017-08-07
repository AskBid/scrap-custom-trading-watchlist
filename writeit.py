import time
import sys
import scrapit


f = open('macrowatchlist.csv', 'r')


for line in f:
    if line.split(',')[0] != "":
        fileName = line.split(',')[0]
        address = line.split(',')[1]
        addressFutures = line.split(',')[2]

        thisFile = open('data/' + fileName + '.csv', 'a+')
        print(fileName)
        print(address)
        print(scrapit.scrapit(address))
        try:
            thisFile.write(scrapit.scrapit(address))
            thisFile.write('\n')
            thisFile.close()
        except:
            print('file write not working')


f.close
