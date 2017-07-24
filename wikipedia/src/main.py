import requests
import re

# 处理爬取的 HTML 字符串
def dealHTML(html, categories, pages, pattern):
    categoryResult = pattern[0].findall(html)
    pageResult = pattern[2].findall(html)

    for value in categoryResult:
        categories.append(pattern[1].search(value).group()[9:])
    for value in pageResult:
        if 'Category:' not in value:    # 会有一些 Category: 之类的混进来，需要剔除
            pages.append(pattern[3].search(value).group()[12:-1])

# 逐行打印 List
def printList(list):
    for value in list:
        print(value)

# Main 接口
def main():
    categories = ['Artificial_neural_networks']   # 根类，注意需要把字符串中的空格转为下划线
    pages = []
    pattern = [
        re.compile(r'<a class="CategoryTreeLabel.+<\/a>'),
        re.compile(r'Category:\w+'),
        re.compile(r'<li><a href=.+<\/a><\/li>'),
        re.compile(r'href="\/wiki\/\S+')
    ]
    i = 0

    # 循环爬取嵌套的类别
    while i < len(categories):
        res = requests.get('https://en.wikipedia.org/wiki/Category:'+categories[i])
        dealHTML(res.text, categories, pages, pattern)
        i = i + 1

    print('一共爬取了%d个页面\n', len(pages))
    printList(pages)


main()



