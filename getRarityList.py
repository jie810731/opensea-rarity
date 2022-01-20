import requests
import json
import pause
import datetime

def getListResponse():
    try:
        url = 'https://graph.compass.art/graphql'
        body = {
            "operationName": "GetTrendingCollections",
            "variables": {
                "period": "1h",
                "sortBy": "salesCount",
                
                "take": 20,
                "skip": 0
            },
            "query": "query GetTrendingCollections($period: String, $sortBy: String, $sortDesc: Boolean, $take: Int, $skip: Int) {\n  collections: trendingCollections(\n    period: $period\n    sortBy: $sortBy\n    sortDesc: $sortDesc\n    take: $take\n    skip: $skip\n  ) {\n    id\n    collection {\n      id\n      name\n      isVerified\n      imageUrl\n      totalSupply\n      slug\n      salesFloor\n      previousSalesFloor\n      contractCreatedTimestamp\n      charts(period: $period) {\n        volume {\n          key\n          value\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    volume\n    salesCount\n    avgPrice\n    maxPrice\n    medianPrice\n    previous {\n      volume\n      salesCount\n      avgPrice\n      minPrice\n      maxPrice\n      medianPrice\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        header = {
            "Content-Type": "application/json",
        }
        res = requests.post(url=url ,headers=header, data=json.dumps(body))
    except Exception as e:
        print('error')
        print(e)
        pass

    return json.loads(res.content)

def getContractAddress(list_response):
    result = []
    for object_item in list_response['data']['collections']:
        result.append(object_item['collection']['slug'])

    return result

if __name__ == "__main__":
    # while True:
    #     print('get rarity list start')
    list_response = getListResponse()
    contract_address = getContractAddress(list_response)
    f = open("{}.txt".format('listen/listen_collection'),"w")
    f.write(json.dumps(contract_address))

    #     now = datetime.datetime.now()
    #     until_time = now + datetime.timedelta(hours=1)
    #     pause.until(until_time)
