import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from geographiclib.geodesic import Geodesic
import airportsdata,time,pandas as pd,re,timezonefinder,datetime,pytz

dropping=['SXF','TXL','NAY'] #removing berlin schonfeld, berlin tegel, beijing nanyuan
top300=pd.read_csv('topairports.csv')
top300=top300[~top300['IATA code'].isin(dropping)]['IATA code']
top300=list(top300.head(300))
set300=set(top300)
print(len(set300))
# print(top300)
allflightstop300=pd.DataFrame()
ainfo=airportsdata.load('IATA')
airporttocoords={i:(ainfo[i]['lat'],ainfo[i]['lon'] ) for i in top300}
tzfd=timezonefinder.TimezoneFinder()
airporttz={i:pytz.timezone(tzfd.timezone_at(lat=airporttocoords[i][0],lng=airporttocoords[i][1])) for i in airporttocoords}
doneflightdata=pd.read_csv('flights.csv')
doneflightdata['dep time']=pd.to_datetime(doneflightdata['dep time'])
doneflightdata=doneflightdata[~(doneflightdata['distance']=='drop')]
doneflightdata.to_csv('all_flights.csv',index=0)
print('generated')
coptions=Options()
coptions.add_argument('--headless')
coptions.add_argument('--no-sandbox')
coptions.add_argument('--disable-dev-shm-usage')
wd = uc.Chrome(service=Service(ChromeDriverManager().install()), options=coptions)
wd.maximize_window()

flightndatetotimedelta={}
dcairports={'IAD','DCA','BWI'}
exp=re.compile('airport-content-destination-listitem.*')
bing=time.perf_counter()
print('running')
for airport in top300:
	for i in range(1,4):
		aday={'departure':[],'arrival':[],'dep time':[],'flight number':[],'distance':[]}
		# clickcount=0
		wd.get(f"https://www.flightsfrom.com/{airport}/destinations?dateMethod=day&dateFrom=2023-02-0{i}&dateTo=2023-02-0{i}")
		soupy=BeautifulSoup(wd.page_source,'html.parser')
		for j in soupy.find_all('li',{'class':exp}):
			dest=j['data-iata']
			for l in j.find_all('div',{'class':'airport-content-destination-list-time'}):
				for k in l.find_all('span',{'class':'airport-font-smallheader'}):
					k.decompose()
			nums=l.text.strip().replace('m','').replace('h','').split()
			flightndatetotimedelta[(airport,dest,datetime.date.fromisoformat(f'2023-02-0{i}'))]=datetime.timedelta(hours=int(nums[0]),minutes=int(nums[1]))
		print(i)
	print(airport)
	with open('flighttimes.txt','w') as f:
		f.write(str(flightndatetotimedelta))
def addarrtime(row):
	arr=row['arrival']
	deptime=row['dep time']
	arrtime=deptime+flightndatetotimedelta[(row['departure'],arr,deptime.date())]
	if arr in set300:
		return arrtime.astimezone(airporttz[arr])
	else:
		return arrtime
doneflightdata['arr time']=doneflightdata.apply(lambda row: addarrtime(row), axis=1)
doneflightdata.to_csv('all_flights.csv',index=0)
print(time.perf_counter()-bing,'seconds')

