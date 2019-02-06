import json, requests, urllib
from settings.secret import AIRTABLE_DATABASE_URL, AIRTABLE_API_KEY


# CONSTANTS

headers = {
    'authorization': 'Bearer ' + AIRTABLE_API_KEY,
    'content-type': 'application/json'
    } 


# UTILITY FUNCTIONS 

def prepare_data(data):
    # Convert data to airtable-compatible format
    data = {"fields": data}
    return json.dumps(data)

def check_for_offset(response_data):
    if "offset" in response_data :
        return response_data['offset']
    else :
        return False

# MAIN FUNCTIONS

def list_records(table, params=''):
    # Params should be given in a dictionary format
    # Offset is used when there are more than 100 records
    params = urllib.parse.urlencode(params, True)
    url = AIRTABLE_DATABASE_URL + table + "?" + params
    response = requests.get(url, headers=headers)
    return response

import asyncio
from aiohttp import ClientSession

async def async_process_records(table, params='', operation=print):
    '''
    Applies a given "operation" function to multiple records
    '''
    tasks = [] # asynchronous tasks
    response_data = list_records(table, params).json()
    offset = check_for_offset(response_data)

    while offset :
        records = response_data['records']
        print("Offset :", offset)
        for record in records :
            task = asyncio.ensure_future(operation(record))
            tasks.append(task)
        params['offset'] = offset
        response = list_records(table, params)
        response_data = response.json()
        offset = check_for_offset(response_data)
    else :
        records = response_data['records']
        for record in records :
            task = asyncio.ensure_future(operation(record))
            tasks.append(task)

    await asyncio.gather(*tasks)
      

def update_record(table, record_id, data):
    url = AIRTABLE_DATABASE_URL + table + '/' + record_id
    data = prepare_data(data)
    response = requests.patch(url, headers=headers, data=data)
    return response

#    response = list_records('Restaurants', {"filterByFormula": "{TEST}"})
#    response = update_record('Restaurants', 'recwcWo2WDGQD7VIH', {'TEST': False,})
#    process_records(
#        table='Restaurants',
#        params={"filterByFormula": "{Today's Trip}", "pageSize": "3"},
#        operation=print
#        )