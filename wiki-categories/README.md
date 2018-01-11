# Wiki-Spider
- 维基百科 Wikipedia 词条数据爬虫

## 原理
### 文件树
- 维基百科是按照 Category 和 Page 来组织整个文件树。
- Category 下面包含 Subcategories 和 Pages。
- Subcategory 也是一个 Category，只是它上层包含一个领域更广的 Category，它下面也包含很多更精确深入的 Subcategories，以及属于它这个 Category 的 Pages。
- Page 即通俗意义上的词条，即对一个名词的解释和百科，一个 Page 会属于多个 Categories。

### Page
- 类似 Github，每次 Page 的修改记录和对比都会被记录。
- 拿到 Page title 以后，可以调用维基百科 API，获取 Page 的所有信息。

### 数据存储
- 参照 [斯坦福大型网络数据集中的维基百科相关](https://snap.stanford.edu/data/wiki-meta.html)

## 项目进程
- 已经完成：可以拿到一个 Category 下所有 Subcategories 和 Pages。
- 未完成：根据 Page title 调用维基百科 API，获取 Page 信息。