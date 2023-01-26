import requests,pandas as pd,string
from bs4 import BeautifulSoup
data=pd.DataFrame()
for i in string.ascii_uppercase:
    response=requests.get(f"https://airlinecodes.info/iata/{i}")
    temp=BeautifulSoup(response.text,'html.parser')
    p=pd.read_html(str(temp))[0]
    p=p.drop(index=list(p.index)[-1])
    data=pd.concat([data,p])
    print(i)
print(data)
data.to_csv('icaoiataairline.csv',index=0)