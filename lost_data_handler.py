from pprint import pprint

from Exec_report import execute_report, execute_report3
from wialon import flags, Wialon, WialonError
from down_data import api_wialon_dwnData
import datetime
import time

# token = 'db1cee3b1f964df20f8d163a1423b6c6286A919144720D152383E5DD77C6113AD31CDC9A'
# ID = 21124722  # Камаз Т730НО
# TimeFrom = '2020-06-30-00-00-00'
# TimeTo = '2020-07-02-23-59-59'
#
# y, m, d, h, min, s = TimeFrom.split('-')
# y1, m1, d1, h1, min1, s1 = TimeTo.split('-')
# t1 = datetime.datetime(int(y), int(m), int(d), int(h), int(min), int(s))
# from_time = int(str(time.mktime(t1.timetuple()))[:-2])
# t2 = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(min1), int(s1))
# to_time = int(str(time.mktime(t2.timetuple()))[:-2])
#
# wialon = Wialon()
# login = None
# try:
#     login = wialon.token_login(token=str(token))
# except WialonError as e:
#     print('Error while login')
# wialon.sid = login['eid']
# res_id = api_wialon_dwnData(wialon)
# units4 = None
# units5 = None
# if res_id:
#     calb1, calb2, calb3, pr_count, pr_dist, units4, units5 = execute_report(res_id, wialon, ID, from_time, to_time)
# else:
#     print('No API resourses')

# pprint(units4)
# pprint(units5)

# count_data_down = int(units4[0]["c"][6])
# subrow = wialon.report_get_result_subrows({
#     "tableIndex": 0,
#     "rowIndex": 0
# })
#
# if count_data_down > 1:
#     for count in subrow:
#         from_time = count['t1']
#         to_time = count['t2']
#         print(f'from time: {from_time}; to time: {to_time}')
#         units = execute_report3(res_id, wialon, ID, from_time, to_time)
#
#         if -5 > float(units[4][1][:units[4][1].find(" "):]) - float(units[3][1][:units[3][1].find(" "):]) > 5:
#             value = datetime.datetime.fromtimestamp(from_time)
#             start_time = (value.strftime('%Y-%m-%d %H:%M:%S'))
#             value = datetime.datetime.fromtimestamp(to_time)
#             end_time = (value.strftime('%Y-%m-%d %H:%M'))
#             lost_data = 'Lost Data (>10%)'
#             lost_data_info = f'Потеря данных! Зафиксирован прострел в период с {start_time} до {end_time}'
#
#         else:
#
#             unit3 = wialon.messages_load_interval({
#
#                 "itemId": ID,
#                 "timeFrom": from_time - 1000,
#                 "timeTo": to_time + 1000,
#                 "flags": 0x0000,
#                 "flagsMask": 0xFF00,
#                 "loadCount": 0xffffffff})
#
#             mess_block = unit3['messages']
#             first_mess_coord_x = None
#             first_mess_coord_y = None
#
#             for mess in mess_block:
#                 if mess['pos'] is not None:
#                     if mess['pos']['x']:
#                         first_mess_coord_x = mess['pos']['x']
#                         first_mess_coord_y = mess['pos']['y']
#                         break
#
#             prostrel = 0
#             prostrel_dist = 0
#             prostrel_time = []
#
#             for mess in mess_block:
#                 if mess['pos'] is not None:
#                     if mess['pos']['x'] is not None:
#                         dist = ((((mess['pos']['x']) - first_mess_coord_x) ** 2 + (
#                                 (mess['pos']['y']) - first_mess_coord_y) ** 2) ** 0.5) * 70000
#                         if dist > 600:
#                             dist = round(dist)
#                             prostrel += 1
#                             prostrel_dist += dist
#
#                             time_mess1 = mess['t']
#                             time_mess = datetime.datetime.utcfromtimestamp(time_mess1 + 25200).strftime(
#                                 '%Y-%m-%dT%H:%M:%SZ')
#
#                             time_mess = time_mess.replace('Z', ' ')
#                             time_mess = time_mess.replace('T', ' ')
#
#                             prostrel_time.append(str(time_mess)[:20:])
#                             prostrel_time.append(dist)
#
#                         first_mess_coord_x = mess['pos']['x']
#                         first_mess_coord_y = mess['pos']['y']
#
#             if prostrel > 0 and prostrel_dist > 1000:
#
#                 value = datetime.datetime.fromtimestamp(from_time)
#                 start_time = (value.strftime('%Y-%m-%d %H:%M:%S'))
#                 value = datetime.datetime.fromtimestamp(to_time)
#                 end_time = (value.strftime('%Y-%m-%d %H:%M'))
#                 lost_data = 'Lost Data (>10%)'
#                 lost_data_info = f'Потеря данных! Зафиксирован прострел в период с {start_time} до {end_time}'

# if units4[0]['c'][4] == 0:
#     print('Потери связи нет')
# else:
#     print(f'Потери связи {units4[0]["c"][4]} секунд')


def lost_data(wialon, units4, res_id, ID):
    count_data_down = int(units4[0]["c"][6])
    subrow = wialon.report_get_result_subrows({
        "tableIndex": 0,
        "rowIndex": 0
    })

    if count_data_down > 1:
        for count in subrow:
            from_time = count['t1']
            to_time = count['t2']
            units = execute_report3(res_id, wialon, ID, from_time, to_time)

            if -5 > float(units[4][1][:units[4][1].find(" "):]) - float(units[3][1][:units[3][1].find(" "):]) > 5:
                value = datetime.datetime.fromtimestamp(from_time)
                start_time = (value.strftime('%Y-%m-%d %H:%M:%S'))
                value = datetime.datetime.fromtimestamp(to_time)
                end_time = (value.strftime('%Y-%m-%d %H:%M'))
                lost_data = 'Lost Data (>10%)'
                lost_data_info = 'Потеря данных! Зафиксировано падение топлива в период с {} до {}'.format(start_time, end_time)
                return lost_data, lost_data_info

            else:

                unit3 = wialon.messages_load_interval({

                    "itemId": ID,
                    "timeFrom": from_time - 1000,
                    "timeTo": to_time + 1000,
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
                                time_mess = datetime.datetime.utcfromtimestamp(time_mess1 + 25200).strftime(
                                    '%Y-%m-%dT%H:%M:%SZ')

                                time_mess = time_mess.replace('Z', ' ')
                                time_mess = time_mess.replace('T', ' ')

                                prostrel_time.append(str(time_mess)[:20:])
                                prostrel_time.append(dist)

                            first_mess_coord_x = mess['pos']['x']
                            first_mess_coord_y = mess['pos']['y']

                if prostrel > 0 and prostrel_dist > 1000:
                    value = datetime.datetime.fromtimestamp(from_time)
                    start_time = (value.strftime('%Y-%m-%d %H:%M:%S'))
                    value = datetime.datetime.fromtimestamp(to_time)
                    end_time = (value.strftime('%Y-%m-%d %H:%M'))
                    lost_data = 'Lost Data (>10%)'
                    lost_data_info = 'Потеря данных! Зафиксирован прострел в период с {} до {}'.format(start_time, end_time)

                    return lost_data, lost_data_info
