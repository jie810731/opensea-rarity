from os import walk
import glob
import json
import requests
import math
import urllib.parse
import threading
import time
import pause
import datetime

def getWatchItems(file_path):
    with open(file_path) as f:
        data = f.read()
    data = json.loads(data)
    
    return data

def getAsset(contract ,token_id):
    url = 'https://api.opensea.io/api/v1/asset/{}/{}'.format(contract,token_id)
    print(url)
    header = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    }
    try:
        res = requests.get(url=url, headers=header)
        data = res.json()

    except Exception as ex:
        print('error')
        print(ex)
        pass

    return data

def getListOrder(contract,token_id):
    list_order = []
    asset = getAsset(contract,token_id)
    
    owner_name = asset['top_ownerships'][0]['owner']['address']
    orders = asset['orders']

    for order in orders:
        maker = order['maker']['address']
        if maker == owner_name:
            bace_price = int(order['base_price']) / math.pow(10,18)
            list_order.append(bace_price)
    
    return  list_order

def listenJob(filename):
    record_object = getWatchItems(filename)
    items = record_object['item']

    slug = filename.replace(".txt", "")
    slug = slug.replace("price/", "")

    try:
        url = 'https://api.opensea.io/api/v1/collection/{}'.format(slug)
        header = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        }   
        res = requests.get(url=url, headers=header)
        data = res.json()
    except Exception as ex:
        print('error')
        print(ex)
    
    contract_address = data['collection']['primary_asset_contracts'][0]['address']

    for key,item in items.items():
        order_lists = getListOrder(contract_address,key)

        if order_lists:
            print('has order list')
            order_lists.sort()

            price = order_lists[0]
            if price < record_object[item['rank']]['average_price']:
                try:
                    body = {
                        "chat_id" : -790427094,
                        "text" : "[{}](https://opensea.io/assets/{}/{})\nRank :{}\nAveragePrice = {}\nHighestPrice = {}\nLowestPrice = {}\nCurrentPrice = {}".format(slug,contract_address,key,item['rank'],record_object[item['rank']]['average_price'],record_object[item['rank']]['height_price'],record_object[item['rank']]['low_price'],price),
                        "parse_mode" : "markdown"
                    }

                    url = 'https://api.telegram.org/bot5277878862:AAGh-AfBwn35qBomaV0OoH3B9bxDvWwYnDs/sendMessage'
                    header = { 
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
                    }   
                    res = requests.get(url=url, headers=header,data=json.dumps(body))
                    data = res.json()
                except Exception as ex:
                    print('error')
                    print(ex)
            else:
                print('too expensive')
        else:
            print('no order list')

def job(test):
    print('index{}'.format(test))
    for i in range(5):
        print("Child thread:", i)
        time.sleep(1)

if __name__ == '__main__':
    while True:
        filenames = glob.glob("price/*.txt")

        if not filenames:
            print('no file go to sleep for a minute')
            time.sleep(60)

            continue

        threads = []
        for index,filename in enumerate(filenames):
            threads.append(threading.Thread(target = listenJob,args = (filename,)))
            threads[index].start()

        for thread in threads:
            thread.join()

        now = datetime.datetime.now()
        until_time = now + datetime.timedelta(minutes=10)
        pause.until(until_time)
