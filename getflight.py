import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import airportsdata,time,pandas as pd,re,geographiclib,timezonefinder

top300=list(pd.read_csv('topairports.csv').head(300)['IATA code'])
allflightstop300=pd.DataFrame()
ainfo=airportsdata.load('IATA')
airporttocoords={i:(ainfo[i]['lat'],ainfo[i]['lon'] )for i in allflightstop300}

coptions=Options()
coptions.add_argument('--headless')
coptions.add_argument('--no-sandbox')
coptions.add_argument('--disable-dev-shm-usage')
wd = uc.Chrome(service=Service(ChromeDriverManager().install()), options=coptions)
wd.maximize_window()


dcairports={'IAD','DCA','BWI'}
exp=re.compile('openTimeTableIata.*')
bing=time.perf_counter()
print('running')
for airport in top300:
	for i in range(1,4):
		aday={'arrival':[],'dep time':[],'arr time':[],'flight number':[]}
		clickcount=0
		wd.get(f"https://www.flightsfrom.com/{airport}/departures?dateMethod=day&dateFrom=2023-02-0{i}&dateTo=2023-02-0{i}")
		# with open('html.txt','w',encoding='utf-8') as f:
		# 	f.write(wd.page_source)
		moreflightsbutton=wd.find_element(By.CSS_SELECTOR,'button[class*="md-raised blue-md-button md-primary md-button md-ink-ripple"]')
		thing=wd.find_element(By.CSS_SELECTOR,'div[ng-hide*="departures_offset == 0"]')
		while not (thing.get_attribute('aria-hidden')=='true' or thing.get_attribute('class')=='ng-hide'):
			clickcount+=1		
			# print('clicking')
			# moreflightsbutton.submit()
			# actions.move_to_element(moreflightsbutton).perform()
			# moreflightsbutton.click()
			# time.sleep(5)

			# WebDriverWait(wd, 4).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'button[class*="md-raised blue-md-button md-primary md-button md-ink-ripple"]'))).click()
			moreflightsbutton.click()
			WebDriverWait(wd, 5).until(EC.invisibility_of_element_located((By.CLASS_NAME,'pageload-background')))

			

			# WebDriverWait(wd, 5).until(EC.element_to_be_clickable(wd.find_element(By.CSS_SELECTOR,'button[class*="md-raised blue-md-button md-primary md-button md-ink-ripple"]'))).click()
			# WebDriverWait(wd, 20).until(EC.element_to_be_clickable(moreflightsbutton))
		soupy=BeautifulSoup(wd.page_source,'html.parser')
		for j in soupy.find_all('div',{'class':"airport-departure-list-item departures-25"}):
			for k in j.find_all('span',{'class':'airport-hide-mobile'}):
				k.decompose()
			if j.find('div',{'class':"airport-departure-list-logo"})!=None:
				j.decompose()
		flightsies=soupy.find_all('li',{'ng-click':exp})
		print(len(flightsies))
		aday['departure']=[airport for j in range(len(flightsies))]
		for j in flightsies:
			aday['arrival'].append(j.find('div',{'class':"airport-departure-list-item departures-25"}).text.strip())
			aday['dep time'].append(j.find('div',{'class':"airport-departure-list-item departures-5 airport-font-midheader"}).text.strip())
			aday['flight number'].append(j.find('div',{'class':"airport-departure-list-item departures-15 airport-font-midheader"}).text.strip())

		adayframe=pd.DataFrame(aday)
		allflightstop300=pd.concat(allflightstop300,adayframe)
		print(i,clickcount)
	print(airport)
print(time.perf_counter()-bing,'seconds')

