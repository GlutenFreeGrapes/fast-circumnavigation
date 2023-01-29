import pandas as pd,datetime,pytz,time,heapq,airportsdata
from geographiclib.geodesic import Geodesic

ding=time.perf_counter()
dc={'IAD','DCA','BWI'}
geod=Geodesic.WGS84
aptdata=airportsdata.load('IATA')
starttime=pytz.timezone('America/New_York').localize(datetime.datetime(2023,2,1,8,0,0))
cutoff=pytz.timezone('America/New_York').localize(datetime.datetime(2023,2,3,9,30,0))
maxlayover=datetime.timedelta(hours=2)
flights=pd.read_csv('better_all_flights_dropped.csv')
longitudes={i:aptdata[i]['lon'] for i in set(flights['departure'])}
coords={i:(aptdata[i]['lat'],longitudes[i]) for i in longitudes}
londisttodc=dict()
for i in longitudes:
    b=set()
    for j in dc:
        raw=longitudes[j]-longitudes[i]
        if raw<0:
            # if abs(raw)<15:
            #     b.add(abs(raw))
            # else:
                b.add(raw+360)
        else:
            b.add(raw)
    londisttodc[i]=min(b)
with open('mindists.txt','w')as f:
    f.write(str(londisttodc))

flights=flights[['departure','dep time','arrival','arr time','flight number','distance']]
flights['dep time']=pd.to_datetime(flights['dep time'])
flights['arr time']=pd.to_datetime(flights['arr time'])
# flights[['dep time','arr time']]=flights[['dep time','arr time']].apply(pd.to_datetime)
flights=flights[flights['arr time']<=cutoff]
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
fringe=[(-500,0,0,0,100,datetime.timedelta(seconds=0).seconds,i,i,'',starttime) for i in dc]
sols=[]
def get_children(airport,dateandtime):
    airportflights=airporttoflights[airport]
    avail=airportflights[airportflights['dep time']>=dateandtime]
    children=set()
    for dest in set(avail['arrival']):
        nextavailflight=avail[avail['arrival']==dest].iloc[0]
        # get flight number, airport, distance, arrival time
        if (nextavailflight['dep time']-dateandtime)<=maxlayover:
            children.add((nextavailflight['arr time'],nextavailflight['distance'],nextavailflight['arrival'],nextavailflight['flight number']))
    return children
with open('possible solutions.txt','w')as f:
    f.write('LIST OF SOLUTIONS\n-----------------')
pcount=0
solct=0
while len(fringe)>0 and solct<5000:
    (ew,dcdist,numflights,curdist,efficiency,timediff,airport,aptpath,flightstaken,curtime)=heapq.heappop(fringe)
    # print((numflights,'east' if ew==-1 else 'west',-efficiency,timediff,curdist,airport,aptpath,flightstaken,curtime))
    # input()
    pcount+=1
    if pcount%500==0:
        print(-ew,dcdist,numflights,curdist,efficiency,timediff,airport,aptpath,flightstaken,curtime)
    if airport in dc and (-curdist)>36900:
        # sols.append((curtime,curdist,aptpath,flightstaken))
        solct+=1
        with open('possible solutions.txt','a') as f:
            f.write('\n'+', '.join([str(i) for i in (curtime,curdist,aptpath,flightstaken,timediff,efficiency)]))
    else:
        for newtime,dist,newairport,flightnum in get_children(airport,curtime):
            if numflights<10:
                ntdiff=newtime-starttime
                ndist=curdist-dist
                heapq.heappush(fringe,(-eastwestbound[(airport,newairport)],londisttodc[newairport],numflights+1,ndist,-ntdiff.seconds/ndist,ntdiff,newairport,aptpath+' - '+newairport,flightstaken+' - '+flightnum,newtime))
print(time.perf_counter()-bing)
    
