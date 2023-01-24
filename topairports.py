import requests,pandas as pd
from bs4 import BeautifulSoup
data=pd.DataFrame()
for i in range(78):
    response=requests.get(f"https://www.aviationfanatic.com/ent_list.php?ent=7&pg={i+1}&NN_AP_Passengers=1&so=22")
    temp=BeautifulSoup(response.text,'html.parser')
    for j in temp.find_all('tr',{'class':'sumrow'}):
        j.decompose()
    p=pd.read_html(str(temp))[0]
    p=p.drop(index=list(p.index)[-1])
    data=pd.concat([data,p])
    print(i+1)
print(data)
data.to_csv('topairports.csv',index=0)