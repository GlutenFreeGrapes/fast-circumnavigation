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
for airport in top300[218:]:
	counter+=1
	print(counter,airport,end=' ')
	sys.stdout.flush()
	for i in range(1,4):
		
		aday={'departure':[],'arrival':[],'dep time':[],'arr time':[],'flight number':[],'distance':[]}
		
		entriesgotten=0
		currenttime=0
		timestring='00:00'
		html=scraper.get(f"https://www.flightsfrom.com/{airport}/departures?dateMethod=day&dateFrom=2023-02-0{i}&dateTo=2023-02-0{i}").text
		html=html[html.find('window.shedule'):html.find('window.activetab')].strip()
		html=html[html.find('{'):html.find(';')]
		whole=json.loads(html)
		for date in whole['dates']:
			if date['date']==f"2023-02-0{i}":
				totalentries=int(date['count'])
		
		while entriesgotten!=totalentries:
			url=f"https://www.flightsfrom.com/{airport}/departures?timeFrom={currenttime}&timeTo=1440&dateMethod=day&dateFrom=2023-02-0{i}&dateTo=2023-02-0{i}"
			if currenttime==0:
				url=f"https://www.flightsfrom.com/{airport}/departures?dateMethod=day&dateFrom=2023-02-0{i}&dateTo=2023-02-0{i}"
			html=scraper.get(url).text
			html=html[html.find('window.shedule'):html.find('window.activetab')].strip()
			html=html[html.find('{'):html.find(';')]
			whole=json.loads(html)
			res=whole['result']
			
			# json.dump(res,open('temp.json','w'),indent=4)
			# print(url)
			# input()
			alltimes=sorted({j["departure_time"] for j in res})
			last=len(alltimes)-1
			removetimes={alltimes[last],timestring}
			if last>1:
				flightsies=[j for j in res if (j['departure_time'] not in removetimes)]
				timestring=alltimes[last-1]
				nextlast=timestring.split(':')
			else:
				# peepee=pd.read_csv('all_flights.csv')
				# peepee=peepee[(peepee['departure']=='KWI') & peepee['dep time'].str.startswith('2023-02-02')]
				# bbbbb={k[:2]+' '+k[2:] for k in peepee['flight number']}
				# print(bbbbb-set(adayframe['flight number']))
				flightsies=[j for j in res if j['departure_time']!=timestring]
				timestring=alltimes[last]
				nextlast=timestring.split(':')
			# print(entriesgotten,totalentries,currenttime)
			# print(alltimes,len(res))
			entriesgotten+=len(flightsies)
			# print(alltimes,last,currenttime,entriesgotten,totalentries)
			currenttime=(60*int(nextlast[0]))+int(nextlast[1])

			for j in flightsies:
				dest=j['iata_to']
				aday['departure'].append(airport)
				aday['arrival'].append(dest)
				deptime=airporttz[airport].localize(datetime.datetime.fromisoformat(f"2023-02-0{i} {j['departure_time']}"))
				aday['dep time'].append(deptime)
				arrtime=deptime+datetime.timedelta(minutes=int(j['elapsed_time']))
				if dest in set300:
					aday['arr time'].append(arrtime.astimezone(airporttz[dest]))
				else:
					aday['arr time'].append(arrtime)
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
		allflightstop300.to_csv('flights_better_bettertwo.csv',index=False)
		print(i,len(adayframe.index),end=' ')
		sys.stdout.flush()
	print()
print(time.perf_counter()-bing,'seconds')
# allflightstop300=allflightstop300[allflightstop300['distance']!='drop']
# allflightstop300.to_csv('flights_better_better_dropped.csv',index=False)

