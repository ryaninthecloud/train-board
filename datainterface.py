"""
DataInterface provides an interface to make
and parse requests to the Darwin API
provided by Network Rail
"""

import configparser as cpr
from sys import exit
import requests
import xml.etree.ElementTree as ElementTree
import xmltodict
import json

class DataInterface:
    """
    DataInterface provides an interface to make
    and parse requests to the Darwin API
    provided by Network Rail and returns
    display middleware friendly responses
    """
    def __init__(self, config_location=None):
        """
        :param config_location: the config file 
               location, defaults if None
        :type: string
        """
        if config_location is None:
            config_location = "configuration.ini"

        cfg_file = cpr.ConfigParser()

        try:
            cfg_file.read(config_location)
        except PermissionError:
            print(f"""Error: Application does not have required permissions to open config file at {config_location}""")
            exit(1)
        except FileNotFoundError:
            print(f"""Error: Application config file at {config_location} does not exist.""")
            exit(1)

        try:
            cfg_file = cfg_file['darwin_config']
            self.__access_token = cfg_file['darwin_access_token']
            self.__default_arrival_station = cfg_file['dflt_arr_station']
            self.__default_departure_station = cfg_file['dflt_dep_station']
            self.__default_time_window = cfg_file['time_window']
            self.__default_max_rows = cfg_file['max_rows']
            self.__darwin_url = cfg_file['darwin_url']
        except KeyError as key_error:
            print(f"""Error: Invalid config, missing key: {key_error}""")
            exit(1)
        
        self.__common_headers = {
            'content-type': 
            'text/xml'
        }

    def get_station_arrivals(self, arrival_station=None, 
                             time_window=None, max_rows=None) -> str:
        """
        Makes request to Darwin to get station arrivals
        based on the configuration parameters

        :param arrival_station: optional for alternative station
        :type: string
        :param time_window: optional for alternative time window
        :type: int
        :param max_rows: optional for alternative max rows
        :returns string of XML Response
        :rtype string
        """

        arrival_station = arrival_station if arrival_station is not None else self.__default_arrival_station
        time_window = time_window if time_window is not None else self.__default_time_window
        max_rows = max_rows if max_rows is not None else self.__default_max_rows

        body = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:typ="http://thalesgroup.com/RTTI/2013-11-28/Token/types" xmlns:ldb="http://thalesgroup.com/RTTI/2021-11-01/ldb/">
            <soapenv:Header>
                <typ:AccessToken>
                    <typ:TokenValue>{self.__access_token}</typ:TokenValue>
                </typ:AccessToken>
            </soapenv:Header>
            <soapenv:Body>
                <ldb:GetDepartureBoardRequest>
                    <ldb:numRows>{max_rows}</ldb:numRows>
                    <ldb:crs>{arrival_station}</ldb:crs>
                    <ldb:timeWindow>{time_window}</ldb:timeWindow>
                </ldb:GetDepartureBoardRequest>
            </soapenv:Body>
            </soapenv:Envelope>
        """        
        response = requests.post(self.__darwin_url, data=body, headers=self.__common_headers)
        return response.text

    def return_display_friendly_arrivals(self, arrivals_element_tree: str) -> dict:
        """
        Returns a dictionary formatted for parsing by
        the ESP32 to display information on the
        matrix board.

        :param arrivals_element_tree: the element tree from the arrivals api
        :type: string
        :returns dictionary of train arrivals
        :rtype dict
        """
        arrivals_dict = xmltodict.parse(arrivals_element_tree)
        try:
            content_root = arrivals_dict['soap:Envelope']\
                ['soap:Body']['GetDepartureBoardResponse']['GetStationBoardResult']
            data_for_station = content_root['lt4:locationName']
        except KeyError:
            station_not_exists_value = {
                'destination':'ERR:STATION VALUE',
                'sch_arrival':'Error',
                'exp_arrival':'Error'
            }
            return {
                'data_for_station':'ERROR',
                'warning_messages':'CHECK STATION VALUE',
                'train_services':[station_not_exists_value]
            }

        try:
            warning_messages = content_root['lt4:nrccMessages']\
                ['lt:message'].split('.')[0].replace('/', '')
        except KeyError:
            warning_messages = f'Good Service for Station {data_for_station}'

        cleaned_train_services = []

        try:
            train_services = content_root['lt8:trainServices']['lt8:service']
            for service in train_services:
                _service = {}
                _service['destination'] = service['lt5:destination']['lt4:location']['lt4:locationName']
                _service['sch_arrival'] = service['lt4:std']
                _service['exp_arrival'] = service['lt4:etd']
                cleaned_train_services.append(_service)
        except KeyError:
            no_services_value = {
                'destination':'NO SERVICES',
                'sch_arrival':'',
                'exp_arrival':''
            }
            cleaned_train_services.append(no_services_value)

        return {
            'data_for_station':data_for_station,
            'warning_messages':warning_messages,
            'train_services':cleaned_train_services
        }