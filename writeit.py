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
        returned = scrapit.scrapit(address)
        print(returned)

        try:
            thisFile.write(returned)
            thisFile.write('\n')
            thisFile.close()
        except:
            print('file write not working for {}'.format(fileName))

        print('\n')

f.close
