import os
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, Request
import requests
from fastapi.responses import RedirectResponse
from kiteconnect import KiteConnect
import hashlib
import wizLights as wizLights

load_dotenv()
app = FastAPI()
kite = KiteConnect(api_key=os.environ['Z_API_KEY']) #represents single user that's authenticated

@app.get("/")
def welcome():
    return 'Welcome to SmartWM.'

@app.get("/login")
def login():
    return RedirectResponse(kite.login_url()+os.getenv('Z_API_KEY'))

@app.api_route("/callback/", methods=["GET", "POST"])
def callback(request:Request):
    request = request.query_params.get('request_token')
    getAccessToken(request)
    return RedirectResponse("/")

@app.get("/holdings")
def fetchHoldings():
    return kite.holdings()

@app.get("/pnl")
def getPnl():
    holdings = fetchHoldings()
    return findNetPnl(holdings)

@app.get("/lights")
def lights():
    pnl = getPnl()
    if pnl < 0:
        wizLights.changeLights('RED')
    else:
        wizLights.changeLights('GREEN')
    return "LIGHTS ON!"

@app.get("/lights/reset")
def lightsRelax():
    wizLights.changeLights('RELAX')


@app.api_route("/logout", methods=["GET", "DELETE"])
def invalidateAccessToken():
    wizLights.changeLights('OFF')
    kite.invalidate_access_token()
    return {"message": "Logout successful"}

def getAccessToken(request_token):
    # After getting request_token from redirect
    api_key = os.getenv('Z_API_KEY')
    api_secret = os.getenv('Z_API_SECRET')

    #fetch access token with request token, api key and api secret
    # checksum = hashlib.sha256((api_key + request_token + api_secret).encode()).hexdigest()
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    kite.set_access_token(access_token)

    #update env variables
    updateEnvVariable('REQUEST_TOKEN', request_token)
    updateEnvVariable('ACCESS_TOKEN', access_token)

def updateEnvVariable(variable, value):
    # Update the .env file
    with open("../.env", "r") as f:
        lines = f.readlines()

    with open("../.env", "w") as f:
        for line in lines:
            if line.startswith(variable):
                f.write(f"{variable}={value}\n")
            else:
                f.write(line)

def findNetPnl(holdings):
    netPnl = 0
    for h in holdings:
        netPnl += h['pnl']
    return netPnl

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)