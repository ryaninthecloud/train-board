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
            if len(cfg_file) == 0:
                raise FileNotFoundError
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
        except cpr.NoSectionError as no_section_error:
            print(f"Error - Invalid Configuration - Section Missing: {no_section_error} in Configuration File")
            exit(1)
        except KeyError as key_error:
            print(f"""Error: Invalid config, missing key: {key_error}""")
            exit(1)
        
        self.__common_headers = {
            'content-type': 
            'text/xml'
        }

    @staticmethod
    def make_ordinal(n) -> str:
        """
        Returns an ordinal string for a number
        Credit to: Florian Brucker on StackOverflow

        :param n: the integer position, i.e. 1 or 2
        :returns: the string ordinal position i.e. 1st or 2nd
        :rtype string
        """
        n = int(n)
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return str(n) + suffix
    
    @staticmethod
    def produce_error_response(error_key: str) -> dict:
        """
        Produces a standardised response when an error occurs
        in the retrieval, parsing or delivery of data.

        This response can be parsed and sent to the matrix display
        for viewing by the user. This function can be expanded in 
        the future for more detailed error management.

        :param error_message: error message content response
        :type: string
        :returns a dictionary of response content for api to deliver
        :rtype dictionary
        """
        known_errors = {
            "darwin_connection":"Could not connect to Darwin",
            "darwin_authorisation":"Check Darwin Token",
            "darwin_other":"Other Darwin Error",
            "darwin_station_key":"Check Station Key",
            "internal_auth":"Check IP Allwd",
            "check_logs_api":"Check Logs API"
        }

        error_template = {
            "response_status":500,
            "error_type": None,
            "error_message": None
        }

        if error_key not in known_errors.keys():
            error_template["error_type"] = error_key.strip().replace(" ","_")
            error_key["non-standard error raised"]
        else:
            error_template["error_type"] = error_key
            error_template["error_message"] = known_errors[error_key]

        return error_template

    def get_station_departures(self, departure_station=None, 
                             time_window=None, max_rows=None) -> str:
        """
        Makes request to Darwin to get station departures
        based on the configuration parameters

        :param departure_station: optional for alternative station
        :type: string
        :param time_window: optional for alternative time window
        :type: int
        :param max_rows: optional for alternative max rows
        :returns string of XML Response
        :rtype string
        """

        departure_station = departure_station if departure_station is not None else self.__default_departure_station
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
                    <ldb:crs>{departure_station}</ldb:crs>
                    <ldb:timeWindow>{time_window}</ldb:timeWindow>
                </ldb:GetDepartureBoardRequest>
            </soapenv:Body>
            </soapenv:Envelope>
        """
        try:        
            response = requests.post(self.__darwin_url, data=body, headers=self.__common_headers)
            print(response.status_code)
            print(response.text)
            if response.status_code == 401:
                return "XTErrorXT:darwin_authorisation"
            elif response.status_code in [404, 400]:
                return "XTErrorXT:darwin_connection"
            elif response.status_code != 200:
                return "XTErrorXT:darwin_other"
        except ConnectionError:
            return "XTErrorTX:darwin_connection"
        return response.text

    def return_display_friendly_departures(self, departures_element_tree: str) -> dict:
        """
        Returns a dictionary formatted for parsing by
        the ESP32 to display information on the
        matrix board.

        :param departures_element_tree: the element tree from the departures api
        :type: string
        :returns dictionary of train departures
        :rtype dict
        """

        if "XTErrorXT:" in departures_element_tree:
            return self.produce_error_response(departures_element_tree.split(":")[1])

        response_template = {
            "response_status":200,
            "data_for_station":None,
            "warning_messages":None,
            "train_services":None
        }

        service_template = {
            "ordinal":None,
            "destination":None,
            "sch_time":None,
            "exp_time":None
        }

        departures_dict = xmltodict.parse(departures_element_tree)

        try:
            content_root = departures_dict['soap:Envelope']\
                ['soap:Body']['GetDepartureBoardResponse']['GetStationBoardResult']
            data_for_station = content_root['lt4:locationName']
        except KeyError:
            return self.produce_error_response("darwin_station_key")

        try:
            warning_messages = content_root['lt4:nrccMessages']\
                ['lt:message']    
            if type(warning_messages) is list:
                warning_messages = warning_messages[0]
            warning_messages = warning_messages.split('.')[0].replace('/', '').replace("\n","").replace("<p>","").replace("</p>","")
        except KeyError:
            warning_messages = f'Good Service for station: {data_for_station}'

        cleaned_train_services = []

        try:
            train_services = content_root['lt8:trainServices']['lt8:service']
            train_service_position_integer = 1
            if isinstance(train_services, dict): train_services = [train_services]
            for service in train_services:
                _service = service_template.copy()
                _service['ordinal'] = self.make_ordinal(train_service_position_integer)
                _service['destination'] = service['lt5:destination']['lt4:location']['lt4:locationName']
                _service['sch_time'] = service['lt4:std']
                _service['exp_time'] = service['lt4:etd']
                cleaned_train_services.append(_service)
                train_service_position_integer += 1
        except KeyError:
            service = service_template
            service['ordinal'] = self.make_ordinal(1)
            service['destination'] = "NoSvcs"
            service['sch_time'] = "00:00"
            service['exp_time'] = "00:00"
            cleaned_train_services.append(service)

        print(cleaned_train_services)

        response_template["data_for_station"] = data_for_station
        response_template["warning_messages"] = warning_messages
        response_template["train_services"] = cleaned_train_services

        return response_template