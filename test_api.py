import requests
import json
import sys
import time
import logging
from utilitis.randomNum import Random
from datetime import date
today = date.today()


URL = "http://10.1.1.10:8080//FPP//rest//rest//fpp//"

headers = {'Content-Type':'application/json',
           'Accept':'*/*'}

logging.basicConfig(filename= 'C:\\Users\\haim\\PycharmProjects\\Devpos\\API\\TestApi\\Logs\\' + f'testApi{today}.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logger = logging.getLogger()
sys.stderr.write = logger.error
sys.stdout.write = logger.info

bankId = Random.get_bank()
accountId = Random.get_acount()


with open('login.json','r') as f:
    login_json = json.load(f)
    login_json['clientDetails']['bankId']=bankId
    login_json['clientDetails']['accountId']=accountId

with open('new_login.json','w') as f:
    json.dump(login_json,f,indent=2)

def test_login():
    response_login = requests.post(URL + "login",json=login_json,headers=headers)
    response_json =json.loads(response_login.text)
    assert response_login.status_code == 200
    sessionId = response_json['sessionId']
    assert len(sessionId) > 0
    return sessionId

with open('create_rfq.json','r') as f:
    rfq_json = json.load(f)
    rfq_json['sessionId'] = test_login()

def test_rfq():
    response_createRFQ = requests.post(URL + "create-quote", json=rfq_json, headers=headers)
    assert response_createRFQ.status_code == 200
    json_createRFQ = json.loads(response_createRFQ.text)
    rfqID = json_createRFQ['rfqId']
    assert len(rfqID) > 0

    return rfqID

def test_get_rfq():
    getRFQ = test_rfq()
    response_getRFQ = requests.post(URL + "get-quote", data=getRFQ, headers=headers)
    json_getRFQ = json.loads(response_getRFQ.text)

    while json_getRFQ['status']['code'] == 'FPP_RFQ_STILL_PENDING' or json_getRFQ['status']['code'] == 'FPP_RFQ_QUOTE_PARTIAL':
        response_getRFQ = requests.post(URL + "get-quote", data=getRFQ, headers=headers)
        json_getRFQ = json.loads(response_getRFQ.text)
        print(json_getRFQ['status']['code'])
        if json_getRFQ['status']['code'] == 'FPP_RFQ_QUOTE_FINAL' or json_getRFQ['status']['code'] == 'FPP_RFQ_QUOTE_ENHANCEMENT':
            print(json.dumps(json_getRFQ, indent=2))
            print(json_getRFQ["quoteProperties"])
        time.sleep(20)
    quoteProperties = json_getRFQ["quoteProperties"]
    quoteId = quoteProperties['id']
    assert len(quoteId) > 0
    return quoteId

def test_order():
    Order = {
        "accountTypeName": "751",
        "defPath": 100,
        "quote": {
            "advicedDeposit": True,
            "nominalAmount": 0,
            "quoteID": test_get_rfq()
        },
        "sessionId": test_login()
    }

    response_createOrder = requests.post(URL + "quotes//create-order", json=Order, headers=headers)
    json_createOrder = json.loads(response_createOrder.text)
    orderId = json_createOrder['orderId']
    assert len(orderId) > 0
    return orderId

def test_get_order():
    getOrder = test_order()

    response_getOrder = requests.post(URL + "quotes//get-order", data=getOrder, headers=headers)
    json_getOrder = json.loads(response_getOrder.text)

    while json_getOrder['status']['code'] == 'FPP_ORDER_STILL_PENDING':
        response_getOrder = requests.post(URL + "quotes/get-order", data=getOrder, headers=headers)
        json_getOrder = json.loads(response_getOrder.text)
        print(json_getOrder['status']['code'])
        time.sleep(20)
    assert response_getOrder == "OK"
    print(json_getOrder['status']['details'])


test_get_order()