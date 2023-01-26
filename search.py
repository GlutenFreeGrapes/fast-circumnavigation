import pandas as pd,datetime,pytz,heapq
dc={'IAD','DCA','BWI'}
starttime=pytz.timezone('America/New_York').localize(datetime.datetime(2023,2,1,8,0,0))
cutoff=pytz.timezone('America/New_York').localize(datetime.datetime(2023,2,3,10,0,0))
flights=pd.read_csv('all_flights.csv')
flights['dep time']=pd.to_datetime(flights['dep time'])
flights['arr time']=pd.to_datetime(flights['arr time'])
flights=flights[flights['arr time']<=cutoff]
flights=flights.sort_values('dep time',ascending=1)
flights.to_csv('flights_sorted.csv',index=0)
airporttoflights={i:flights[flights['departure']==i] for i in set(flights['departure'])}
airportdept = {i:set(airporttoflights[i]['arrival']) for i in airporttoflights}
with open('alldepartures.txt','w')as f:
    f.write(str(airportdept))
fringe=[(0,starttime-starttime,i,i,'',starttime) for i in dc]
sols=[]
def get_children(airport,dateandtime):
    airportflights=airporttoflights[airport]
    avail=airportflights[airportflights['dep']>=dateandtime]
    for dest in set(avail['arrival']):
        avail[avail['arrival']==dest].head(1)
while len(fringe)>0:
    (curdist,timediff,airport,apts,flightstaken,curtime)=fringe.pop()
    if airport in dc and curdist>36500:
        sols.append((curtime,curdist,apts,flightstaken))
    
    
