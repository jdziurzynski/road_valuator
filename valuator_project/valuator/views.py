from django.shortcuts import render
from django.http import JsonResponse
import requests
import json
import re
import datetime
from pprint import pprint
import pgeocode
from geopy.geocoders import Nominatim

key = 'BING MAPS KEY'




def resolve_waypoint(point):
    location = point
    country_code_pattern = r"(\D{1,2})"
    post_code_pattern = r"(\d{4,9})"
    post_code_pattern_pl = r"(\d{2}-\d{3,5})"
    country_code = re.search(country_code_pattern, point)
    if country_code:
        country_code = country_code[0]
        if country_code.upper() == 'PL':
            post_code_no = re.search(post_code_pattern_pl, point)
        else:
            post_code_no = re.search(post_code_pattern, point)
        if country_code and post_code_no:
            location = "{} {}".format(country_code, post_code_no[0]).upper()
    return location


def get_location(address):
    geolocator = Nominatim(user_agent="truck_valuator")
    location = geolocator.geocode(address)
    if location:
        return location
    return None

def get_location_reverse(long, lat):
    geolocator = Nominatim(user_agent="truck_valuator")
    coordinates = "{}, {}".format(long, lat)
    location = geolocator.reverse(coordinates)
    return location


def resolve_location(request):
    data = {'location': 'Not found'}
    location_input = request.GET.get('location', None)
    if location_input:
        solved = resolve_waypoint(str(location_input))
        location = get_location(solved)
        if location:
            data['location'] = location.address
    return JsonResponse(data)



def get_bing_road(start, dest, viapoints_locations=False, avoid=False, optimize=False):
    body = {
        'wp.1': '{},{}'.format(start.latitude, start.longitude),
    }

    if viapoints_locations:
        for n in viapoints_locations:
            k = 'vwp.{}'.format(int(n)+2)
            body[k] = '{},{}'.format(viapoints_locations[n].latitude, viapoints_locations[n].longitude)
    k_end = 'wp.{}'.format(len(body)+1)
    body[k_end] = '{},{}'.format(dest.latitude, dest.longitude)
    if optimize:
        body['optWp'] = optimize
    if avoid:
        body['avoid'] = avoid
    url = 'http://dev.virtualearth.net/REST/V1/Routes/Driving?key={}'.format(key)
    response = requests.get(url, params=body)
    if response.status_code == 200:
        return response.json()
    else:
        return False

def get_data_road(data):
    resources = data['resourceSets'][0]['resources'][0]
    distance = int(resources['travelDistance'])
    duration_raw = str(datetime.timedelta(seconds=resources['travelDuration'])).split(':')
    duration = "{}:{}h".format(duration_raw[0],duration_raw[1])
    sublegs = data['resourceSets'][0]['resources'][0]['routeLegs'][0]['routeSubLegs']
    vias = []
    for subleg in sublegs:
        duplicate = False
        if subleg['startWaypoint']['isVia']:
            for via in vias:
                if subleg['startWaypoint']['coordinates'][0] and subleg['startWaypoint']['coordinates'][1] in via:
                    duplicate = True
            if not duplicate:
                vias.append(subleg['startWaypoint']['coordinates'])
        if subleg['endWaypoint']['isVia']:
            for via in vias:
                if subleg['endWaypoint']['coordinates'][0] and subleg['endWaypoint']['coordinates'][1] in via:
                    duplicate = True
            if not duplicate:
                vias.append(subleg['endWaypoint']['coordinates'])
    vias_addrs = []
    for via in vias:
        location = get_location_reverse(via[0], via[1])
        addrs = "{}, {}".format(location.raw['address']['city'], location.raw['address']['country'])
        vias_addrs.append(addrs)
    response_data = {
        'distance': distance,
        'duration' : duration,
        'vias' : vias_addrs
    }
    return response_data

def proces_road(request):
    data = {'solved': False}
    avoid = ''
    avoid_str = ''
    start = request.GET.get('start', False)
    dest = request.GET.get('dest', False)
    viapoints = request.GET.get('viapoints', False)
    rate = request.GET.get('rate', False)
    highways = request.GET.get('highways', False)
    tolls = request.GET.get('tolls', False)
    bordercrossing = request.GET.get('bordercrossing', False)
    optimize = request.GET.get('optimize', False)
    viapoints_locations = {}
    if viapoints:
        viapoints = json.loads(viapoints)
        for n in viapoints:
            via_point = resolve_waypoint(viapoints[n])
            viapoints_locations[n] = get_location(via_point)
    if highways and highways != 'false':
        avoid += 'highways '
        avoid_str += 'Highways;'
    if tolls and tolls != 'false':
        avoid += 'tolls '
        avoid_str += 'Tolls;'
    if bordercrossing and bordercrossing != 'false':
        avoid += 'borderCrossing'
        avoid_str += 'Border Crossing '
    if avoid != '':
        avoid = avoid.replace(" ",",")
        avoid_str = avoid_str.replace(";",", ")
    start_point = resolve_waypoint(start)
    dest_point = resolve_waypoint(dest)
    start_location = get_location(start_point)
    dest_location = get_location(dest_point)
    if start_location and dest_location and rate:
        road_get = get_bing_road(start_location, dest_location, viapoints_locations=viapoints_locations, avoid=avoid, optimize=optimize)
        # pprint(road_get)
        if road_get:
            road_data = get_data_road(road_get)
            cost = int(road_data['distance'] * float(rate))
            start_str = start_location.address.split(',')
            start_str = "{}, {}".format(start_str[0], start_str[-1])
            dest_str = dest_location.address.split(',')
            dest_str = "{}, {}".format(dest_str[0], dest_str[-1])

            data = {
                'solved': True,
                'start': start_str,
                'dest': dest_str,
                'distance': str(road_data['distance']) + ' km',
                'duration': road_data['duration'],
                'avoid': avoid_str,
                'cost' : cost
            }
            if road_data['vias']:
                data['vias'] = road_data['vias']
    else:
        return JsonResponse(data)

    return JsonResponse(data)


def render_main(request):
    return render(request, 'main.html')
