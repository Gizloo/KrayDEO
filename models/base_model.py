import datetime
from pony.orm import *

db = Database()

db.bind(provider='postgres',
        user='postgres',
        password='1234',
        host='localhost',
        database='kraydeo_travel_base')


class Object(db.Entity):
    wialon_id = Required(int)
    name = Required(str)


class Travel(db.Entity):
    date_p = Required(datetime.datetime)
    name_object = Required(str)
    start_time = Required(str)
    end_time = Required(str)
    start_fuel_p = Required(float)
    start_fuel_w = Required(float)
    end_fuel_p = Required(float)
    end_fuel_w = Required(float)
    fuel_up_p = Required(float)
    fuel_up_w = Required(float)
    fuel_down = Required(float)
    consum_p = Required(float)
    consum_w = Required(float)
    consum_f = Required(float)
    wialon = Required(int)
    result = Required(str)


db.generate_mapping(create_tables=True)
