import re
import xml.etree.ElementTree as ET
from collections import namedtuple

import requests
from flask import Flask, request, session
from twilio.twiml.messaging_response import Body, Message, MessagingResponse
from credentials import secret_key

app = Flask(__name__)

app.secret_key = secret_key

# bot is to recieve two messages to obtain correct prediction of arrival time to a stop
# first message is of the format "route_id direction(North, South, East or West) location(i.e. Bay St)"
# second message is to confirm stop_id

@app.route('/', methods=['POST'])
def send_sms():
    # get text in message sent
    body = request.values.get('Body', None)
    
    resp = MessagingResponse()
    message = Message()
    message_body = ""
    
    # if first message was received, output the 5 earliest arrival times
    # else get stop_id from user
    if 'route_id' in session :
        times = fetch_times(body)
        session.pop('route_id', None)
        for time in times[:5]:
            message_body += "{} : {} minutes\n".format(time[0], time[1])
    else:
        # query string should be in format 'route_title' 'direction' 'location'"
        route_id, direction, location = re.split(r'\s', body, maxsplit=2)
        session['route_id'] = route_id
        
        queried_stops = route_info(route_id, direction, location)
        session['stops'] = queried_stops

        message_body += "Which stop id are you looking for?\n\n"
        for stop in session['stops']:
            message_body += "name: {} , id: {}\n".format(stop[0], stop[1])
        
    message.body(message_body)
    resp.append(message)

    return str(resp)


# get arrival predictions for specified 'stop_id'
def fetch_times(stop_id):
    params = {'command': 'predictions', 'a': 'ttc', 'stopId': stop_id.strip(), 'routeTag': session['route_id']}
    root = get_root(params)

    # [(route branch, minutes to arrival)]
    times = []
    for direction in root.find('predictions').findall('direction'):
        for prediction in direction.findall('prediction'):
            times.append((prediction.get('branch'), prediction.get('minutes')))

    return sorted(times, key=lambda tup: int(tup[1]))

# returns stops matching the user entered query
def route_info(route_id, direction, location):
    params = {'command': 'routeConfig', 'a': 'ttc', 'r': route_id}
    root = get_root(params)
    
    Stop_Info = namedtuple('Stop', 'tag title id')

    # filter stops with stop title containing 'location' substring
    route_stops = []
    for stop in root.find('route').findall('stop'):
        si = Stop_Info(stop.get('tag'), stop.get('title'), stop.get('stopId'))
        if location.lower() in (si.title).lower():
            route_stops.append(si)

    # further filter stops located in the 'direction' path
    direction_elements = root.findall("./route//direction[@name='" + direction + "']")
    query_stops = []
    for direction in direction_elements:
        for stop in direction.findall('stop'):
            for s in route_stops:
                if stop.get("tag") == s.tag:
                    query_stops.append((s.title, s.id))

    return query_stops

# takes in dict 'params' which specifies the parameters of the URL for the GET request
# returns the root of the XML tree
def get_root(params):
    url = 'http://webservices.nextbus.com/service/publicXMLFeed'
    r = requests.get(url, params=params)
    root = ET.fromstring(r.text)
    return root


if __name__ == '__main__':
    app.run()
