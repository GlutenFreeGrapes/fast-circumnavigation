import pandas as pd,datetime,pytz,time,heapq,airportsdata

ding=time.perf_counter()
dc={'IAD','DCA','BWI'}
aptdata=airportsdata.load('IATA')
starttime=pytz.timezone('America/New_York').localize(datetime.datetime(2023,2,1,8,0,0))
cutoff=pytz.timezone('America/New_York').localize(datetime.datetime(2023,2,3,10,0,0))
threehours=datetime.timedelta(hours=3)
flights=pd.read_csv('all_flights.csv')
longitudes={i:aptdata[i]['lon'] for i in set(flights['departure'])}
flights=flights[['departure','dep time','arrival','arr time','flight number','distance']]
flights['dep time']=pd.to_datetime(flights['dep time'])
flights['arr time']=pd.to_datetime(flights['arr time'])
# flights[['dep time','arr time']]=flights[['dep time','arr time']].apply(pd.to_datetime)
flights=flights[flights['arr time']<=cutoff]
flights=flights.sort_values('dep time',ascending=1)
flights.to_csv('flights_sorted.csv',index=0)
airporttoflights={i:flights[flights['departure']==i] for i in set(flights['departure'])}
airportdepartures={i:set(airporttoflights[i]['arrival']) for i in airporttoflights}
eastwestbound={}
for i in airportdepartures:
    for j in airportdepartures[i]:
        longdist=longitudes[j]-longitudes[i]
        if longdist<=-180 or 0<=longdist<=180:
            eastwestbound[(i,j)]=1#east
        else:
            eastwestbound[(i,j)]=-1
# with open('east or west.txt','w')as f:
#     f.write(str(eastwestbound))

print('running')
bing=time.perf_counter()
print(bing-ding)
fringe=[(0,0,-100,datetime.timedelta(seconds=0).seconds,0,i,i,'',starttime) for i in dc]
sols=[]
def get_children(airport,dateandtime):
    airportflights=airporttoflights[airport]
    avail=airportflights[airportflights['dep time']>=dateandtime]
    children=set()
    for dest in set(avail['arrival']):
        nextavailflight=avail[avail['arrival']==dest].iloc[0]
        # get flight number, airport, distance, arrival time
        if (nextavailflight['dep time']-dateandtime)<=threehours:
            children.add((nextavailflight['arr time'],nextavailflight['distance'],nextavailflight['arrival'],nextavailflight['flight number']))
    return children


while len(fringe)>0:
    (numflights,ew,efficiency,timediff,curdist,airport,aptpath,flightstaken,curtime)=heapq.heappop(fringe)
    # print((numflights,'east' if ew==-1 else 'west',-efficiency,timediff,curdist,airport,aptpath,flightstaken,curtime))
    # input()
    if airport in dc and (-curdist)>36500:
        sols.append((curtime,curdist,aptpath,flightstaken))
        with open('possible solutions.txt','w') as f:
            f.write('\n'.join([str(i) for i in sols]))
    else:
        for newtime,dist,newairport,flightnum in get_children(airport,curtime):
            if numflights<8:
                ntdiff=newtime-starttime
                ndist=curdist-dist
                heapq.heappush(fringe,(numflights+1,-eastwestbound[(airport,newairport)],ntdiff.seconds/ndist,ntdiff,ndist,newairport,aptpath+' - '+newairport,flightstaken+' - '+flightnum,newtime))
print(time.perf_counter()-bing)
    
