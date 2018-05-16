import requests
import time
from bs4 import BeautifulSoup
from multiprocessing import Queue, Pool, Process


# 爬取代理网站信息
def get_proxies(data_queue, page_queue):
    headers = {
    'Referer':'http://www.xicidaili.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.3964.2 Safari/537.36'
    }
    count = 1
    while True:
        if page_queue.full():
            print('获取代理结束')
            break
        if data_queue.qsize() > 20:
            time.sleep(5)
        response = requests.request(method='get', url='http://www.xicidaili.com/nn/%s' % count, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        tr_list = soup.find(id="ip_list").find_all('tr')
        for i in tr_list:
            if i.has_attr('class'):
                td = i.find_all('td')
                ip = td[1].text
                port = td[2].text
                pro = td[5].text.lower()
                proxies = {pro : '%s://%s:%s' % (pro, ip, port)}
                data_queue.put(proxies)
        count += 1


# 验证爬取的代理是否可用
def veryfi_proxies(data_queue, page_queue):
    while True:
        if page_queue.full():
            print('验证代理结束')
            break
        print('验证代理获取数据')
        data = data_queue.get(timeout=2)
        try:
            requests.get(url='http://cn.bing.com/', proxies=data, timeout=5)
            print(data)
            data_persistence(data)
            page_queue.put(data, timeout=2)
        except Exception:
            pass



# 数据持久化
def data_persistence(data):
    pass


def main(num):
    data_queue = Queue()  # 存放代理的
    page_queue = Queue(maxsize=num)  #  存放flag ,如果队列满表示获取完客户指定的数量代理

    get = Process(target=get_proxies, args=(data_queue, page_queue,))
    get.start()
    v_list = []
    for i in range(20):
        a = Process(target=veryfi_proxies, args=(data_queue, page_queue,))
        a.start()
        v_list.append(a)
    get.join()
    for i in v_list:
        i.join()



if __name__ == '__main__':
    main(40)  # 传入需要代理个数
