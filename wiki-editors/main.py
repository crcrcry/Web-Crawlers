import requests
import re

# 爬取的数据地址
UsersListURL = 'https://en.wikipedia.org/wiki/Special:ListUsers?username=&group=&editsOnly=1&wpsubmit=&wpFormIdentifier=mw-listusers-form&limit=500'
UserContribsURL = 'https://en.wikipedia.org/wiki/Special:Contributions/'
# example: https://en.wikipedia.org/wiki/Special:Contributions/Yin?start=2015-01-01&end=2015-12-31

# 网页 HTML 信息抓取
def getWebHTML(url):
  res = requests.get(url)
  return res.text

def handleHTMLEscapeChar(str):
  return str.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ')

# 用户列表获取
def getUsers():
  try:
    # 正则写的比较简单，但应该 work
    regexr = {
      'normalUsers': re.compile(r'class="mw-userlink" title="[^"]+"><bdi>(.+?)</bdi>'),
      'redUsers': re.compile(r'class="new mw-userlink" title="[^"]+"><bdi>(.+?)</bdi>'),
      'nextPage': re.compile(r'<a href="([^"]+)" class="mw-nextlink" title="Special:ListUsers" rel="next">next 500</a>')
    }

    normalUsers = []
    redUsers = []
    nextPageURL = UsersListURL
    while True:
      pageHTML = getWebHTML(nextPageURL)

      # normal users，并处理 HTML 转义字符，逐步写入文件
      pageNormalUsers = regexr['normalUsers'].findall(pageHTML)
      normalUsers.extend([handleHTMLEscapeChar(u) for u in pageNormalUsers])
      fileStr = ''
      for u in pageNormalUsers:
        fileStr += u + '\n'
      with open('./normal_users.txt', 'a') as f:
        f.write(fileStr)

      # red users，并处理 HTML 转义字符，逐步写入文件
      pageRedUsers = regexr['redUsers'].findall(pageHTML)
      redUsers.extend([handleHTMLEscapeChar(u) for u in pageRedUsers])
      fileStr = ''
      for u in pageRedUsers:
        fileStr += u + '\n'
      with open('./red_users.txt', 'a') as f:
        f.write(fileStr)

      # print info
      print('Normal Users: %d, Red Users: %d' % (len(normalUsers), len(redUsers)))

      nextPageURL = regexr['nextPage'].findall(pageHTML)[0]
      nextPageURL = handleHTMLEscapeChar(nextPageURL)
      nextPageURL = 'https://en.wikipedia.org' + nextPageURL
  except IndexError as e:
    print('Not found next page url')
  
  return {'redUsers': redUsers, 'normalUsers': normalUsers}
    
# 用户信息获取
def getUsersContribs(users):
  # 正则写的比较简单，但应该 work
  regexr = {
    'contribs': re.compile(r'<li data-mw-revid="\d+"><a href="[^"]+" class="[^"]+" title="[^"]+">([^<]+)</a>'),
  }

  usersContribs = {}
  for u in users:
    # URL 拼装与 HTML 爬取
    # test
    pageHTML = getWebHTML(UserContribsURL + u + '?start=2006-01-01&end=2016-12-31')
    # 正则，获取其中的 contributions
    contribs = regexr['contribs'].findall(pageHTML)
    print(contribs)
    # 存储每个人的所有 contributions，没有的存储 None
    if len(contribs) == 0:
      usersContribs[u] = None
    else:
      usersContribs[u] = contribs
  
  return usersContribs

# 获取数据
def getData():
  # 用户列表
  users = getUsers()
  print('Finish Getting Users List.')

  # 贡献时间列表
  # contribs = getUsersContribs(users)
  # print('Finish Getting Contributions List')
  # with open('./contribs.txt', 'w') as f:
  #   str = ''
  #   for c in contribs:
  #     for t in contribs[c]:
  #       str = str + c + ', ' + t + '\n'
  #   f.write(str)

# Main 接口
def main():
  getData()


main()



