# --------------------------------------------- Imports ---------------------------------------------
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import requests
import os

from time import sleep
from pandas import DataFrame
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()












# --------------------------------------------- Set Up ---------------------------------------------
# Browser Options
options = Options()
# options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36")
options.add_argument("--window-size=1920,1200")
# options.add_experimental_option("detach", True)

# Start up brodser and go to website
driver = webdriver.Chrome(options=options)
driver.get('https://stockanalysis.com/stocks/screener/')

wait = WebDriverWait(driver, 20)











# --------------------------------------------- Helper Functions ---------------------------------------------

# Clicks
def click(selector):
    try:
        (wait.until(EC.presence_of_element_located(selector))).click()
    except TimeoutException:
        print("Timeout")

def clickSelector(selector):
    click((By.CSS_SELECTOR, selector))

def clickXPath(selector):
    click((By.XPATH, selector))












# --------------------------------------------- Process Functions ---------------------------------------------

# Filtering By analyst ratings
def filter():
    clickSelector('#main > div.rounded.border.bg-gray-50.p-2.dark\:border-dark-600.dark\:bg-dark-775 > div.mt-3.flex.flex-col.gap-y-2\.5.sm\:flex-row.lg\:gap-y-2.pb-1 > button')
    clickSelector('#analystRatings')
    clickSelector("#main > div.rounded.border.bg-gray-50.p-2.dark\:border-dark-600.dark\:bg-dark-775 > div.mt-3.flex.flex-col.gap-y-2\.5.sm\:flex-row.lg\:gap-y-2.border-b.border-default.pb-3.dark\:border-sharp > div.fixed.left-0.top-0.z-\[99\].flex.h-screen.w-screen.items-center.justify-center.bg-gray-500\/50 > div > button")
    clickSelector("#main > div.rounded.border.bg-gray-50.p-2.dark\:border-dark-600.dark\:bg-dark-775 > div.sm\:grid.sm\:grid-cols-2.sm\:gap-x-2\.5.lg\:grid-cols-3 > div > div.flex.items-center > div > button")
    clickSelector("#Strong\ Buy")
    clickSelector("#main > div.relative.mt-4 > div.mt-5.grid-cols-2.items-center.border-gray-300.dark\:border-dark-700.sm\:mt-6.sm\:grid.sm\:border-t.lg\:flex.lg\:space-x-1.lg\:overflow-visible.lg\:py-2.lg\:px-1 > div.hide-scroll.col-span-2.overflow-x-auto.border-t.border-default.lg\:order-2.lg\:grow.lg\:border-0.lg\:pl-1.xl\:pl-3 > nav > ul > li:nth-child(4) > button")
    clickSelector("#analystCount")

# Add extra columns into table
def addColumns():
    columnsList = "/html/body/div/div[1]/div[2]/main/div[3]/div[1]/div[1]/div[3]/"

    clickXPath(columnsList + "button")
    for i in range(30 - 18):
        clickXPath(columnsList + f"div/div[1]/div[{18 + i}]/input")

# Adding more rows
def addRows():
    clickSelector("#main > div.relative.mt-4 > nav > div > div > button")
    clickSelector("#main > div.relative.mt-4 > nav > div > div > div > button:nth-child(2)")

# Get Stock Screener Table Info
def screenerTable(rowsData):
    rows = rowsData.copy()
    valid = False
    count = 0
    headers = [ header.text for header in driver.find_elements(By.TAG_NAME, "th") ]

    while not valid and count < 2:
        valid = False
        count += 1

        for row in driver.find_elements(By.TAG_NAME, "tr")[1:]:
            rowData = []

            for cell in row.find_elements(By.TAG_NAME, "td"):
                cellValue = cell.text
                rowData.append(cellValue)

                if cellValue == "-":
                    valid = False

            rows[rowData[0]] = dict(zip(headers, rowData))
        
        print("Missing data found. Retrying...")

    return rows

# Get Forecast Table
def forecastTable(stockData):
    stocks = stockData.copy()
    tableSelector = "#main > div:nth-child(3) > div.space-y-8 > div.rounded-sm.border.border-gray-200.p-3.dark\:divide-dark-700.dark\:border-dark-700.lg\:flex.lg\:space-x-4.lg\:divide-x > div.grow.lg\:pl-4 > div.mt-3.overflow-x-auto.text-center.lg\:mt-5 > table"
    
    for stock in stocks:
        header = []
        data = []
        forecastData = {
            "Strong Buy": 0,
            "Buy": 0,
            "Hold": 0,
            "Sell": 0,
            "Strong Sell": 0,

        }

        try:
            driver.get(f'https://stockanalysis.com/stocks/{stock}/forecast/')

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, tableSelector)))
            sleep(1.5)

            table = driver.find_element(By.CSS_SELECTOR, tableSelector).text.split("\n")[1:]

            for row in table:
                cells = row.split(" ")
                num = 0

                header.append(" ".join(cells[:-6]))

                if cells[-1] != "n/a":
                    num = float(cells[-1])
                else:
                    num = 0

                data.append(num)

            forecastData = dict(zip(header, data))

        except NoSuchElementException:
            print("forecast not found")
            
        except TimeoutException:
            print("Website unreachable")

        stocks[stock]["Forecast"] = forecastData

    return stocks

# Sort Stocks by ratings
def sortStocks(stockData):
    # Calculating Stock Analysis Score
    for stock in stockData.values():
        forecast = stock["Forecast"]
        stock["Rating Score"] = 0
        
        for rating in forecast:
            multiplier = 0

            match rating:
                case "Strong Buy":
                    multiplier = 2
                case "Buy":
                    multiplier = 1
                case "Hold":
                    multiplier = -1
                case "Sell":
                    multiplier = -2
                case "Strong Sell":
                    multiplier = -3

            stock["Rating Score"] += forecast[rating] * multiplier
    
    # Sorting Stocks by Rating Score
    stockData = dict(sorted(stockData.items(), key=lambda item: item[1]["Rating Score"], reverse=True))
    return stockData

def saveToExcel(stockData):
    data = {}

    # Extracting Data
    for stock in stockData.values():
        for header, value in stock.items():

            # Creating Headers
            if header not in data or header == "Forecast":

                if header != "Forecast":
                    data[header] = []

                else:

                    for forecastHeader in stock["Forecast"]:
                        if forecastHeader not in data:
                            data[forecastHeader] = []

            # Extracting Data
            if header != "Forecast":
                data[header].append(value)

            else:

                for forecastHeader in stock["Forecast"]:
                    data[forecastHeader].append(value[forecastHeader])

    df = DataFrame(data)
    df.to_excel('D:\Goh Hong Rui\Tests\Web Scraping\\test.xlsx', sheet_name='sheet1', index=False)

    return df

def uploadToPythonAnywhere(df):
    # Initialising varirables
    TOKEN = os.getenv('PYTHONANYWHERE_TOKEN')
    USER = os.getenv('USER')

    ENDPOINT = 'https://www.pythonanywhere.com/api/v0/user/{USER}'
    FILESAPI = f'/files/path'
    FILEPATH = f'/home/{USER}/Web-Scraping'
    FILENAME = '/test.xlsx'

    RELOADAPI = f"/webapps/{USER}.pythonanywhere.com/reload/"

    # Convert excel to bytes to store in pythonanywhere
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    res = requests.post(ENDPOINT + FILESAPI + FILEPATH + FILENAME,
        files={ 'content': buffer },
        headers={ 'Authorization': 'Token ' + TOKEN }
    )

    print(res)

    # Reload web app to reflect changes
    requests.post(ENDPOINT + RELOADAPI, headers={ 'Authorization': 'Token ' + TOKEN })











# --------------------------------------------- Run ---------------------------------------------

print("--------------------------------------------- Start ---------------------------------------------")

print("--------------------------------------------- Setting Filters ---------------------------------------------")
filter()

print("--------------------------------------------- Filters Set, Adding Columns ---------------------------------------------")
addColumns()

print("--------------------------------------------- Columns Added, Adding Rows ---------------------------------------------")
addRows()

print("--------------------------------------------- Rows Added, Getting Stock Screener Table Data ---------------------------------------------")
stocks = screenerTable({})

# Next Page
print("--------------------------------------------- Next Page ---------------------------------------------")
clickSelector("#main > div.relative.mt-4 > nav > button.controls-btn.xs\:pl-1.xs\:pr-1\.5.bp\:text-sm.sm\:pl-3.sm\:pr-1")

stocks = screenerTable(stocks)

print("--------------------------------------------- Stock Screener Table Data Retrieved, Getting Forecast ---------------------------------------------")
forecasts = forecastTable(stocks)

print("--------------------------------------------- Stock Forcast Data Retrieved, Closing Browser and Sorting Stocks ---------------------------------------------")
# Close Browser
driver.quit()

# Sort Stocks By Rating
sortedForecasts = sortStocks(forecasts)

print("--------------------------------------------- Stocks Sorted, Saving to Excel ---------------------------------------------")
excelDF = saveToExcel(sortedForecasts)

print("--------------------------------------------- Saved to Excel, Uploading to PythonAnywhere ---------------------------------------------")
uploadToPythonAnywhere(excelDF)

print("=================================================================== Web Scraping Complete ===================================================================")