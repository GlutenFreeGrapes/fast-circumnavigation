import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import airportsdata,time

# airportsdata.Airport()

coptions=Options()
coptions.add_argument('--headless')
coptions.add_argument('--no-sandbox')
coptions.add_argument('--disable-dev-shm-usage')
coptions.add_argument("--window-size=1366,768")
wd = uc.Chrome(service=Service(ChromeDriverManager().install()), options=coptions)
dcairports={'IAD','DCA','BWI'}
airports=['IAD','CHS','LBL']

for airport in airports:
	for i in range(1,4):
		print(i)
		wd.get(f"https://www.flightsfrom.com/{airport}/departures?dateMethod=day&dateFrom=2023-02-0{i}&dateTo=2023-02-0{i}")
		moreflightsbutton=wd.find_element(By.CSS_SELECTOR,'button[class*="md-raised blue-md-button md-primary md-button md-ink-ripple"]')
		while wd.find_element(By.CSS_SELECTOR,'div[ng-hide*="departures_offset == 0"]').get_attribute('aria-hidden')!='true':		
			print('clicking')
			moreflightsbutton.click()
			time.sleep(1)

	print(airport)


