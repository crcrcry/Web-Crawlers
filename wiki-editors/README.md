# Wiki-Spider
- 维基百科 Wikipedia Editors 数据爬虫

## 原理
- 维基百科 Special pages 中包含维基的数据统计，包括 All pages 和 All users（分红名与非红名）
- 通过 All users 获取每位 user 的贡献信息

## wikidata
- 维基百科的请求速度太慢，平均每秒请求一次页面
- wikidata 2018-1 有 28 G 数据，且只包含 wiki 中的条目和属性，不包含用户数据，无法使用

## improve
- 先做第一步好了
- 第二部找个框架来实现并行