from bs4 import BeautifulSoup
import requests

"""
需求分析， 输入用户名，返回能爬去到的用户信息
"""
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'
}


# 天涯， 传入用户ID或者用户名返回用户信息
def tianya_user(user_id):
    '''
    # http://search.tianya.cn/bbs?q=小杰s=0&f=2
    :param user_id:， 用户名，或者用户ID
    :return: dict 用户信息{}
    '''
    try:
        # 如果传入的是ID
        user_id = int(user_id)
        response = requests.get(url='http://www.tianya.cn/%s' % user_id, headers=headers)
    except ValueError as e:
        # 传入的是用户名
        user_id = user_id.strip()
        search_user_response = requests.get(url='http://search.tianya.cn/user?q=%s' % user_id, headers=headers)
        if search_user_response.status_code != 200:
            return False, '访问失败！'
        if search_user_response.text.find('暂时没有找到含有') != -1:
            return False, '当前用户不存在'
        soup = BeautifulSoup(search_user_response.text, 'lxml')
        url = soup.find(name='div', attrs={'class': 'searchListUser'}).find_all(name='li')[0].find(name='a').attrs.get(
            'href')

        response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        if response.text.find('您访问的用户不存在') != -1:
            return False, '当前用户不存在'
        else:
            soup = BeautifulSoup(response.text, 'lxml')
            user_div = soup.find(name='div', attrs={'class': 'base-info'})
            if not user_div:
                return False, '当前用户没有基本信息'
            user_info = {}
            # 解析出来性别
            strong = user_div.find(name='strong', attrs={'class': 'title'})
            if strong:
                if '他' in strong.text:
                    user_info['性别'] = '男'
                else:
                    user_info['性别'] = '女'
            # 解析其他信息
            temp_dict = {'user-location': '地址', 'user-bir': '生日', 'user-note': '描述', 'career-category': '行业',
                         'user-career': '职业', 'user-tags': '标签'}
            # 保存用户信息的li列表
            li_list = user_div.find(name='div', attrs={'class': 'info-wrapper'}).find_all(name='li')
            for li in li_list:
                if li:
                    i_class = li.find(name='i').attrs.get('class', None)[0]
                    if i_class:
                        if i_class.strip() in list(temp_dict.keys()):
                            user_info[temp_dict[i_class.strip()]] = li.text.strip()
                        else:
                            user_info[i_class] = li.text.strip()
            return True, user_info
    else:
        return False, '访问失败！'


# 知乎,传入用户名，返回用户信息
def zhihu_user(username):
    '''
    # https://www.zhihu.com/search?q=小杰&type=people
    :param username:
    :return:
    '''
    search_user_response = requests.get(url='https://www.zhihu.com/search?q=%s&type=people' % username.strip(),
                                        headers=headers)
    if search_user_response.status_code != 200:
        return False, '访问失败！'
    soup = BeautifulSoup(search_user_response.text, 'lxml')
    a_list = soup.find_all(name='a', attrs={'class': 'UserLink-link'})
    user_link = set()
    for a in a_list:
        if a:
            if a.attrs.get('href', None):
                user_link.add('https:%s' % a.attrs['href'])
    user_info = []
    for link in user_link:
        user_dict = {}
        user_response = requests.get(url=link, headers=headers)
        if user_response.status_code == 200:
            soup = BeautifulSoup(user_response.text, 'lxml')
            # 解析用户名
            user_name = soup.find(name='span', attrs={'class': 'ProfileHeader-name'}).text.strip()
            user_dict['用户名'] = user_name
            # 解析描述信息
            note = soup.find(name='span', attrs={'class': 'ProfileHeader-headline'}).text.strip()
            user_dict['描述'] = note
            # 解析男女
            if '他' in soup.find(name='button', attrs={'class': 'FollowButton'}).text:
                user_dict['性别'] = '男'
            else:
                user_dict['性别'] = '女'
            user_info.append(user_dict)
    return user_info


if __name__ == '__main__':
    print('天涯论坛传入用户ID120097474获取到:', tianya_user('120097474'))
    print('天涯论坛传入用户名‘小杰’获取到:', tianya_user('小杰'))
    print('知乎传入用户名‘小杰’获取到:', zhihu_user('小杰'))
