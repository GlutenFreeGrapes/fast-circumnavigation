import pandas as pd
top=pd.read_csv('flights_better_better.csv')
bottom=pd.read_csv('flights_better_bettertwo.csv')
full=pd.concat([top,bottom])
full['dep time']=pd.to_datetime(full['dep time'])
full['arr time']=pd.to_datetime(full['arr time'])
full=full.drop_duplicates().sort_values('dep time',ascending=1)
full.to_csv('better_all_flights.csv',index=False)
full=full[full['distance']!='drop']
full.to_csv('better_all_flights_dropped.csv',index=False)
