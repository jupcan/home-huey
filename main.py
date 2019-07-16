#!/usr/bin/python3
# -*- coding: utf-8 -*-
from pprint import pprint
import random
import datetime
import uuid
import re
import pandas as pd
from phue import Bridge
import radar


def main():
    """
    creates bridge instance and executes algorithm
    """
    b = Bridge('bridge_ip')
    b.connect()
    lights = [l.name for l in b.lights]
    print(lights)
    start_date, end_date, name, rules = ask_info()
    bulbs = [random.randint(1, 4) for i in range(rules)]
    sol = [randomize(b, lights, start_date, end_date, name, x) for x in bulbs]
    pprint(sol)
    create_file(sol)

def ask_info():
    """
    :return: all user inputs needed to run the program
    :raises exception: not entering a valid input
    """
    valid = False
    delta_opts = {'d' : 'days','dia' : 'days', 'dias' : 'days', 'día' : 'days', 'días' : 'days' \
    , 'h' : 'hours', 'hora' : 'hours', 'horas' : 'hours', 'm' : 'minutes', \
    'minuto' : 'minutes', 'minutos' : 'minutes', 'es' : 'especial'}
    while not valid:
        name = input("introduce un nombre de vacaciones: ")
        date = input("introduce una fecha de inicio(yyyy-mm-dd hh:mm:ss): ")
        tvars = input("que intervalo y cantidad de tiempo quieres(d1-h5-m30-es7)? ")
        items = text_num_split(tvars)
        time = int(items[1])
        if items[0] in delta_opts:
            rules = int(input("cuantas rutinas quieres generar? "))
            interval = items[0]
        else:
            raise ValueError
        try:
            start_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            valid = True
            if delta_opts[interval] == 'days':
                end_date = start_date + datetime.timedelta(days=time)
            elif delta_opts[interval] == 'hours':
                end_date = start_date + datetime.timedelta(hours=time)
            elif delta_opts[interval] == 'minutes':
                end_date = start_date + datetime.timedelta(minutes=time)
            else:
                end_date = start_date + datetime.timedelta(days=time)
                daterange = pd.date_range(start_date, end_date)
                for single_date in daterange:
                    start_date = single_date
                    end_date = single_date + datetime.timedelta(hours=7)
        except ValueError:
            print("error. formato de fecha incorrecto.\n")
    return start_date.strftime("%Y-%m-%dT%H:%M:%S"), end_date.strftime("%Y-%m-%dT%H:%M:%S"), \
    name+uuid.uuid4().hex.upper()[0:4], rules

def randomize(bridge, lights, start_date, end_date, name, bulb):
    """
    creates random on/off dates and times for given bulbs in given range
    :param bridge: philip hue bridge instance
    :param lights: list of lights available on the bridge
    :param start_date: date range to start generating random ones
    :param end_date: date range end, adds number of days to start_date
    :param name: vacations name to identify generated rules on android app
    :param name: bulb id to randomize from the ones available in lights
    """
    on = {'on': True}
    off = {'on': False}
    start = radar.random_datetime(start=start_date, stop=end_date)
    start_str = start.strftime("%Y-%m-%dT%H:%M:%S")
    end = (start + datetime.timedelta(minutes=random.randint(1, 50))).replace(microsecond=0)
    end_str = end.strftime("%Y-%m-%dT%H:%M:%S")

    bridge.create_schedule(name, start_str, bulb, on)
    bridge.create_schedule(name, end_str, bulb, off)
    return lights[bulb-1], start_str, end_str, str(end-start)

def create_file(sol):
    """
    creates txt file with the solution
    :param sol: random home solution automatization
    """
    txt = open('out.txt', 'w')
    if sol is not None:
        txt.write("\n".join(str(item) for item in sol))
    else:
        print('no solution found')
        txt.write('no solution found')
    txt.close()

def text_num_split(item):
    """
    divides a string into char and digits
    :param item: what we want to divide
    :return: list of elements divided
    """
    for i, letter in enumerate(item, 0):
        if letter.isdigit():
            return [item[:i],item[i:]]

if __name__ == '__main__':
    main()
