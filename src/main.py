# THIS MODULE WILL RUN MODULER CODE FROM HERE



# ETC IMPORTS
import argparse, sys


# UI IMPORTS
from rich.console import Console
from rich.panel import Panel
console = Console()


# NSM IMPORTS
from nsm_scanner import Mass_IP_Scanner
from nsm_database import Database





class Program_Vars():
    """This will be used to pass vars from argparse to a class that stores them"""


    api_key_ipinfo = False




class Main():
    """This wil launch program wide logic"""


    data = (
    "\n [bold cyan]Mass IP Scanning Framework[/bold cyan]"
    "\n\n   [bold yellow]Find Vulnerable Devices[/bold yellow]"
    "\n\n    [bold magenta]Made by NSM-Barii[/bold magenta]\n"
)

    panel = Panel(renderable=data, expand=False, style="bold red")


    parser = argparse.ArgumentParser(
        description="Mass IP Scanning framework meant to find vulnerable devices left uncheck open to the internet"
    )

    parser.add_argument("-p", help="Port to scan.")
    parser.add_argument("-t", help="Maximum number of threads to spawn.")

    parser.add_argument("--save", action="store_true", help="Save all active IPs to database/ips.txt.")

    parser.add_argument("--iot",    action="store_true", help="Scan for IoT devices (MQTT, CoAP, mDNS).")
    parser.add_argument("--nas",    action="store_true", help="Scan for NAS devices (SMB, Synology, web panels).")
    parser.add_argument("--camera", action="store_true", help="Scan for IP cameras (RTSP, ONVIF, web interfaces).")
    parser.add_argument("--router", action="store_true", help="Scan for routers and network infrastructure (admin panels, SSH, Telnet, TR-069).")
    parser.add_argument("--remote", action="store_true", help="Scan for remote access services (RDP, VNC, SSH, FTP).")
    parser.add_argument("--database", action="store_true", help="Scan for open databases (3306, 5432, 27017, 6379, 9200).")
    

    parser.add_argument("--country", help="Only create IP Blocks within x Country")
    parser.add_argument("--show-all", action="store_true", help="Show all active IPS")
    parser.add_argument("--paths",  help="Manually set path for directory bruteforcing (nas, router, camera).")
 
    parser.add_argument("--geo", choices=["local", "ipinfo"], help="Enable IP geolocation lookup.")  
    parser.add_argument("--ipinfo", help="Optional ipinfo.io API key. Defaults to none.")


    args = parser.parse_args()


    if len(sys.argv) == 1:
        console.print(panel)
        parser.print_help(); exit()
        

    # REQUIRED VARS
    port = args.p        or False
    max_threads = args.t or 250


    # ADDITIONS
    save           = args.save        or False
    paths          = args.paths       or False
    country        = args.country     or False
    all            = args.show_all    or False
    lookup         = args.geo         or False
    api_key_ipinfo = args.ipinfo      or False
    

    # PRESET OPTIONS
    iot      = args.iot        or False
    nas      = args.nas        or False
    router   = args.router     or False
    remote   = args.remote     or False
    camera   = args.camera     or False
    database = args.database   or False

    
    # SET CONSTANTS
    Mass_IP_Scanner.all     = all
    Mass_IP_Scanner.save    = save
    Mass_IP_Scanner.country = country


    # ASSIGN PRESETS
    if iot:        port = Database.IOT_PORTS;    
    elif nas:      port = Database.paths_nas      ; Database.paths = Database.paths_nas
    elif router:   port = Database.ROUTER_PORTS   ; Database.paths = Database.paths_router
    elif remote:   port = Database.REMOTE_PORTS
    elif camera:   port = Database.CAMERA_PORTS   ; Database.paths = Database.paths_camera
    elif database: port = Database.DATABASE_PORTS 
    
    
    if paths:
        if   paths in ["nas"]:    Database.paths = Database.paths_nas
        elif paths in ["router"]: Database.paths = Database.paths_router    
        elif paths in ["camera"]: Database.paths = Database.paths_camera


    Database.ports  = port
    Database.lookup = lookup
    Database.api_key_ipinfo = api_key_ipinfo




    c1 = "red"; c2 = "bold green"; c3 = "bold blue"; c4 = "bold yellow"

    stats = (
        f"[{c1}][+] Port(s):[{c4}] {port}"
        f"\n[{c1}] [+] Max Workers:[{c4}] {max_threads}"
        f"\n[{c1}] [+] File Saving:[{c4}] {save}"
        f"\n[{c1}] [+] GEO Lookup:[{c4}] {lookup}"
        f"\n[{c1}] [+] API Key:[{c4}] {api_key_ipinfo}"
    )

    panel  = Panel(renderable= stats,        
        title="Constants",
        border_style="purple",
        style="bold red",
        expand=False 
    )
    
    console.print(
        f"[{c1}]=========   CONSTANTS   =========\n",
        stats,
        f"\n[{c1}]=================================",
    )

    

    Mass_IP_Scanner._main(port=port, threads=max_threads)
