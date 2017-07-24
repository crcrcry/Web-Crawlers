import requests
import re
import json
import time
import datetime

from tenacity import retry
from pymongo import MongoClient

def fetchProjects():
    URI = 'http://www.tmsf.com/include/hzweb/index_search_center_property.js'
    r = requests.get(URI)
    if r.status_code != 200:
        raise RuntimeError('server responded %d' % r.status_code)
    m = re.search(r'data_auto\s*=(.+);', r.text, re.M)
    if not m:
        raise RuntimeError('cannot find projects')
    projects = json.loads(m.group(1))
    print('fetched %d projects' % len(projects))
    return projects

def fetchProjectInfo(projects):
    i = 0
    houses = []
    now = datetime.datetime.now().strftime('%Y%m%d%H')
    for proj in projects:
        # sleep to avoid getting too fast
        time.sleep(0.5)
        URI = 'http://jia3.tmsf.com/tmj3/property_price.jspx?propertyid=%d&siteid=33&_d=%s' % (proj['propertyid'], now)

        # add user-agent to headers
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        r = requests.get(URI, headers=headers)

        if r.status_code != 200:
            print('server responded %d' % r.status_code)
            continue
            # raise RuntimeError('server responded %d' % r.status_code)

        m = re.search('priceboj\s*=\s*\'(.*)\'', r.text)
        if not m:
            print('cannot find project info for proj')
            continue
            # raise RuntimeError('cannot find project info for proj')

        # parse data
        result = json.loads(m.group(1))
        houses.append(result)

    print('fetched %d houses info' % len(houses))
    return houses

def updateProjectStore(db, collection, infos):
    # update data in db
    for item in infos:
        result = collection.find({"cohProperty.propertyid": item['cohProperty']['propertyid']}).count()
        if result == 0:
            collection.insert_one(item)
            print("insert success")
        else:
            print("duplicate item")

# duration: interval(seconds)
def main(duration):
    while 1 == 1:
        conn = MongoClient()
        db = conn.HangzhouHouses    # database
        collection = db.houses      # connection

        projects = fetchProjects()
        houses = fetchProjectInfo(projects)
        updateProjectStore(db, collection, houses)

        time.sleep(duration)

if __name__ == '__main__':
    main(80000)
