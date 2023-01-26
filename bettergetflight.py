import cloudscraper
from bs4 import BeautifulSoup
from geographiclib.geodesic import Geodesic
import airportsdata,time,pandas as pd,re,timezonefinder,datetime,pytz,json,sys


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
with open('locations.txt','w')as f:
	f.write(str(airporttocoords))
tzfd=timezonefinder.TimezoneFinder()
geod = Geodesic.WGS84
alldists={(i,j):(geod.Inverse(airporttocoords[i][0],airporttocoords[i][1],airporttocoords[j][0],airporttocoords[j][1])['s12']/1000) for i in top300 for j in top300}
with open('distances km.txt','w')as f:
	f.write(str(alldists))
airporttz={i:pytz.timezone(tzfd.timezone_at(lat=airporttocoords[i][0],lng=airporttocoords[i][1])) for i in airporttocoords}
with open('timezones.txt','w')as f:
	f.write(str(airporttz))
scraper = cloudscraper.create_scraper()

counter=0
dcairports={'IAD','DCA','BWI'}
tests=['ATL']
exp=re.compile('openTimeTableIata.*')
bing=time.perf_counter()
print('running')
for airport in top300:
	counter+=1
	print(counter,airport,end=' ')
	sys.stdout.flush()
	for i in range(1,4):
		
		aday={'departure':[],'arrival':[],'dep time':[],'arr time':[],'flight number':[],'distance':[]}
			# clickcount=0
		for hour in range(0,96):
			
			

			# moreflightsbutton=wd.find_element(By.CSS_SELECTOR,'button[class*="md-raised blue-md-button md-primary md-button md-ink-ripple"]')
			# thing=wd.find_element(By.CSS_SELECTOR,'div[ng-hide*="departures_offset == 0"]')
			# while not (thing.get_attribute('aria-hidden')=='true' or thing.get_attribute('class')=='ng-hide'):
			# 	moreflightsbutton.click()
			# 	WebDriverWait(wd, 5).until(EC.invisibility_of_element_located((By.CLASS_NAME,'pageload-background')))
			# with open('html.txt','w',encoding='utf-8') as f:
			# 	f.write(wd.page_source)
			html=scraper.get(f"https://www.flightsfrom.com/{airport}/departures?timeFrom={hour*15}&timeTo={((hour+1)*15)}&dateMethod=day&dateFrom=2023-02-0{i}&dateTo=2023-02-0{i}").text
			html=html[html.find('window.shedule'):html.find('window.activetab')].strip()
			html=html[html.find('{'):html.find(';')]
			flightsies=json.loads(html)['result']
			
			for j in flightsies:
				dest=j['iata_to']
				aday['departure'].append(airport)
				aday['arrival'].append(dest)
				deptime=airporttz[airport].localize(datetime.datetime.fromisoformat(f"2023-02-0{i} {j['departure_time']}"))
				aday['dep time'].append(deptime)

				if dest in set300:
					aday['arr time'].append(airporttz[dest].localize(datetime.datetime.fromisoformat(f"2023-02-0{i} {j['arrival_time']}")))
				else:
					aday['arr time'].append(deptime+datetime.timedelta(minutes=int(j['elapsed_time'])))
				aday['flight number'].append(j['carrier']+' '+j['flightnumber'])
				if dest in set300:
					aday['distance'].append(alldists[(airport,dest)])
				else:
					aday['distance'].append('drop')
		# for ii in aday:
		# 	print(ii,len(aday[ii]))
		adayframe=pd.DataFrame(aday)
		adayframe=adayframe.drop_duplicates(adayframe)
		allflightstop300=pd.concat([allflightstop300,adayframe])
		allflightstop300.to_csv('flights_better.csv',index=False)
		print(i,len(adayframe.index),end=' ')
		sys.stdout.flush()
	print()
print(time.perf_counter()-bing,'seconds')

