import requests
import re

# 爬取的数据地址
UsersListURL = 'https://en.wikipedia.org/w/index.php?title=Special:ListUsers&limit=500'
UserDetailURL = 'https://en.wikipedia.org/wiki/Special:Contributions/'

# 网页 HTML 信息抓取
def getWebHTML(url):
  res = requests.get(url)
  return res.text

# 用户列表获取
def getUsers():
  try:
    # 正则写的比较简单，但应该 work
    regexr = {
      'pageUsers': re.compile('<bdi>(.+?)</bdi>'),
      'nextPage': re.compile('<a href="([^"]+)" class="mw-nextlink" title="Special:ListUsers" rel="next">next 500</a>')
    }

    users = []

    nextPageURL = UsersListURL
    while True:
      pageHTML = getWebHTML(nextPageURL)
      pageUsers = regexr['pageUsers'].findall(pageHTML)
      users.extend(pageUsers)
      print(len(users))

      nextPageURL = regexr['nextPage'].findall(pageHTML)[0]
      nextPageURL = nextPageURL.replace('&amp;', '&')
      nextPageURL = 'https://en.wikipedia.org' + nextPageURL
      print(nextPageURL)
  except IndexError as e:
    print('Not found next page url')

  return users
    

# 用户信息获取
def getUsersDetails(users):
  pass

# 获取数据
def getData():
  uesrs = getUsers()

# Main 接口
def main():
  getData()


main()



