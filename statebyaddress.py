#!/usr/bin/python3
import logging
import requests
from sqlalchemy import create_engine
from json import dumps
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

error_message = ''

# Setup Logger
logger = logging.getLogger("root")
logger.setLevel(logging.INFO)

# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

app = Flask(__name__)
api = Api(app)  # api is a collection of objects, where each object contains a specific functionality (GET, POST, etc)

# Method that calls google maps api to get latitude and longitude
def getAddrCoordinates(address=None, api_key=None, return_full_response=False):
    """Get geocode results from Google Maps Geocoding API.
    Note, that in the case of multiple google geocode results, this function returns details of the FIRST result.
    @param address: String address as accurate as possible. For Example "18 Grafton Street, Dublin, Ireland"
    @param api_key: String API key if present from google.
    @param return_full_response: Boolean to indicate if you'd like to return the full response from google.
    This is useful if you'd like additional location details for storage or parsing later."""

    output = {}
    # Set up your Geocoding url
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(address)
    if api_key is not None:
        geocode_url = geocode_url + "&key={}".format(api_key)

    logger.debug(geocode_url)

    # Ping google for the results
    try:
        results = requests.get(url=geocode_url, params=address)
        # Results will be in JSON format - convert to dict using requests functionality
        results = results.json()
        logger.debug('Results JSON value is: {}'.format(results))
        cont_processing = True
    except request.exceptions.Timeout:
        output = {
            "formatted_address": None,
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "google_place_id": None,
            "type": None,
            "postcode": None,
            "status_msg": "Timeout Occured connecting to the url. Please try after sometime"
        }
        output['status'] = 'ZERO_RESULTS'
        cont_processing = False
    except request.exceptions.TooManyRedirects:
        output = {
            "formatted_address": None,
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "google_place_id": None,
            "type": None,
            "postcode": None,
            "status_msg": "URL formed to call the Google API is bad: {}".format(geocode_url)
        }
        output['status'] = 'ZERO_RESULTS'
        cont_processing = False
    except request.exceptions.RequestException as e:
        output = {
            "formatted_address": None,
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "google_place_id": None,
            "type": None,
            "postcode": None,
            "status_msg": "Error calling to Google Maps API: {}".format(e)
        }
        output['status'] = 'ZERO_RESULTS'
        cont_processing = False

    if cont_processing:
        # if there's no results or an error, return empty results.
        if len(results['results']) == 0:
            output = {
                "formatted_address": None,
                "latitude": None,
                "longitude": None,
                "accuracy": None,
                "google_place_id": None,
                "type": None,
                "postcode": None,
                "status_msg": "Address passed to the API is not valid"
            }
        else:
            answer = results['results'][0]
            output = {
                "formatted_address": answer.get('formatted_address'),
                "latitude": answer.get('geometry').get('location').get('lat'),
                "longitude": answer.get('geometry').get('location').get('lng'),
                "accuracy": answer.get('geometry').get('location_type'),
                "google_place_id": answer.get("place_id"),
                "type": ",".join(answer.get('types')),
                "postcode": ",".join([x['long_name'] for x in answer.get('address_components')
                                      if 'postal_code' in x.get('types')]),
                "status_msg": None
            }

        # Append some other details:
        output['input_string'] = address
        output['number_of_results'] = len(results['results'])
        output['status'] = results.get('status')

        if return_full_response.lower() == 'true':
            output['google_response'] = results
        else:
            if return_full_response.lower() == 'false':
                output['google_response'] = None

    logger.debug("Output from Get Google Results Method is: {}".format(output))
    return output

# Method that uses latitude and longitude from google maps api to identify the state from PostgreSQL DB
def QueryOutput(geoloccoordinates, dbConn):
    logger.debug("Inside QueryOutput method")
    query = dbConn.execute(
        "SELECT name FROM tl_2019_us_state WHERE ST_CONTAINS(geom, ST_SetSRID(ST_MakePoint({}, {}), 26918));".format(
            geoloccoordinates['longitude'], geoloccoordinates['latitude']))
    finalresult = query.fetchone()
    logger.debug("The state of the address is: {}".format(finalresult[0]))
    return finalresult[0]

@app.route('/statebyaddress', methods=['GET'])
def runStateNameReq():
    addr = request.json['address']
    return_full_results = request.json['googleresultflag']
    dbusername = request.json['dbusername']
    dbpassword = request.json['dbpassword']
    dbhostname = request.json['dbhostname']
    dbname = request.json['dbname']
    apikeyforcall = request.json['apikeyforcall']

    # Db Connection String, GCP API Key and error Message initialization
    sqlconnectstring = 'postgresql://' + dbusername + ':' + dbpassword + '@' + dbhostname + '/' + dbname
    db_connect = create_engine(sqlconnectstring)

    geoResult = getAddrCoordinates(addr, apikeyforcall, return_full_results)

    # Construct the JSON response for the API
    # if there are no results or an error, return empty results.
    if geoResult["status"] != 'ZERO_RESULTS':
        dbdata_output = QueryOutput(geoResult, db_connect)

        responseContent = {
            "input_string": geoResult['input_string'],
            "formatted_address": geoResult['formatted_address'],
            "latitude": geoResult['latitude'],
            "longitude": geoResult['longitude'],
            "accuracy": geoResult['accuracy'],
            "google_place_id": geoResult['google_place_id'],
            "type": geoResult['type'],
            "postcode": geoResult['postcode'],
            "status_msg": geoResult['status_msg'],
            "us_state": dbdata_output,
            "google_response": geoResult['google_response']
        }
    else:
        responseContent = {
            "input_string": geoResult['input_string'],
            "formatted_address": None,
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "google_place_id": None,
            "type": None,
            "postcode": None,
            "status_msg": geoResult['status_msg'],
            "us_state": None,
            "google_response": geoResult['google_response']
        }

    return responseContent

if __name__ == '__main__':
    app.run(debug=True)
