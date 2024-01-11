"""
Code to support the control, flow and management
of the web interface application
"""
import configparser as cpr

def validate_configuration_for_application() -> None:
    """
    Validates the existence of the correct
    configuration file and the required keys.
    Should be called before using any of the functions
    listed in the application_control file.
    Create to avoid repeated validation in the below 
    functions.
    """
    parser = cpr.ConfigParser()
    configuration_file = None

    try:
        parser.read("configuration.ini")
        web_interface_configuration = parser["web_interface"]
        if len(web_interface_configuration) == 0:
            raise FileNotFoundError
    except FileNotFoundError:
        print("Error - Not Found: Web App cannot find configuration.ini")
        exit(1)
    except PermissionError:
        print("Error - Permissions: Web App cannot open configuration.ini")
        exit(1)
    except Exception as e:
        print(f"Error: Web App encountered {e} when reading configuration.ini")
        exit(1)
    
    print(configuration_file)

    try:
        allowed_ip_list = web_interface_configuration["allowed_ip_addresses"]
    except cpr.NoSectionError as no_section_error:
        print(f"Error - Invalid Configuration - Section Missing: {no_section_error} in Configuration File")
        exit(1)
    except KeyError as key_error:
        print(f"Error - Invalid Configuration: Web Application is missing key {key_error}")
        exit(1)


def load_restrictive_ip_configuration() -> (bool, list):
    """
    Loads the allowed_ip_list from the
    configuration.ini file.

    :returns a tuple containing the state of the ip restriction
    as well as a list of the allowed_ip_addresses 
    :rtype tuple
    """
    parser = cpr.ConfigParser()

    try:
        parser.read("configuration.ini")
        web_application_config = parser["web_interface"]
        ip_restriction_active = web_application_config["ip_restriction_active"]
        allowed_ip_addresses = web_application_config["allowed_ip_addresses"]
        ip_restriction_active = bool(ip_restriction_active)
        allowed_ip_addresses = [ip.replace(" ", "") for ip in allowed_ip_addresses.replace("[", "").replace("]", "").split(",")]
    except Exception as general_exception:
        print(f"Error Unknown: When attempting to load IP restrictive states: {general_exception}")
        exit(1)

    return (ip_restriction_active, allowed_ip_addresses)