import httpx
from urllib import parse
import time
import asyncio
from data import postData
import json
import pandas as pd
from fake_useragent import UserAgent
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('-l','--location', type=str, help='Enter your location', required=True)
parser.add_argument('-d', '--date', nargs=2, help='date format should be start_date: mm/dd/yyyy end_date: mm/dd/yyyy', required=True)

args = parser.parse_args()
location_input = args.location
date_input = args.date
start_date = date_input[0]
end_date = date_input[1]



target_url = 'https://communitycrimemap.com/'
agent = UserAgent()

# # Target Location Coordinates

async def getLocationCoordinates(location):
    search_query = parse.quote(location)
    location_CoordinatesUrl = f'https://geocode.search.hereapi.com/v1/geocode?q={search_query}&apiKey=jt44KWTUkN1qUFQLOecBsdtGsXUKKqGAsfcMIp8wW1o'
    async with httpx.AsyncClient() as client:
        request = await client.get(location_CoordinatesUrl)
        if request.status_code == 200:
            responseData = request.json()
            responseData = {'lat': float(responseData['items'][0]['position']['lat']), 'long':float(responseData['items'][0]['position']['lng'])}
            post_data = postData(start_date, end_date, {'longitude':responseData['long'], 'latitude':responseData['lat']})
            return post_data
        

        


# Request Authentication Token

async def getAuthenticationToken():
    url = f'{target_url}api/v1/auth/newToken'
    async with httpx.AsyncClient() as client:
        request = await client.get(url)
        if request.status_code == 200:
            responseData = request.json()            
            return responseData['data']['jwt']


async def getLocationData():
    url = f'{target_url}api/v1/search/load-data'
    async with httpx.AsyncClient() as client:
        request = await client.post(url, data=json.dumps(await getLocationCoordinates(location_input)), headers={"Content-Type": "application/json", "Authorization": f"Bearer {await getAuthenticationToken()}"})
        if request.status_code == 200:
            responseData= request.json()
            table_list = []
            for item in responseData['data']['data']['pins'].values():                
                dataLabel = item['EventRecord']['MOs']['MO'].get('label')
                dataCrime = item['EventRecord']['MOs']['MO'].get('Crime')
                dataAddress = item['EventRecord']['MOs']['MO'].get('AddressOfCrime')
                dataDate = item['EventRecord']['MOs']['MO'].get('DateTime')
                dataAgency = item['EventRecord']['MOs']['MO'].get('Agency')
                format =  {'Agency':dataAgency,'Class':dataLabel,'Crime':dataCrime,'Address':dataAddress,'Date':dataDate}
                table_list.append(format)
               
            df = pd.DataFrame(table_list)    
            df.to_csv('crimedata.csv')    
            return 'File Data Saved :)'
               
                
  

async def main():
    task = await asyncio.create_task(getLocationData())
    return task





start_time = time.perf_counter()
print(asyncio.run(main()))
end_time = time.perf_counter()

# print(f'time spent:{end_time-start_time}')
# import math
# latitude = 38.57944
# longitude = -121.49086
# offset = 1.0 / 1000.0
# latMax = latitude + offset
# latMin = latitude - offset

# lngOffset = offset * math.cos(latitude * math.pi / 180.0)
# lngMax = longitude + lngOffset
# lngMin = longitude - lngOffset

# print ('latMax = ' + str(latMax), 'latMin = ' + str(latMin), 'lngMax = '
#         + str(lngMax), 'lngMin = ' + str(lngMin))
