import requests
import os
import pandas as pd

from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

def uploadToPythonAnywhere(df):
    # Initialising varirables
    TOKEN = os.getenv('PYTHONANYWHERE_TOKEN')
    USER = os.getenv('USER')

    ENDPOINT = f'https://www.pythonanywhere.com/api/v0/user/{USER}'
    FILESAPI = '/files/path'
    FILEPATH = f'/home/{USER}/Web-Scraping'
    FILENAME = '/test.xlsx'

    RELOADAPI = f"/webapps/{USER}.pythonanywhere.com/reload/"

    HEADERS = { 'Authorization': 'Token ' + TOKEN }

    # Convert excel to bytes to store in pythonanywhere
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    res = requests.post(ENDPOINT + FILESAPI + FILEPATH + FILENAME,
        files={ 'content': buffer },
        headers=HEADERS
    )
    
    reqMsg = res.content.decode('utf-8')
    print("Upload Response: " + reqMsg)

    # Reload web app to reflect changes
    res = requests.post(ENDPOINT + RELOADAPI, headers=HEADERS)
    
    reqMsg = res.content.decode('utf-8')
    print("Reload Response: " + reqMsg)

uploadToPythonAnywhere(pd.read_excel('test.xlsx'))