import scrapit as sc

s = sc.scrapBloomberg('https://www.bloomberg.com/quote/CO1:COM')

for i in s:
    print(s[i])
