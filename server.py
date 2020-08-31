# -*- coding: utf-8 -*-
import datetime
import time

from pony import orm
from pony.orm import select, db_session, commit
from wialon import Wialon, WialonError
from flask import Flask, render_template
from Exec_report import execute_report, execute_report2
from down_data import api_wialon_dwnData
from handler import handler1, handler2
from models.base_model import Travel, Object
from models.test_model import Travel_Test, Object_Test
app = Flask(__name__)


@app.route("/KrayDEO/<requestbot>", methods=['GET'])
def index(requestbot):
    req_b = str(requestbot)
    token, ID, TimeFrom, TimeTo = req_b.split(';')
    if token == 'db1cee3b1f964df20f8d163a1423b6c6286A919144720D152383E5DD77C6113AD31CDC9A':
        token = 'db1cee3b1f964df20f8d163a1423b6c67D562ED72C4E60F2797A1247C61C9B977DBC7DCA'
    y, m, d, h, min, s = TimeFrom.split('-')
    y1, m1, d1, h1, min1, s1 = TimeTo.split('-')
    t1 = datetime.datetime(int(y), int(m), int(d), int(h), int(min), int(s))
    from_time = int(str(time.mktime(t1.timetuple()))[:-2]) - 25200
    t2 = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(min1), int(s1))
    to_time = int(str(time.mktime(t2.timetuple()))[:-2]) - 25200

    wialon = Wialon()
    login = None
    try:
        login = wialon.token_login(token=str(token))
    except WialonError as e:
        return ('Error while login')
    wialon.sid = login['eid']
    res_id = api_wialon_dwnData(wialon)

    if res_id:
        calb1, pr_count, pr_dist, units4, units5 = execute_report(res_id, wialon, ID, from_time, to_time)
    else:
        return 'No API resourses'

    milleage = int(str(calb1[1][1])[:calb1[1][1].find("."):])

    callback_retr = ''
    callback_retr += str(calb1[1][1])[:calb1[1][1].find(" "):] + ';'
    callback_retr += str(calb1[2][1]) + ';'
    callback_retr += str(calb1[4][1])[:calb1[4][1].find(" "):] + ';'
    callback_retr += str(calb1[3][1])[:calb1[3][1].find(" "):] + ';'
    callback_retr += str(calb1[5][1])[:calb1[5][1].find(" "):] + ';'
    callback_retr += str(calb1[6][1])[:calb1[6][1].find(" "):] + ';'
    callback = handler1(calb1, milleage, pr_count, pr_dist, from_time, to_time, wialon, units4, units5, res_id, ID)

    callback_retr += str(callback.data_status) + ';' + str(callback.track_status) \
                     + ';' + str(callback.dut_status) + ';' + str(callback.ign_status) + ';'

    return callback_retr


@app.route("/KrayDEO/norm/<requesthandler>", methods=['GET'])
def norm(requesthandler):
    req_b = str(requesthandler)

    token, ID, TimeFrom, TimeTo, start_fuel_n, consumption_n, fuel_up = req_b.split(';')
    if token == 'db1cee3b1f964df20f8d163a1423b6c6286A919144720D152383E5DD77C6113AD31CDC9A':
        token = 'db1cee3b1f964df20f8d163a1423b6c67D562ED72C4E60F2797A1247C61C9B977DBC7DCA'
    start_fuel_n.replace(',', '.')
    consumption_n.replace(',', '.')
    fuel_up.replace(',', '.')

    start_fuel_n, consumption_n, fuel_up = float(start_fuel_n), float(consumption_n), float(fuel_up)

    y, m, d, h, min, s = TimeFrom.split('-')
    y1, m1, d1, h1, min1, s1 = TimeTo.split('-')
    t1 = datetime.datetime(int(y), int(m), int(d), int(h), int(min), int(s))
    from_time = int(str(time.mktime(t1.timetuple()))[:-2]) - 25200
    t2 = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(min1), int(s1))
    to_time = int(str(time.mktime(t2.timetuple()))[:-2]) - 25200
    callback_consum_info = ""

    wialon = Wialon()
    login = None
    try:
        login = wialon.token_login(token=str(token))
    except WialonError as e:
        return ('Error while login')
    wialon.sid = login['eid']
    res_id = api_wialon_dwnData(wialon)

    if res_id:
        volume_tank, end_fuel_f, fuel_up_f, fuel_down, start_fuel_f = execute_report2(res_id, wialon, ID, from_time,
                                                                                      to_time)
    else:
        return 'No API resourses'

    consum_f = round(start_fuel_n + fuel_up - end_fuel_f, 2)

    callback = handler2(volume_tank, consum_f, fuel_up_f, fuel_down, fuel_up, consumption_n, start_fuel_n, start_fuel_f)
    callback_retr = ''

    if callback.fuel_up:
        callback_retr += "Заправка не сходится:" + str(round(fuel_up_f - fuel_up, 2)) + ";"
        callback_consum_info += "Заправка не сходится:" + str(round(fuel_up_f - fuel_up, 2)) + '\n'
    elif callback.nedoliv:
        callback_retr += "Недолив:" + str(round((fuel_up - fuel_up_f), 2)) + ";"
        callback_consum_info += "Недолив:" + str(round((fuel_up - fuel_up_f), 2)) + '\n'
    else:
        callback_retr += "Ok;"  # Заправка ОК

    if callback.fuel_down:
        callback_retr += str(round(fuel_down, 2)) + ";"
    else:
        callback_retr += "0;"  # Слив ОК

    if callback.fuel_start:
        callback_retr += "Нач ур. не сходится!;"
        callback_consum_info += "Нач ур. не сходится! \n"

    else:
        callback_retr += "Ok;"  # Нач ур. ОК

    """Дальше один из 4 вариантов"""
    if callback.short:
        callback_retr += "Короткая поездка, списание по норме;"
        callback_consum_info += "Короткая поездка, списание по норме \n"

    elif callback.perejog:
        callback_retr += "Пережог топлива:" + str(round(consum_f - consumption_n, 2)) + ", списание по факту;"
        callback_consum_info += "Пережог топлива:" + str(round(consum_f - consumption_n, 2)) + ", списание по факту"

    elif callback.economy:
        callback_retr += "Экономия топлива:" + str(round(consumption_n - consum_f, 2)) + ", списание по факту;"
        callback_consum_info += "Экономия топлива:" + str(round(consumption_n - consum_f, 2)) + ", списание по факту"

    else:
        callback_retr += "Расход сходится;"
        callback_consum_info += "Расход сходится"

    callback_retr += str(consum_f) + ';'
    end_fuel_n = float(start_fuel_n) - float(consumption_n) + float(fuel_up)
    data_obj = wialon.core_search_item({"id": ID, "flags": 0x00000001})
    name_obj = data_obj['item']['nm']
    start_period = '{}.{}.{}. {}:{}:{}'.format(d, m, y, h, min, s)
    end_period = '{}.{}.{}. {}:{}:{}'.format(d1, m1, y1, h1, min1, s1)
    consum_smt = float(start_fuel_f) + (fuel_up_f) - (end_fuel_f)
    consum_smt = round(consum_smt, 2)

    write_db(ID, name_obj, start_period, end_period, start_fuel_n, start_fuel_f,
             end_fuel_n, end_fuel_f, fuel_up, fuel_up_f, fuel_down, consumption_n, consum_smt, consum_f,
             callback_consum_info)

    return callback_retr


@app.route("/KrayDEO/test/<requestbot>", methods=['GET'])
def test(requestbot):
    req_b = str(requestbot)
    token, ID, TimeFrom, TimeTo = req_b.split(';')
    if token == 'db1cee3b1f964df20f8d163a1423b6c6286A919144720D152383E5DD77C6113AD31CDC9A':
        token = 'db1cee3b1f964df20f8d163a1423b6c67D562ED72C4E60F2797A1247C61C9B977DBC7DCA'
    y, m, d, h, min, s = TimeFrom.split('-')
    y1, m1, d1, h1, min1, s1 = TimeTo.split('-')
    t1 = datetime.datetime(int(y), int(m), int(d), int(h), int(min), int(s))
    from_time = int(str(time.mktime(t1.timetuple()))[:-2]) - 25200
    t2 = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(min1), int(s1))
    to_time = int(str(time.mktime(t2.timetuple()))[:-2]) - 25200
    wialon = Wialon()

    try:
        login = wialon.token_login(token=str(token))
    except WialonError as e:
        return ('Error while login')

    wialon.sid = login['eid']
    res_id = api_wialon_dwnData(wialon)

    if res_id:
        calb1, pr_count, pr_dist, units4, units5 = execute_report(res_id, wialon, ID, from_time, to_time)
    else:
        return 'No API resourses'

    milleage = int(str(calb1[1][1])[:calb1[1][1].find("."):])

    callback_retr = ''
    callback_retr += str(calb1[1][1])[:calb1[1][1].find(" "):] + ';'
    probeg = calb1[1][1].replace("km", 'км.')
    callback_retr += str(calb1[2][1]) + ';'
    motoh = calb1[2][1]
    callback_retr += str(calb1[4][1])[:calb1[4][1].find(" "):] + ';'
    start_fuel = calb1[4][1].replace("l", 'л.')

    callback_retr += str(calb1[3][1])[:calb1[3][1].find(" "):] + ';'
    end_fuel = calb1[3][1].replace("l", 'л.')

    callback_retr += str(calb1[5][1])[:calb1[5][1].find(" "):] + ';'
    fuel_up = calb1[5][1].replace("l", 'л.')
    callback_retr += str(calb1[6][1])[:calb1[6][1].find(" "):] + ';'
    fuel_down = calb1[6][1].replace("l", 'л.')
    callback = handler1(calb1, milleage, pr_count, pr_dist, from_time, to_time, wialon, units4, units5, res_id, ID)

    callback_retr += str(callback.data_status) + ';' + str(callback.track_status) \
                     + ';' + str(callback.dut_status) + ';' + str(callback.ign_status) + ';'

    data_obj = wialon.core_search_item({"id": ID, "flags": 0x00000001})
    name_obj = data_obj['item']['nm']
    start_period = "{}.{}.{}. {}:{}:{}".format(d, m, y, h, min, s)
    end_period = '{}.{}.{}. {}:{}:{}'.format(d1, m1, y1, h1, min1, s1)

    return render_template('test_first.html', name=name_obj, probeg=probeg, motoh=motoh, start_fuel=start_fuel,
                           end_fuel=end_fuel, fuel_up=fuel_up, fuel_down=fuel_down, start_period=start_period,
                           end_period=end_period, data_status=callback.data_status, data_info=callback.data_info,
                           track_status=callback.track_status, track_info=callback.track_info,
                           dut_status=callback.dut_info, ign_status=callback.ign_info, callback=callback_retr)


@app.route("/KrayDEO/test_norm/<requesthandler>", methods=['GET'])
def test_norm(requesthandler):
    req_b = str(requesthandler)
    token, ID, TimeFrom, TimeTo, start_fuel_n, consumption_n, fuel_up = req_b.split(';')
    if token == 'db1cee3b1f964df20f8d163a1423b6c6286A919144720D152383E5DD77C6113AD31CDC9A':
        token = 'db1cee3b1f964df20f8d163a1423b6c67D562ED72C4E60F2797A1247C61C9B977DBC7DCA'
    start_fuel_n.replace(',', '.')
    consumption_n.replace(',', '.')
    fuel_up.replace(',', '.')

    start_fuel_n, consumption_n, fuel_up = float(start_fuel_n), float(consumption_n), float(fuel_up)

    y, m, d, h, min, s = TimeFrom.split('-')
    y1, m1, d1, h1, min1, s1 = TimeTo.split('-')
    t1 = datetime.datetime(int(y), int(m), int(d), int(h), int(min), int(s))
    from_time = int(str(time.mktime(t1.timetuple()))[:-2]) - 25200
    t2 = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(min1), int(s1))
    to_time = int(str(time.mktime(t2.timetuple()))[:-2]) - 25200

    wialon = Wialon()
    login = None
    try:
        login = wialon.token_login(token=str(token))
    except WialonError as e:
        return ('Error while login')

    wialon.sid = login['eid']
    res_id = api_wialon_dwnData(wialon)

    if res_id:
        volume_tank, end_fuel_f, fuel_up_f, fuel_down, start_fuel_f = execute_report2(res_id, wialon, ID, from_time,
                                                                                      to_time)
    else:
        return 'No API resourses'

    consum_f = round(start_fuel_n + fuel_up - end_fuel_f, 2)

    callback = handler2(volume_tank, consum_f, fuel_up_f, fuel_down, fuel_up, consumption_n, start_fuel_n, start_fuel_f)
    callback_retr = ''

    if callback.fuel_up:
        diff = round(fuel_up_f - fuel_up, 2)
        callback_retr += "Заправка не сходится:" + str(round(fuel_up_f - fuel_up, 2)) + ";"
        callback_fuel_info = "Заправка не сходится, разница = {}".format(diff)

    elif callback.nedoliv:
        diff = round((fuel_up - fuel_up_f), 2)
        callback_retr += "Недолив:" + str(round((fuel_up - fuel_up_f), 2)) + ";"
        callback_fuel_info = "Недолив, объемом = {}".format(diff)
    else:
        callback_retr += "Ok;"  # Заправка ОК
        callback_fuel_info = "Заправка ОК"

    if callback.fuel_down:
        callback_retr += str(round(fuel_down, 2)) + ";"
    else:
        callback_retr += "0;"  # Слив ОК
    diff_start = round(float(start_fuel_n) - float(start_fuel_f))
    if callback.fuel_start:
        callback_retr += "Нач ур. не сходится!;"
        callback_start_info = "Нач ур. не сходится! Разница в {} л.".format(diff_start)
    else:
        callback_retr += "Ok;"  # Нач ур. ОК
        callback_start_info = "Нач. уровень сходится"

    """Дальше один из 4 вариантов"""
    if callback.short:
        pr_volume_consum = round((float(consumption_n) / float(volume_tank)) * 100, 2)
        callback_retr += "Короткая поездка, списание по норме;"
        callback_consum_info = "Короткая поездка, потрачено {}% от бака, списание по норме".format(pr_volume_consum)

    elif callback.perejog:
        diff = round(consum_f - consumption_n, 2)
        callback_retr += "Пережог топлива:" + str(round(consum_f - consumption_n, 2)) + ", списание по факту;"
        callback_consum_info = "Пережог топлива, объем = {}, списание по факту".format(diff)

    elif callback.economy and not callback.nedoliv and not callback.fuel_down:
        diff = round(consumption_n - consum_f, 2)
        callback_retr += "Экономия топлива:" + str(round(consumption_n - consum_f, 2)) + ", списание по факту;"
        callback_consum_info = "Экономия топлива, объем = {}, списание по факту".format(diff)

    else:
        callback_retr += "Расход сходится"
        callback_consum_info = 'Расход сходится (В пределах погрешности)'

    if float(fuel_down) > 0:
        fuel_down_info = 'Слито {}! Необходимо провести служебное расследование'.format(fuel_down)
    else:
        fuel_down_info = 'Cливов не зафиксировано'

    end_fuel_n = float(start_fuel_n) - float(consumption_n) + float(fuel_up)
    data_obj = wialon.core_search_item({"id": ID, "flags": 0x00000001})
    name_obj = data_obj['item']['nm']
    start_period = '{}.{}.{}. {}:{}:{}'.format(d, m, y, h, min, s)
    end_period = '{}.{}.{}. {}:{}:{}'.format(d1, m1, y1, h1, min1, s1)
    consum_smt = float(start_fuel_f) + (fuel_up_f) - (end_fuel_f)
    consum_smt = round(consum_smt, 2)

    write_db(ID, name_obj, start_period, end_period, start_fuel_n, start_fuel_f,
             end_fuel_n, end_fuel_f, fuel_up, fuel_up_f, fuel_down, consumption_n,
             consum_smt, consum_f, callback_consum_info, Test=True)

    return render_template('test_norm.html', name=name_obj, start_p=start_period,
                           end_period=end_period, start_fuel_n=start_fuel_n,
                           start_fuel_f=start_fuel_f, consumption_n=consumption_n, consum_f=consum_f, fuel_up=fuel_up,
                           fuel_up_f=fuel_up_f, fuel_down=fuel_down, callback=callback_retr,
                           callback_fuel_info=callback_fuel_info, callback_consum_info=callback_consum_info,
                           volume_tank=volume_tank, end_fuel_n=end_fuel_n, end_fuel_f=end_fuel_f,
                           callback_start_info=callback_start_info, fuel_down_info=fuel_down_info,
                           consum_smt=consum_smt)


@db_session
def write_db(wialon, name, start_period, end_period, start_fuel_n, start_fuel_f, end_fuel_n, end_fuel_f, fuel_up,
             fuel_up_f, fuel_down, consumption_n, consum_smt, consum_f, comm, Test=False):
    if Test:
        objs = select(o for o in Object_Test)
        if any(int(obj.wialon_id) == int(wialon) for obj in objs):
            pass
        else:
            Object_Test(wialon_id=wialon, name=name)

        Travel_Test(date_p=datetime.datetime.now(),
               name_object=name,
               start_time=start_period,
               end_time=end_period,
               start_fuel_p=start_fuel_n,
               start_fuel_w=start_fuel_f,
               end_fuel_p=end_fuel_n,
               end_fuel_w=end_fuel_f,
               fuel_up_p=fuel_up,
               fuel_up_w=fuel_up_f,
               fuel_down=fuel_down,
               consum_p=consumption_n,
               consum_w=consum_smt,
               consum_f=consum_f,
               wialon=wialon,
               result=comm)
    else:
        objs = select(o for o in Object)
        if any(int(obj.wialon_id) == int(wialon) for obj in objs):
            pass
        else:
            Object(wialon_id=wialon, name=name)

        Travel(date_p=datetime.datetime.now(),
               name_object=name,
               start_time=start_period,
               end_time=end_period,
               start_fuel_p=start_fuel_n,
               start_fuel_w=start_fuel_f,
               end_fuel_p=end_fuel_n,
               end_fuel_w=end_fuel_f,
               fuel_up_p=fuel_up,
               fuel_up_w=fuel_up_f,
               fuel_down=fuel_down,
               consum_p=consumption_n,
               consum_w=consum_smt,
               consum_f=consum_f,
               wialon=wialon,
               result=comm)


@app.route("/KrayDEO/travel", methods=['GET'])
@db_session
def travel_base():
    travels = select(p for p in Travel)
    objs = select(o for o in Object)
    return render_template('travel.html',
                           travels=travels, objs=objs)


@app.route("/KrayDEO/travel/<id_wialon>;<start_time>;<end_time>", methods=['GET'])
@db_session
def travel_base_obj(id_wialon, start_time, end_time):
    id_wialon = str(id_wialon)
    objs = select(o for o in Object)
    travels = select(p for p in Travel if p.wialon == id_wialon)
    return render_template('travel.html',
                           travels=travels, objs=objs)


@app.route("/KrayDEO/test/travel", methods=['GET'])
@db_session
def test_travel_base():
    travels = select(p for p in Travel_Test)
    objs = select(o for o in Object_Test)

    return render_template('test_travel.html',
                           travels=travels, objs=objs)


@app.route("/KrayDEO/test/travel/<id_wialon>;<start_time>;<end_time>", methods=['GET'])
@db_session
def test_travel_base_obj(id_wialon, start_time, end_time):
    id_wialon = str(id_wialon)
    objs = select(o for o in Object_Test)
    travels = select(p for p in Travel_Test if p.wialon == id_wialon)
    return render_template('test_travel.html',
                           travels=travels, objs=objs)


if __name__ == "__main__":
    app.run(host='localhost', port=4568, debug=False, threaded=True)
    # app.run(host='10.128.0.2', port=4567, debug=True, threaded=True)
