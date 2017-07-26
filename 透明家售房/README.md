# 透明家售房
- [透明家售房](http://jia3.tmsf.com/web3/index.html)，杭州房屋数据爬虫，为 HomeFinder 做准备。

## 进度
### 已完成
- 楼盘基本数据获取
- 楼盘具体数据获取

---
### 未完成
- 楼盘数据分类、处理、存储

## 收获
- request 和 re 模块熟悉
- mongodb 和 pymongo 熟悉

## 踩坑
- re.search() 和 re.match() 只匹配一次，找到即返回，不过每次调用能查找下一处匹配的地方。re.findAll() 可以一次查找到全部匹配。
- re 中，group() + 参数，可以获取匹配之处的一部分。没有参数则获取匹配完整字符串。
- 爬虫要模拟浏览器，技巧很多，如请求头加 user-agent，[详见](https://my.oschina.net/jhao104/blog/647308?fromerr=LEc4jbps)
- 爬虫爬取过快，可能会被封 ip，可以 sleep 来逐条爬取。
- mongodb 中的 db 和 collection。
- mongodb 去重，好像没有快捷方法，手动查询比较。