#!/usr/bin/env python3
# coding=utf-8

import argparse
import json
import urllib.request

'''
Дата: 15.09.2017

Скрипт сбора статистики Nginx для Zabbix >= 3.4

Парсит страницу и отдаёт данные в JSON за один раз (одно соединение, вместо отдельного на каждый элемент)
Дальше zabbix сам парсит JSON и забирает значения по ключам.

Zabbix: версия не ниже 3.4
        Только начиная с 3.4 появились "зависимые элементы"
'''


def nginx_status(url):
    response = urllib.request.urlopen(url)
    if response.getcode() != 200:
        response.close()
        raise ValueError('HTTP %s received from %s.' % (response.getcode(), url))
    raw = response.read()
    response.close()

    data = raw.decode("utf-8").splitlines()
    data.remove('server accepts handled requests')  # Удаляем лишнюю строку "server accepts handled requests"

    # Парсим вывод и заполняем словарь
    result = {
        'Active_connections': data[0].split(': ')[1],
        'Reading': data[2].split(' ')[1],
        'Writing': data[2].split(' ')[3],
        'Waiting': data[2].split(' ')[5],
        'Accepts': data[1].split(' ')[1],
        'Handled': data[1].split(' ')[2],
        'Requests': data[1].split(' ')[3]
    }

    return json.dumps(result)


'''
Адрес страницы получаем из макроса Узла сети {$NGINX_STATUS_PAGE}
Если Узлу сети не присвоить макрос {$NGINX_STATUS_PAGE},  
то по умолчанию будет использоваться адрес http://localhost/nginx_status    
'''

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='URL to query stats', default='http://localhost/nginx_status')
    args = parser.parse_args()

    print(nginx_status(args.url))