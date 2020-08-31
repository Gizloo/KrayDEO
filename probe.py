from pony.orm import *
#
# db = Database()
#
#
# class Person(db.Entity):
#     name = PrimaryKey(int)
#     cars = Set('Car')
#
#
# class Car(db.Entity):
#     make = Required(str)
#     model = Required(str)
#     owner = Required(Person)
#
#
# db.bind(provider='postgres',
#         user='postgres',
#         password='1234',
#         host='localhost',
#         database='test_base')
#
# db.generate_mapping(create_tables=True)
#
#
# @db_session
# def test():
#     p1_test = 1234
#     p2_test = 231
#
#     if Person[p2_test] not in Person.select():
#         Person(name=p2_test)
#
#     Car(make='Toyota', model='Camry', owner=p1_test)
#     Car(make='Toyota', model='Camry1', owner=p1_test)
#     Car(make='Toyota', model='Camry2', owner=p1_test)
#     Car(make='Toyota', model='Camry2', owner=p2_test)
#
#     for per in Person.select():
#         print(per)
#     for car in Car.select():
#         print(f'{car.model} - {car.owner}')

import datetime
from pony.orm import *

db = Database()

db.bind(provider='postgres',
        user='postgres',
        password='1234',
        host='localhost',
        database='test_base3')


class Object(db.Entity):
    wialon_id = PrimaryKey(int)
    travel = Set('Travel')


class Travel(db.Entity):
    date_p = Required(datetime.datetime)
    name_object = Required(str)
    wialon = Required(Object)


db.generate_mapping(create_tables=True)


@db_session
def test():
    ob1_test = 1234

    if ob1_test not in Object.select():
        Object(wialon_id=ob1_test)

    Travel(date_p = datetime.datetime.now(),
           name_object='Toyota',
           wialon=ob1_test
           )
    Travel(date_p=datetime.datetime.now(),
           name_object='Toyota2',
           wialon=ob1_test
           )
    Travel(date_p=datetime.datetime.now(),
           name_object='Toyota3',
           wialon=ob1_test
           )
    Travel(date_p=datetime.datetime.now(),
           name_object='Toyota4',
           wialon=ob1_test
           )

    for travel in Travel.select():
        print(f'{travel.name_object}')


test()
