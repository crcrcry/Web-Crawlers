import requests
import re
import json
import time
import datetime

from pymongo import MongoClient

# 获取所有楼盘列表
def fetchProjects():
    URI = 'http://www.tmsf.com/include/hzweb/index_search_center_property.js'
    r = requests.get(URI)
    fail_count = 0

    # 请求失败时 重新请求 5 次。
    while r.status_code != 200:
        fail_count = fail_count + 1
        if fail_count >= 5:
            return []

        print('server responded %d' % r.status_code)
        time.sleep(0.5)
        r = requests.get(URI)

    m = re.search(r'data_auto\s*=(.+);', r.text, re.M)
    if not m:
        print('cannot find projects')
        return []
    projects = json.loads(m.group(1))
    print('fetched %d projects' % len(projects))
    return projects

# 获取楼盘下所有楼的房子的信息
def fetchProjectInfo(projects):
    i = 0
    houses = []
    now = datetime.datetime.now().strftime('%Y%m%d%H')
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H')

    # 基本信息获取
    for proj in projects:
        URI = 'http://jia3.tmsf.com/tmj3/property_price.jspx?propertyid=%d&siteid=33&_d=%s' % (proj['propertyid'], now)

        result = {}
        result['price'] = dataCrawling(URI, 'priceboj\s*=\s*\'(.*)\'')
        # 没抓到就别放进去了，防止 keyError
        if 'cohProperty' in result['price'].keys():
            result['price']['crawltime'] = nowtime  # 价格历史 时间数据
            houses.append(result)
    print('基本信息获取完毕')

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

        # 获取每一页中的每个房子的信息
        item['houses'] = []
        for data in item['houseList']:
            nowUrl = 'http://jia3.tmsf.com/tmj3/property_house.jspx?showid=%d&linkid=%d&siteid=%s&uuid=&openid=&_=' % (data['houseid'], proj['cohProperty']['propertyid'], proj['cohProperty']['siteid'])
            item['houses'].append(dataCrawling(nowUrl, ''))

    print('详细信息获取完毕')

    # 统一处理数据，加上 propertyid
    for item in houses:
        for property in item:
            # 处理 list
            if type(item[property]) == list:
                for obj in item[property]:
                    obj['propertyid'] = item['price']['cohProperty']['propertyid']
            # 处理 dict
            else:
                item[property]['propertyid'] = item['price']['cohProperty']['propertyid']
    print('数据处理完毕，准备存储入数据库')

    print('fetched %d houses info' % len(houses))
    return houses

# 爬取无需翻页的数据
def dataCrawling(url, regexr):
    # 请求时较容易发生网络错误，需要有对异常、对非200状态码的处理
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

        # time.sleep(0.5)     # 防止连续请求，请求太快
        r = requests.get(url, headers=headers)
        fail_count = 0

        # 请求失败时，重新请求
        while r.status_code != 200:
            fail_count = fail_count + 1
            print('server responded %d' % r.status_code)

            # 三次请求失败，这个数据先暂时不要了
            if fail_count >= 3:
                raise Exception('三次请求失败，这个数据先暂时不要了')
            else:
                time.sleep(0.5)
                r = requests.get(url, headers=headers)

        if regexr == '':
            m = r.text
        else:
            m = re.search(regexr, r.text)
            if not m:
                raise Exception('cannot find project info for proj')
            m = m.group(1)

        return json.loads(m)
    except Exception as e:
        print('Error in dataCrawling: %s' % e)
        return {}

# 爬取需要翻页的数据
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

# 更新数据库
def updateProjectStore(db, infos):
    # update data in db
    collections = {
        'price': db.prices,                 # 楼盘价格，propertyid 分辨楼盘，下同
        'images': db.images,                # 楼盘图片
        'housetype': db.housetypes,         # 楼盘下的经典户型
        'news': db.news,                    # 所有楼盘新闻列表
        'comment': db.comments,             # 所有楼盘评价列表
        'houseList': db.houseLists,         # 所有楼盘的所有 houses 的简要信息列表
        'houses': db.houses                 # 所有楼盘的所有 houses 的详细信息列表
    }

    for item in infos:
        for collection in collections:
            # price 数据记录历史
            if collection == 'price':
                collections[collection].insert(item[collection])
            # 清除旧的数据，用新的数据填充，保持数据最新
            else:
                collections[collection].remove({'propertyid': item['price']['propertyid']})
                if len(item[collection]) != 0:
                    collections[collection].insert(item[collection])

    print('update success')

# Main 入口
def main():
    try:
        conn = MongoClient()
        db = conn.HangzhouHouses  # database

        projects = fetchProjects()
        houses = fetchProjectInfo(projects)
        updateProjectStore(db, houses)
    except Exception as e:
        print("Error: %s" % e)

if __name__ == '__main__':
    main()
