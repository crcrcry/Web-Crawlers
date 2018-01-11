# Wiki-Spider
- 维基百科 Wikipedia Editors 数据爬虫

## 原理
- 维基百科 Special pages 中包含维基的数据统计，包括 All pages 和 All users
- 通过 All users 获取每位 user 的贡献信息

## 缺陷
- 维基百科的请求速度太慢，平均 4-5 秒才能抓 500 个用户，更换方法，直接下载 wikidata