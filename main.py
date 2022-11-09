from flask import Flask, render_template, request
import base64
from os import system
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as optimize
import redis
from os import remove
from flask import jsonify
from flask_cors import CORS,cross_origin


redisConnection = redis.StrictRedis(host='redis-13659.c299.asia-northeast1-1.gce.cloud.redislabs.com', port=13659, db=0, password="yaF2eb60hDdCGRrq2dG8TE0h5KO5UPMn", socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', unix_socket_path=None)

app = Flask(__name__)
PORT = 5000
DEBUG = False

@app.after_request
def after_request(response):
    response.access_control_allow_origin = "*"
    return response


@app.route('/optimize')
@cross_origin()
def optimize():


    count = redisConnection.get('count')
    count = int(count)


    nameId = 1
    if id:
        nameId = count + 1
    else:
        nameId = 1

    redisConnection.set('count',str(nameId))    
    funtion = request.args.get('funtion').replace(" ", "+")
    print(funtion)
    CODE = """
import redis
import matplotlib.pyplot as plt
import scipy.optimize as optimize
import base64
from os import remove
import requests
import json

nameStrId = """+str(nameId)+"""
redisConnect = redis.StrictRedis(host='redis-13659.c299.asia-northeast1-1.gce.cloud.redislabs.com', port=13659, db=0, password="yaF2eb60hDdCGRrq2dG8TE0h5KO5UPMn", socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', unix_socket_path=None)



def fun(x):
    return ("""+str(funtion)+""")

x = range(-30, 30)
plt.plot(x, [fun(i) for i in x])
plt.axhline(0, color="black")
plt.axvline(0, color="black")
plt.xlim(-30, 30)
plt.ylim(-30, 30)
min = optimize.minimize(fun, 2 , method = 'TNC', tol=1e-6 )
plt.plot(min.x[0],min.fun,marker ="o")

imageName = "tempImage"+str(nameStrId)+".jpg"
plt.savefig(imageName)

image = open(imageName,'rb')
image_read = image.read()
base64_bytes  = base64.encodebytes(image_read)
base64_string = base64_bytes .decode("ascii")

url = f"https://analysis-project.lulosys.com/public/storageImage"

payload = json.dumps({
    "image": base64_string,
    "idName": 1
    })
    


headers = {
'Content-Type': 'application/json',
'Cookie': 'XSRF-TOKEN=eyJpdiI6Ijg2c2ptZnQ0UC9vTFMzeWZtOXBmMlE9PSIsInZhbHVlIjoibVExYXBHSS82MmpINlRacWRRTlJkeW95K0NnK3pFR0FxcFkzM0ZDZmJOeUFCaDN3MzhDczkydTRmcHBoNHVDRVliSGJSc0tnZzBvWW5GUkliYk83bFNUWUJWQkJJRkcvS282RXRpZGtXZVpoRDN5a05YU1poemd3cUhqLzNjQWciLCJtYWMiOiIwNzZjNWZmYzlhYWY5NjlhNjg4MGU0ZTM0N2EyMjA3MTMxOTYyMmMwMzgzODE1OWIxNWMxMDdhZTlmNzYyOTFkIiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6ImtOUGxDbllmZ3crc01oTnZpZ1FTQXc9PSIsInZhbHVlIjoiMGl6TDhEVVBBRk9WNGFDM0pTdEtzRXhZUm9sZUpnanF4NmZlb3VheUFCS2VyTXNkZS9ESUovQnBHOTJrOHJzekszNitab0w3cGczdTUrbThvaERVbktUNXRrSmJKQ3k5ZEYwbzlycEJOOVpBK1VVN0J4Ny90ZFdHRDNxM2NENW4iLCJtYWMiOiJmODFjZDhiZTNlODNhYjVmMDM2OWFjMTQ0ZDIyZDIyMTQ2Y2IzYmRlM2YxZGYwNGEyNjM5MGNkODFkZGMzOWNlIiwidGFnIjoiIn0%3D'
}

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text)
redisConnect.set("tempImageJpg"+str(nameStrId),response.text )
redisConnect.set("tempImage"+str(nameStrId),base64_bytes )
redisConnect.set("resut"+str(nameStrId), json.dumps({"min":min.x[0]}) )
"""

    nameFile = "temp"+str(nameId)+".py"
    with open(nameFile,"w") as file:
        file.write(CODE)
        
    system("python "+nameFile)

    remove(nameFile)

    resp = redisConnection.get("resut"+str(nameId))
        
    return {"puntos":str(resp),"idName":str(nameId)}


@app.route('/')
def index():
    # os.system("shutdown /s /t 1") 
    print("Siii funciona")
    return 'Hola Mundo!'

@app.route('/imageByIdName')
def imageJPG():

    idName = request.args.get('idName')
    resp = redisConnection.get("tempImage"+str(idName))
    return resp

@app.route('/imageByIdNameJpg')
def image():

    idName = request.args.get('idName')
    image = redisConnection.get("tempImageJpg"+str(idName))

    return image


if __name__ == '__main__':
    app.run(port = PORT, debug=DEBUG)


