#!/usr/bin/env python3
# coding=utf-8

import argparse
import json
import urllib.request

'''
Дата: 15.09.2017

Скрипт сбора статистики Apache для Zabbix >= 3.4

Парсит страницу и отдаёт данные в JSON за один раз (одно соединение, вместо отдельного на каждый элемент)
Дальше zabbix сам парсит JSON и забирает значения по ключам.

Apache: версия 2.4.x
        Может будет работать и на других версиях, если вывод mod_status не изменится

Zabbix: версия не ниже 3.4
        Только начиная с 3.4 появились "зависимые элементы"
'''


# Читаем содержимое страницы
# Удаляем лишние строки и возвращаем в виде списка

def get_apache_status(url):
    response = urllib.request.urlopen(url)
    if response.getcode() != 200:
        response.close()
        raise ValueError('HTTP %s received from %s.' % (response.getcode(), url))
    raw = response.read().decode("utf-8")
    response.close()
    raw = list(raw.splitlines()[10:])
    return raw


def parsing( data: object ) -> object:
    result = dict()
    for i in data:
        key, value = i.split(': ')
        key = key.replace(' ', '_').lower()
        if key != 'scoreboard':
            result[key] = value
        else:
            result['waiting_for_connection'] = value.count('_')
            result['starting_up'] = value.count('S')
            result['reading_request'] = value.count('R')
            result['sending_reply'] = value.count('W')
            result['keepalive'] = value.count('K')
            result['dns_lookup'] = value.count('D')
            result['closing_connection'] = value.count('C')
            result['logging'] = value.count('L')
            result['gracefully_finishing'] = value.count('G')
            result['idle_cleanup_of_worker'] = value.count('I')
            result['open_slots'] = value.count('.')
    return json.dumps(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='URL to query stats', default='http://localhost/server-status')
    args = parser.parse_args()

    ''' 
    К адресу стрницы добавляем '?auto' и вызываем функцию.
    Если указать адрес типа http://localhost/server-status?auto
    то zabbix будет ругаться на знак ? в передаваемом параметре.

    Адрес страницы получаем из макроса Узла сети {$APACHE_STATUS_PAGE}
    Если Узлу сети не присвоить макрос {$APACHE_STATUS_PAGE},  
    то по умолчанию будет использоваться адрес http://localhost/server-status    
    '''
    print(parsing(get_apache_status(args.url + '?auto')))