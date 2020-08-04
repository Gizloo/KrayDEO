# -*- coding: utf-8 -*-
import datetime
from pprint import pprint

from wialon import flags, Wialon, WialonError


def execute_report(res_id, wialon, id, t1, t2):
    units1 = None
    units2 = None

    units = wialon.report_exec_report({
        'reportResourceId': res_id,
        'reportTemplateId': 1,
        'reportObjectId': id,
        'reportObjectSecId': 0,
        'interval': {'from': t1, 'to': t2, 'flags': 0}})
    # pprint(units)
    units = units['reportResult']['stats']

    units3 = wialon.report_exec_report({
        'reportResourceId': res_id,
        'reportTemplateId': 3,
        'reportObjectId': id,
        'reportObjectSecId': 0,
        'interval': {'from': t1, 'to': t2, 'flags': 0}})

    units4 = wialon.report_get_result_rows({
        "tableIndex": 0,
        "indexFrom": 0,
        "indexTo": 100
    })

    units5 = wialon.report_get_result_rows({
        "tableIndex": 1,
        "indexFrom": 0,
        "indexTo": 100
    })

    unit3 = wialon.messages_load_interval({

        "itemId": id,
        "timeFrom": t1,
        "timeTo": t2,
        "flags": 0x0000,
        "flagsMask": 0xFF00,
        "loadCount": 0xffffffff})

    mess_block = unit3['messages']
    first_mess_coord_x = None
    first_mess_coord_y = None

    for mess in mess_block:
        if mess['pos'] is not None:
            if mess['pos']['x']:
                first_mess_coord_x = mess['pos']['x']
                first_mess_coord_y = mess['pos']['y']
                break

    prostrel = 0
    prostrel_dist = 0
    prostrel_time = []

    for mess in mess_block:
        if mess['pos'] is not None:
            if mess['pos']['x'] is not None:
                dist = ((((mess['pos']['x']) - first_mess_coord_x) ** 2 + (
                        (mess['pos']['y']) - first_mess_coord_y) ** 2) ** 0.5) * 70000
                if dist > 600:
                    dist = round(dist)
                    prostrel += 1
                    prostrel_dist += dist

                    time_mess1 = mess['t']
                    time_mess = datetime.datetime.utcfromtimestamp(time_mess1 + 25200).strftime('%Y-%m-%dT%H:%M:%SZ')

                    time_mess = time_mess.replace('Z', ' ')
                    time_mess = time_mess.replace('T', ' ')

                    prostrel_time.append(str(time_mess)[:20:])

                    prostrel_time.append(dist)

                first_mess_coord_x = mess['pos']['x']
                first_mess_coord_y = mess['pos']['y']

    return units, prostrel, prostrel_dist, units4, units5


def execute_report2(res_id, wialon, id, t1, t2):
    units1 = None

    units = wialon.report_exec_report({
        'reportResourceId': res_id,
        'reportTemplateId': 2,
        'reportObjectId': id,
        'reportObjectSecId': 0,
        'interval': {'from': t1, 'to': t2, 'flags': 0}})

    units1 = wialon.report_get_result_rows({
        "tableIndex": 0,
        "indexFrom": 0,
        "indexTo": 0
    })

    volume_tank = units1[0]['c'][0]
    end_fuel_f = units1[0]['c'][5][:units1[0]['c'][5].find(' '):]
    fuel_up_f = units1[0]['c'][2]
    fuel_down = units1[0]['c'][3]
    start_fuel_f = units1[0]['c'][4]

    return float(volume_tank), float(end_fuel_f), float(fuel_up_f), float(fuel_down), float(start_fuel_f)


def execute_report3(res_id, wialon, id, t1, t2):

    units = wialon.report_exec_report({
        'reportResourceId': res_id,
        'reportTemplateId': 1,
        'reportObjectId': id,
        'reportObjectSecId': 0,
        'interval': {'from': t1, 'to': t2, 'flags': 0}})
    units = units['reportResult']['stats']
    return units



# token = 'db1cee3b1f964df20f8d163a1423b6c6286A919144720D152383E5DD77C6113AD31CDC9A'
# wialon = Wialon()
# login = None
# try:
#     login = wialon.token_login(token=str(token))
# except WialonError as e:
#     print('Error while login')
# wialon.sid = login['eid']
# t1 = 1592528400
# t2 = 1592571600+60
# percent, consum_f, fuel_up_f, fuel_down = execute_report2('21121126', wialon, '20986204', t1, t2)  # КамАЗ в938нв 124
#
