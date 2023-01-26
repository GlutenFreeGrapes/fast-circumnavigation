import pandas as pd
bingbong=pd.read_csv('flights_better.csv')
print(len(set(bingbong['flight number'])))
print(len(bingbong.index))
for i in set(bingbong['flight number']):
    if len(bingbong[bingbong['flight number']==i])>1:
        print(i)