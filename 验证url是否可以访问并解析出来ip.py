# coding=utf-8
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import socket
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 正常访问的
success_file = 'success.txt'
# 访问失败的
erro_file = 'erro.txt'
# 正常失败的，都在
other = 'xxx.txt'
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36"
}


def parse_ip(url, port):
    domain = url.split('//')[1].split('/')[0].split(':')[0]
    ip = socket.getaddrinfo(domain, port)[-1][-1]
    print('%s解析出来ip:' % url, ip[0])
    return ip


def requests_url(url):
    try:
        response = requests.get(url=url, headers=headers, verify=False, timeout=30)
    except Exception as e:
        print('[ERRORE]访问失败:%s' % url)
        return False, url, '', ''
    response.encoding = response.apparent_encoding
    if response.status_code == 200:
        print('[SUCCESS]访问成功:%s' % url)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find(name='title').text if soup.find(name='title') else ""
        if title.find('404页面') != -1:
            return False, url, '', ''
        if response.url.startswith('http:'):
            ip, port = parse_ip(url, "80")
            return True, url, ip, title
        else:
            ip, port = parse_ip(url, "443")
            return True, url, ip, title
    else:
        print('[ERRORE]访问失败:%s' % url)
        return False, url, '', ''



def save_data(url):
    a, url, ip, title = requests_url(url)
    if a:
        with open(success_file, 'a+', encoding='utf-8') as f:
            print('写入文件：', '%s,%s,%s\n' % (ip.strip(), title.strip(), url.strip()))
            f.write('%s\t%s\t%s\n' % (ip.strip(), title.strip(), url.strip()))
        with open(other, 'a+', encoding='utf-8') as f:
            f.write('%s\t%s\t%s\n' % (ip.strip(), title.strip(), url.strip()))
    else:
        with open(erro_file, 'a+', encoding='utf-8') as f:
            f.write('%s\n' % url)
        with open(other, 'a+', encoding='utf-8') as f:
            f.write('%s\n' % url)



def main(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        url_list = f.readlines()
    for url in url_list:
        if url and len(url) > 4:
            handel_url = url.strip().replace('"', '')
            if handel_url.startswith('http'):
                save_data(handel_url)
            else:
                save_data('http://%s' % handel_url)
                save_data('https://%s' % handel_url)


if __name__ == '__main__':
    main('url.txt')
    # print(requests_url('https://etrade.ydamc.com/etrading/'))
