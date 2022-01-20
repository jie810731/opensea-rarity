import os.path
import json
from random import triangular
import requests
import numpy_indexed as npi
from collections import Counter
from itertools import groupby
import unittest
import copy

def getCollectionTotalCount(assets_response):
    return assets_response['assets'][0]['token_id']

def getAssets(contract ,offset = 0):
    url = 'https://api.opensea.io/api/v1/assets?limit=50&asset_contract_address={}&offset={}&format=json'.format(contract.strip(),offset)
    print('get assets, url={}'.format(url))
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

def getAssetsRarityScore(traits,total,trait_object,trait_type_count):
    duplicate_trait_object = copy.deepcopy(trait_object)
    score = 0
    for trait in traits:
        value = 1 / round((trait['trait_count']/int(total)),2)
        score += value

        duplicate_trait_object.pop(trait['trait_type'])

    for key,count in duplicate_trait_object.items():
        value = 1 / round(((total-count)/int(total)),2)
        score += value
    
    trait_len = len(traits)
    counts_of_this_trait = trait_type_count[trait_len]
    value = 1 / round((counts_of_this_trait/int(total)),2)

    score += value

    return score

def getListenCollection():
    file_name ='listen/listen_collection.txt'
    is_need_get_data = True

    while is_need_get_data :
        if os.path.exists(file_name):
            with open(file_name) as f:
                data = f.read()
            data = json.loads(data)
            is_need_get_data = False
            
    return data

def getAssetsWithScore(collection_slug):
    try:
        url = 'https://api.opensea.io/api/v1/collection/{}'.format(collection_slug)
        header = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        }   
        res = requests.get(url=url, headers=header)
        data = res.json()
    except Exception as ex:
        print('error')
        print(ex)

        return 
    
    traits_count  = get_trait_count(data['collection']['traits'])
    if len(traits_count) == 0:
        return  
    contract_address = data['collection']['primary_asset_contracts'][0]['address']
    data = getAssets(contract_address)
    result =[]
    assets = data['assets']

    is_get_data = True
    while is_get_data:
        data = getAssets(contract_address,len(assets))
        if not data['assets']:
            is_get_data = False
        assets = assets + data['assets']

    total = len(assets)

    for index,asset in enumerate(assets):
        traits = asset['traits']
        asset['trait_count'] = len(traits)

    assets.sort(key=lambda assets: assets['trait_count'])
    trait_type_count = {}

    for key, groups in groupby(assets, lambda asset : asset['trait_count']):
        trait_type_count[key] = len(list(groups))

    for index,asset in enumerate(assets):
        score = getAssetsRarityScore(traits,total,traits_count,trait_type_count)
        formate = {
            'token_id': asset['token_id'],
            'score':score
        }
        
        result.append(formate)

    return result

def writeFile(file_path,content):
    f = open("{}.txt".format(file_path),"w")
    f.write(json.dumps(content))

def get_trait_count(input):
    traits_count  = {}
    for index,trait in input.items():
        count = 0
        for value,each_count in trait.items():
            count += each_count

        traits_count[index] = count
    
    return traits_count

class TestStringMethods(unittest.TestCase):
    def test_get_trait_count(self):
        input  =  {
            "Skin": {
                "8": 1,
                "9": 3,
                "top secret": 1
            },
            "Top Secret": {
                "top secret": 1
            }
        }
        expect = {
            'Skin':5,
            'Top Secret':1
        }
        
        result = get_trait_count(input)
        self.assertEqual(result,expect)
    
    def test_get_assets_rarity_score(self):
        total = 5
        trait = [
                {
                    "trait_type": "CLOTHES",
                    "value": "Top Secret",
                    "display_type": 'null',
                    "max_value": 'null',
                    "trait_count": 2,
                    "order": 'null'
                },
                {
                    "trait_type": "mouth",
                    "value": "Top Secret",
                    "display_type": 'null',
                    "max_value": 'null',
                    "trait_count": 3,
                    "order": 'null'
                }
        ]
        trait_object = {
            'CLOTHES': 3,
            'mouth': 2,
            'else': 3
        }

        expect =  1/(2/total) + 1/(3/total) + 1/((total-3)/total)
        result = getAssetsRarityScore(trait,5,trait_object)

        self.assertEqual(result,expect)

if __name__ == '__main__':
    # unittest.main()
    listen_collections = getListenCollection()
    print('list_collection_slug = :{}'.format(listen_collections))
    for listen_collection in listen_collections:
        assets_score = getAssetsWithScore(listen_collection)
        sortd = sorted(assets_score, key = lambda s: s['score'],reverse=True)
        writeFile('contract/{}'.format(listen_collection),sortd)