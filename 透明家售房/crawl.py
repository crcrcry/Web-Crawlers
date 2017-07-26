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
    # 基本信息获取
    for proj in projects:
        # test
        i = i + 1
        if i < 300:
            continue
        elif i > 305:
            break

        # sleep to avoid getting too fast
        time.sleep(0.5)
        URI = 'http://jia3.tmsf.com/tmj3/property_price.jspx?propertyid=%d&siteid=33&_d=%s' % (proj['propertyid'], now)

        result = {}
        result['price'] = dataCrawling(URI, 'priceboj\s*=\s*\'(.*)\'')
        houses.append(result)

    # 详细数据获取
    for item in houses:
        proj = item['price']

        detailData = {
            'page': [
                {
                    'name': 'images',
                    'url': 'http://jia3.tmsf.com/tmj3/property_detail.jspx?linktype=1&propertyid=%d&siteid=%s&_d=' % (proj['cohProperty']['propertyid'], proj['cohProperty']['siteid']),
                    'regexr': 'var property_\d+\s*=\s*\'(.*)\''
                },
                {
                    'name': 'housetype',
                    'url': 'http://jia3.tmsf.com/tmj3/property_housetype.jspx?siteid=%s&propertyid=%d&_=' % (proj['cohProperty']['siteid'], proj['cohProperty']['propertyid']),
                    'regexr': ''
                }
            ],
            'noPage': [
                {
                    'name': 'news',
                    'url': 'http://jia3.tmsf.com/tmj3/property_news.jspx?linktype=1&propertyid=%d&siteid=%s&_=&page=' % (proj['cohProperty']['propertyid'], proj['cohProperty']['siteid']),
                    'regexr': ''
                },
                {
                    'name': 'comment',
                    'url': 'http://jia3.tmsf.com/tmj3/property_comm.jspx?siteid=%s&propertyid=%d&_=&page=' % (proj['cohProperty']['siteid'], proj['cohProperty']['propertyid']),
                    'regexr': ''
                },
                {
                    'name': 'houseList',
                    'url': 'http://jia3.tmsf.com/tmj/property_control.jspx?siteid=%s&linkid=%d&buildingid=&area=&housetype=&_=&page=' % (proj['cohProperty']['siteid'], proj['cohProperty']['propertyid']),
                    'regexr': ''
                }
            ]
        }

        for data in detailData['page']:
            item[data['name']] = dataCrawling(data['url'], data['regexr'])
        for data in detailData['noPage']:
            item[data['name']] = pageDataCrawling(data['url'], data['regexr'])

        item['houses'] = []
        for data in item['houseList']:
            nowUrl = 'http://jia3.tmsf.com/tmj3/property_house.jspx?showid=%d&linkid=%d&siteid=%s&uuid=&openid=&_=' % (data['houseid'], proj['cohProperty']['propertyid'], proj['cohProperty']['siteid'])
            item['houses'].append(dataCrawling(nowUrl, ''))

    print('fetched %d houses info' % len(houses))
    return houses


def dataCrawling(url, regexr):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print('server responded %d' % r.status_code)

    if regexr == '':
        m = r.text
    else:
        m = re.search(regexr, r.text)
        if not m:
            print('cannot find project info for proj')
        m = m.group(1)

    return json.loads(m)

def pageDataCrawling(url, regexr):
    page = 1
    list = []
    while 1 == 1:
        result = dataCrawling(url+str(page), regexr)
        list.extend(result['list'])
        # 页数中 isover 属性标记是否有下一页
        if result['isover']:
            break
        else:
            page = page + 1
    return list


def updateProjectStore(db, collection, infos):
    # update data in db
    for item in infos:
        result = collection.find({"price.cohProperty.propertyid": item['price']['cohProperty']['propertyid']}).count()
        if result == 0:
            collection.insert_one(item)
            print("insert success")
        else:
            print("duplicate item")

# duration: interval(seconds)
def main(duration):
    # while 1 == 1:
        conn = MongoClient()
        db = conn.HangzhouHouses    # database
        collection = db.houses      # connection

        projects = fetchProjects()
        houses = fetchProjectInfo(projects)
        updateProjectStore(db, collection, houses)

        # time.sleep(duration)

if __name__ == '__main__':
    main(80000)
