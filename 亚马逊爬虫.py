from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import openpyxl
import xlrd
import os

save_file = 'save.xlsx'


def main(excel_file):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('log-level=3')

    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe', chrome_options=chrome_options)

    driver.implicitly_wait(20)

    workbook = xlrd.open_workbook(excel_file)
    worksheet = workbook.sheets()[0]

    new_workbook = openpyxl.Workbook()
    new_sheet = new_workbook.create_sheet('验证成功')

    start_rows = 0

    if os.path.isfile('%s.tmp' % excel_file):
        temp_file = open('%s.tmp' % excel_file, 'r+')
        start_rows = int(temp_file.readlines()[-1])
    else:
        temp_file = open('%s.tmp' % excel_file, 'w+')
    for i in range(start_rows, worksheet.nrows):
        if i == 0:
            continue
        rows = worksheet.row_values(i)
        url = 'https://www.amazon.com/dp/%s' % rows[1]
        driver.get(url=url)
        value = driver.page_source.find('Amazon Best Sellers Rank')
        if value != -1:
            print('验证成功:', rows)
            new_sheet.append(rows)
            new_workbook.save(save_file)
        else:
            print('验证失败:', rows)

        temp_file.write('%s\n' % i)
        temp_file.flush()
    # 保存excel文件
    new_workbook.save(save_file)
    os.remove('%s.tmp' % excel_file)
    driver.close()
    driver.quit()


if __name__ == '__main__':
    help = '''
    **************************************************************************
    
                                亚马逊爬虫
        
    **************************************************************************
    '''
    print(help)
    while True:
        file = input('请输入验证文件的绝对路径：')
        if os.path.isfile(file):
            break
        else:
            print('输入文件路径不存在！请重新输入')
    excel_file = file
    main(excel_file)
    input('程序执行完毕，结果文件保存在%s!按任意键退出...' % save_file)

