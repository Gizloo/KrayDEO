# -*- coding: utf-8 -*-
from lost_data_handler import lost_data


def handler1(calb1, mill, pr_count, pr_dist, from_time, to_time, wialon, units4, units5, res_id, ID):
    class callback:
        def __init__(self):
            self.data_status = 'Data OK'
            self.data_info = 'Данные корректны, прострелов/сливов за период потери связи нет'

            self.track_status = 'Track OK'
            self.track_info = 'Трек корректен, прострелов нет'

            self.dut_status = 'DUT OK'
            self.dut_info = 'ДУТ есть, работает'

            self.ign_status = 'IGN OK'
            self.ign_info = 'Зажигание работает'

    callback = callback()

    if float(units4[0]['c'][5]) >= (float(to_time) - float(from_time)) - 1800:
            callback.data_status = 'Нет данных за период!'
    elif float(units4[0]['c'][5]) > 3600:
        try:
            callback.data_status, callback.data_info = lost_data(wialon, units4, res_id, ID)
        except:
            pass

    if int(units5[0]['c'][3]) > 10 and float(units5[0]['c'][4]) > 3600:
        if float(calb1[3][1][:calb1[3][1].find("l"):]) == 0 and float(calb1[4][1][:calb1[4][1].find("l"):]):
            object_ = wialon.core_search_item({"id": ID,
                                               "flags": 0x00001000})
            sens = object_['item']['sens']

            for num, sen in sens.items():
                if 'Расходомер' in sen["n"]:
                    callback.dut_status = 'DUT not find'
                    callback.dut_info = 'ДУТ не установлен, есть расходомер'
            for num, sen in sens.items():
                if 'Топливо' in sen["n"] and 'fuel_level' in sen["t"]:
                    callback.dut_status = 'Lost DUT data'
                    callback.dut_info = 'ДУТ не работает'

        else:
            object_ = wialon.core_search_item({"id": ID,
                                               "flags": 0x00001000})
            sens = object_['item']['sens']

            for num, sen in sens.items():
                if 'Расходомер' in sen["n"]:
                    callback.dut_status = 'DUT not find'
                    callback.dut_info = 'ДУТ не установлен, есть расходомер'

            for num, sen in sens.items():
                if 'Топливо' in sen["n"] and 'fuel_level' in sen["t"]:
                    callback.dut_status = 'DUT OK'
                    callback.dut_info = 'ДУТ есть, работает'

    if pr_count > 1 and pr_dist/1000 > int(mill)/100*85:
        callback.track_status = 'Track NotOk (<90%)'
        callback.track_info = 'Зафиксировано {} прострелов; расстоянием {} км.'.format(pr_count, round(pr_dist/1000,1))

    object_ = wialon.core_search_item({"id": ID,
                                       "flags": 0x00001000})
    sens = object_['item']['sens']

    for num, sen in sens.items():
        if 'engine operation' in sen["t"]:
            count_days = 0
            if 'days' in calb1[2][1]:
                count_days = calb1[2][1][:count_days.find('d'):]
                count_days = int(count_days) * 24
                time = calb1[2][1]['days'+4:]
            else:
                time = calb1[2][1]
            h, m, s = time.split(':')
            h = int(h) + count_days
            if int(h) > 0 or int(m) > 0 or int(s) > 0:
                if 'pwr_ext' in sen["p"]:
                    callback.ign_status = 'IGN Warning'
                    callback.ign_info = 'Зажигание заведено на питание'
                    break
                else:
                    callback.ign_status = 'IGN OK'
                    callback.ign_info = 'Зажигание работает'
                    break
            else:
                callback.ign_status = 'IGN Error'
                callback.ign_info = 'Зажигание не работает'
                break
        else:
            callback.ign_status = 'IGN Error'
            callback.ign_info = 'Нет датчика зажигания'

    return callback


def handler2(volume_tank, consum_f, fuel_up_f, fuel_down, fuel_up_n, consum_n, start_fuel_p, start_fuel_f):

    class callback2:
        def __init__(self):
            self.fuel_start = False
            self.fuel_down = False
            self.fuel_up = False
            self.short = False
            self.perejog = False
            self.economy = False
            self.nedoliv = False

    callback2 = callback2()
    if int(fuel_down) > 0:
        callback2.fuel_down = True
    diff_f = fuel_up_f - fuel_up_n
    pr_diff_f = int(diff_f / volume_tank * 100)
    if pr_diff_f > 2:
        callback2.fuel_up = True
    if pr_diff_f < -2:
        callback2.nedoliv = True
    diff_fuel_start = int(start_fuel_f - start_fuel_p)
    if diff_fuel_start > 5 or diff_fuel_start < -5:
        callback2.fuel_start = True

    if float(volume_tank) > 500:
        if consum_n / volume_tank * 100 < 2:
            callback2.short = True
        else:
            diff_consum = consum_f - consum_n
            pr_diff_consum = int(diff_consum / volume_tank * 100)
            if pr_diff_consum > 1:
                callback2.perejog = True
            if pr_diff_consum < -1:
                callback2.economy = True

    elif float(volume_tank) > 300:
        if consum_n / volume_tank * 100 < 3:
            callback2.short = True
        else:
            diff_consum = consum_f - consum_n
            pr_diff_consum = int(diff_consum / volume_tank * 100)
            if pr_diff_consum > 1:
                callback2.perejog = True
            if pr_diff_consum < -1:
                callback2.economy = True
    else:
        if consum_n / volume_tank * 100 < 5:
            callback2.short = True
        else:
            diff_consum = consum_f - consum_n
            pr_diff_consum = int(diff_consum / volume_tank * 100)
            if pr_diff_consum > 1:
                callback2.perejog = True
            if pr_diff_consum < -1:
                callback2.economy = True

    return callback2


