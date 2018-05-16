import requests
from bs4 import BeautifulSoup
from uuid import uuid4

# 发送get请求下载整个网站
response = requests.get(
    url='https://www.autohome.com.cn/news/')

# 指定编码为此网站的编码
response.encoding = response.apparent_encoding

# response.text 所有HTML标签的文本格式

# 下载的html文本转换成对象， 第二个参数指定html解析器为 lxml
soup = BeautifulSoup(response.text, 'lxml')

# 获取包含所有新闻列表的DIV
news_div = soup.find(id='auto-channel-lazyload-article')

# 查找news_div下的所有li标签  list类型
news_li_list = news_div.find_all('li')

for a in news_li_list:
    news_a = a.find('a')  # 查找li下边每一个li标签包含的a标签
    if news_a:
        # print(news_a.attrs)  # 返回a标签的属性 字典类型 {'href':'//www.autohome.com.cn/news/201803/914177.html#pvareaid=102624'}
        title = news_a.find('h3').text  # 获取新闻的标题
        news_img ='http:%s' % news_a.find('img').attrs.get('src')  # 获取图片链接

        # 发送get请求下载图片
        img_respone = requests.get(url=news_img)
        filename = str(uuid4()) + '.jpg'  # 创建一个文件名
        # 保存文件到本地
        with open(filename, 'wb') as f:
            f.write(img_respone.content)  # 获取的img_respone转换成字节

        print('标题：%s  链接：http:%s  相关图片：%s' % (title, news_a.attrs.get('href'), news_img))  # 获取所有的新闻链接
