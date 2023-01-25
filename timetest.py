import pytz,datetime
a=pytz.timezone('US/Eastern').localize(datetime.datetime(2023,2,1,9,0,0))
b=pytz.timezone('US/Central').localize(datetime.datetime(2023,2,1,8,1,0))
c=pytz.timezone('UTC').localize(datetime.datetime(2023,2,1,10,0,0))
d=pytz.timezone('US/Central').localize(datetime.datetime(2023,2,1,8,0,0))

print(a,b,c,d)
print(a<b)
print(b-a)
print(c<a)
print(d==a)
print(sorted([a,b,c,d]))
