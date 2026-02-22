# THIS MODULE WILL RUN MODULER CODE FROM HERE



# ETC IMPORTS
import argparse



# NSM IMPORTS
from nsm_scanner import Mass_IP_Scanner





class Program_Vars():
    """This will be used to pass vars from argparse to a class that stores them"""


    api_key_ipinfo = False




class Main():
    """This wil launch program wide logic"""



    parser = argparse.ArgumentParser(
        description="Mass IP Scanning framework meant to find vulnerable devices left uncheck open to the internet"
    )

    parser.add_argument("-p", help="The port you want to scan for")
    parser.add_argument("-t", help="This is to choose the max amount of threads you want to spawn at a time")
    parser.add_argument("-f", action="store_true", help="This option will save all active ips to a list database/ips.txt")
    parser.add_argument("-deep", action="store_true", help="this is to enable a ipinfo lookup")
    parser.add_argument("--ipinfo", help="Opotional to pass along your own api key for ipinfo.io or the program will default to none")


    args = parser.parse_args()

    port = args.p or False
    max_threads = args.t or 250
    save = args.f or False
    lookup = args.deep or False
    api_key_ipinfo = args.ipinfo or False


    
    Mass_IP_Scanner.save   = save
    Mass_IP_Scanner.lookup = lookup
    Mass_IP_Scanner.api_key_ipinfo = api_key_ipinfo

    Mass_IP_Scanner._main(port=port, threads=max_threads)
