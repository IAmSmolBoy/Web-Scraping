from flask import Flask, render_template
import pandas as pd
from numpy import reshape

# Get Stock Data
df = pd.read_excel("test.xlsx")

# Start Web Server
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    stocksData = df.to_dict()
    headers = list(stocksData.keys())

    data = []
    firstColumn = list(stocksData.values())[0]

    for i in range(len(list(firstColumn.values()))):
        stock = {}

        for header in headers:
            stock[header] = stocksData[header][i]
        
        data.append(stock)

    return render_template("index.html", headers=headers, stocks=data)