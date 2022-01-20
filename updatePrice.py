from os import walk
import glob
import json
import requests
import math
import time
import pause
import datetime
import threading

def getAssetItems(file_path):
    with open(file_path) as f:
        data = f.read()
    data = json.loads(data)

    return data

def getAsset(contract ,token_id):
    url = 'https://api.opensea.io/api/v1/asset/{}/{}?format=json'.format(contract,token_id)
    header = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    }
    print(url)
    try:
        res = requests.get(url=url, headers=header)
        data = res.json()

    except Exception as ex:
        print('error')
        print(ex)
        
        return

    return data

def getLastPrice(contract,token_id):
    asset = getAsset(contract,token_id)
    try:
        last_price = asset['last_sale']['total_price']
        unit_symbol = asset['last_sale']['payment_token']['symbol']
        unit_decimals = asset['last_sale']['payment_token']['decimals']
        last_price = float(last_price) / math.pow(10,unit_decimals)
        us_price = asset['last_sale']['payment_token']['usd_price']
    except Exception as ex:
        return None

    return {
        'price':last_price,
        'symbol':unit_symbol,
        'us_price':us_price
    }

def storeRarity(filename):
    items = getAssetItems(filename)
    total_count = len(items)

    result = {
        'A':{
            'top_index':0,
            'down_index':1 / 100 * total_count,
            'height_price':None,
            'low_price':None,
            'average_price':0,
            'total_price':0,
            'total_count':0
        },
        'B':{
            'top_index':1 / 100 * total_count,
            'down_index':3 / 100 * total_count,
            'height_price':None,
            'low_price':None,
            'average_price':0,
            'total_price':0,
            'total_count':0
        },
        'C':{
            'top_index':3 / 100 * total_count,
            'down_index':5 / 100 * total_count,
            'height_price':None,
            'low_price':None,
            'average_price':0,
            'total_price':0,
            'total_count':0
        },
        'D':{
            'top_index':5 / 100 * total_count,
            'down_index':10 / 100 * total_count,
            'height_price':None,
            'low_price':None,
            'average_price':0,
            'total_price':0,
            'total_count':0
        },
    }
    store_item = {}
    slug = filename.replace(".txt", "")
    slug = slug.replace("contract/", "")

    try:
        url = 'https://api.opensea.io/api/v1/collection/{}'.format(slug)
        print(url)
        header = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        }   
        res = requests.get(url=url, headers=header)
        data = res.json()
    except Exception as ex:
        print('error')
        print(ex)

        return 
    
    contract_address = data['collection']['primary_asset_contracts'][0]['address']
    
    for index,item in enumerate(items):
        if index > result['D']['down_index']:
            break
        last_price = getLastPrice(contract_address,item['token_id'])
        store_item[item['token_id']] = {
            'rarity':index/len(items)
        }
      
        for key in result:
            if index >= result[key]['top_index'] and index <= result[key]['down_index']:
                store_item[item['token_id']]['rank'] = key
        
        if last_price == None:
            continue

        store_item[item['token_id']]['price'] = last_price['price']

        for key in result:
            if index >= result[key]['top_index'] and index <= result[key]['down_index']:
                if result[key]['height_price'] == None:
                    result[key]['height_price'] = last_price['price']

                if result[key]['low_price'] == None:
                    result[key]['low_price'] = last_price['price']

                if last_price['price'] > result[key]['height_price']:
                    result[key]['height_price'] = last_price['price']

                if last_price['price'] < result[key]['low_price']:
                    result[key]['low_price'] = last_price['price']
                
                result[key]['total_price'] += last_price['price']
                result[key]['total_count'] += 1

    for key in result:
        if result[key]['total_count'] == 0:
            break
        result[key]['average_price'] =  result[key]['total_price']/result[key]['total_count']

    result['item'] = store_item
    
    f = open("price/{}.txt".format(slug),"w")
    f.write(json.dumps(result))
    f.close()

if __name__ == '__main__':
    while True:
        filenames = glob.glob("contract/*.txt")
        if not filenames:
            print('no file go to sleep for a minute')
            time.sleep(60)
            
            continue
        
        threads = []
        for index,filename in enumerate(filenames):
            threads.append(threading.Thread(target = storeRarity,args = (filename,)))
            threads[index].start()
        
        for thread in threads:
            thread.join()

        print('end updatePrice')

        now = datetime.datetime.now()
        until_time = now + datetime.timedelta(minutes=10)
        pause.until(until_time)