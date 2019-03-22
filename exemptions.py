import csv
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

class TaxPortal():

	def prep(self):
		columns = ['Address', 'Pin', 'Exemptions']
		opt = Options()
		opt.add_argument("--headless")
		driver = webdriver.Chrome(options=opt)
		return driver

	# check if property has <0 exemptions
	def exempt_check(self, driver):
		info = driver.find_elements_by_class_name("js-open-modal2")
		for element in info:
			if 'Exemptions' in element.text:
				if element.text[0] is '0':
					return False
				else:
					return True

	# gather exemption info
	def gather_from_page(self, driver):
		pin = driver.find_element_by_id("ContentPlaceHolder1_lblResultTitle").text
		info = driver.find_elements_by_class_name("js-open-modal2")
		for element in info:
			if 'Exemptions' in element.text:
				exemptions = element.text[:11]
				break

		return pin, exemptions

	# write out exemption lat, long, pin, address lines to excel
	def write_out(self, out_list):
		with open('exemptions.csv', 'w', newline='') as csvout:
			fields = ['Address', 'Exemptions', 'Pin', 'Longitude', 'Latitude']
			writer = csv.DictWriter(csvout, fieldnames = fields)
			writer.writeheader()
			for row in out_list:
				writer.writerow(row)
		return None

	def run(self, excel, url, driver):
		leads = []

		# open execl data
		with open(excel, newline='\n') as f:
			census_data = csv.DictReader(f)
			driver.get(url)

			start = time.time()
			for i, row in enumerate(census_data):
				out_row = {}
				addr_input = driver.find_element_by_id("houseNumber").send_keys(row['NUMBER']) #NUMBER
				street_input = driver.find_element_by_id("txtStreetName").send_keys(row['STREET']) #STREET
				city_input = driver.find_element_by_id("txtCity").send_keys("Chicago") #CHICAGO
				driver.find_element_by_id("ContentPlaceHolder1_PINAddressSearch_btnSearch").click() #submit

				# print for benchmarking purposes
				if i%50 == 0 and i > 0:
					now = time.time()
					print("Completed:",i,"in ",(now-start)/60)

				# do a partial run
				if i == 500:
					break

				time.sleep(0.1)

				# if address has exemptions, goto page
				try:
					listing = driver.find_element_by_id("ContentPlaceHolder1_AddressResults_rptAddressResults_lnkAddressPIN_0")
					listing.click()
				except NoSuchElementException:
					print("not found",row['NUMBER'],row['STREET'])
					driver.get(url)
					continue

				# at a property page
				# parse page for exemptions and pin if exemptions present
				# otherwise next

				###### change this to try, except and compare speed #######
				if self.exempt_check(driver):
					pin, exemptions = self.gather_from_page(driver)
				
					out_row['Address'] = row['NUMBER'] + ' ' + row['STREET']
					out_row['Pin'] = pin
					out_row['Exemptions'] = exemptions
					out_row['Latitude'] = row['LAT']
					out_row['Longitude'] = row['LON']
 
					leads.append(out_row)

				# get search page and go next row
				driver.get(url)

		return leads
	

if __name__ == "__main__":
	excel ="C:\\Users\\User\\Downloads\\openaddr-collected-us_midwest\\us\\il\\city_of_chicago.csv"
	url = "http://www.cookcountypropertyinfo.com/default.aspx"
	seeker = TaxPortal()
	driver = seeker.prep()
	leads = seeker.run(excel, url, driver)
	seeker.write_out(leads)