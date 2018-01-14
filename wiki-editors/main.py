import requests
import re
import time

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

# 用户列表获取，直接存于文件或数据库中（防止内存耗尽）
def getUsers():
  try:
    # 正则写的比较简单，但应该 work
    regexr = {
      'normalUsers': re.compile(r'class="mw-userlink" title="[^"]+"><bdi>(.+?)</bdi>'),
      'redUsers': re.compile(r'class="new mw-userlink" title="[^"]+"><bdi>(.+?)</bdi>'),
      'nextPage': re.compile(r'<a href="([^"]+)" class="mw-nextlink" title="Special:ListUsers" rel="next">next 500</a>')
    }

    # 维基 3000 万用户，用户数组消耗内存会超级大，直接一边算一边存文件里
    redUsersNum = 0
    normalUsersNum = 0
    nextPageURL = UsersListURL
    while True:
      t0 = time.time()
      pageHTML = getWebHTML(nextPageURL)
      t1 = time.time()

      # normal users，并处理 HTML 转义字符，逐步写入文件
      pageNormalUsers = regexr['normalUsers'].findall(pageHTML)
      normalUsersNum += len(pageNormalUsers)
      fileStr = ''
      for u in pageNormalUsers:
        fileStr += handleHTMLEscapeChar(u) + '\n'
      with open('./normal_users.txt', 'a') as f:
        f.write(fileStr)

      # red users，并处理 HTML 转义字符，逐步写入文件
      pageRedUsers = regexr['redUsers'].findall(pageHTML)
      redUsersNum += len(pageRedUsers)
      fileStr = ''
      for u in pageRedUsers:
        fileStr += handleHTMLEscapeChar(u) + '\n'
      with open('./red_users.txt', 'a') as f:
        f.write(fileStr)
      
      nextPageURL = regexr['nextPage'].findall(pageHTML)[0]
      nextPageURL = handleHTMLEscapeChar(nextPageURL)
      nextPageURL = 'https://en.wikipedia.org' + nextPageURL

      t2 = time.time()
      # print info
      print('Normal Users: %d, Red Users: %d, Request time: %.2fs, Regexr time: %.2fs' % (normalUsersNum, redUsersNum, (t1 - t0), (t2 - t1)))

  except IndexError as e:
    print('Not found next page url')
  
    
# 用户信息获取，直接存于文件中
def getUsersContribs(users):
  # 正则写的比较简单，但应该 work
  regexr = {
    'contribs': re.compile(r'<li data-mw-revid="\d+"><a href="[^"]+" class="[^"]+" title="[^"]+">([^<]+)</a>'),
  }

  usersContribs = {}
  for u in users:
    # URL 拼装与 HTML 爬取
    # test
    pageHTML = getWebHTML(UserContribsURL + u + '?start=2016-01-01&end=2016-12-31')
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
  t0 = time.time()
  getUsers()
  t1 = time.time()
  print('Finish Getting Users List in %.2fs.' % (t1 - t0))

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



