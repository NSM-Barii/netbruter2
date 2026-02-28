# THIS WILL HOUSE UTILITIES AND OR FILES

# UI IMPORTS
from rich.console import Console


# ETC IMPORTS
from pathlib import Path
import json, requests, mmh3, re, threading
from pymongo import MongoClient
from urllib.parse import urljoin, urlparse
import geoip2.database


LOCK = threading.Lock()
console = Console()




class Database():
    """This will hold database values"""
    

    # SET FROM main.py
    selection = ""
    ports = False
    paths = False
    found = set()

    

    # PRESETS
    DATABASE_PORTS = [
        3306,   # MySQL
        5432,   # PostgreSQL
        27017,  # MongoDB
        6379,   # Redis
        9200    # Elasticsearch
    ]

    CAMERA_PORTS = [
        80,      # HTTP web interface (most common camera login page)
        443,     # HTTPS web interface (secure camera panel)
        554,     # RTSP video stream (very high signal for cameras)
        8000,    # Hikvision / OEM camera management port
        8080,    # Alternate HTTP web interface
        37777,   # Dahua proprietary service port
        34567,   # Common on generic / cheap OEM IP cameras
        3702,    # ONVIF discovery (usually LAN, not internet)
        8443     # Alternate HTTPS web interface
    ]

    ROUTER_PORTS = [
        80,     # HTTP admin panel
        443,    # HTTPS admin panel
        8080,   # Alternate web admin
        8443,   # Alternate secure admin
        23,     # Telnet (legacy routers)
        22,     # SSH management
        7547,   # TR-069 (ISP remote management)
        8291    # MikroTik Winbox
    ]

    NAS_PORTS = [
        5000,   # Synology HTTP
        5001,   # Synology HTTPS
        9000,   # Various NAS web panels
        445,    # SMB file sharing
        139     # NetBIOS session service
    ] 

    REMOTE_PORTS = [
        3389,   # RDP
        5900,   # VNC
        22,     # SSH
        21      # FTP
    ]

    IOT_PORTS = [
        1883,   # MQTT
        8883,   # Secure MQTT
        5683,   # CoAP
        5353    # mDNS (mostly LAN discovery)
    ]   


   
    paths_camera = [
         "/onvif/device_service",
        "/snapshot.jpg",
        "/video.cgi",
        "/ISAPI/System/status",
        "/cgi-bin/magicBox.cgi",
        "/doc/page/login.asp",
        "/web/cgi-bin/"
    ]

    paths_router = [
        "/",                 # title / server header
        "/login",            # common
        "/admin",            # common
        "/cgi-bin/",         # embedded web UIs
        "/HNAP1/",           # some consumer routers
        "/setup.cgi",        # older firmwares
        "/rom-0",            # legacy Zyxel-style misconfig (rare, but high signal)
        "/api/",             # modern web panels
    ]

    paths_nas = [
        "/",                       # landing page/title
        "/webman/index.cgi",       # Synology DSM (often redirects)
        "/auth.cgi",               # Synology auth endpoint (presence signal)
        "/cgi-bin/",               # QNAP/Synology patterns
        "/admin/",                 # generic NAS panels
    ]




    server_signatures = [
        "boa",
        "goahead",
        "uc-httpd",
        "thttpd",
        "webs",
        "app-webs",
        "hikvision",
        "dahua"
    ]


    www_auth_signatures = [
        'Basic realm="IP Camera"',
        'Basic realm="Login"',
        'Basic realm="WebCam"'
    ]


    html_signatures = [
        "ip camera",
        "network camera",
        "webcam",
        "live view",
        "hikvision",
        "dahua",
        "foscam",
        "onvif",
        "surveillance"
    ]


    
    """
    
    HIKVISION -->  DNVRS-Webs  http://85.0.232.117/#/portal
                   DNVRS-Webs
    HIKIVISION --> 2107490541
    
    """


   
    @classmethod
    def _check_paths(cls, ip, port, CONSOLE, timeout=1, errors=False):
        """This will check path signatures"""

        ip_camera_favicon_hashes = [
            {"model": "Axis IP Cameras", "hash": "b06e05c4b09e08bae67359c138e73d21"},
            {"model": "Hikvision IP Cameras", "hash": "2570d07e8d5c5283110b3e23f1ae1817"},
            {"model": "D-Link Sky IP Cameras", "hash": "c73c4b9efd843dcc7870f7c5be8cf603"},
            {"model": "Panasonic IP Cameras", "hash": "8031482ee5264c083b1cc9548139b077"},
            {"model": "Foscam IP Cameras", "hash": "530ca7eb297bf44e53dd13cc7024b42e"},
            {"model": "Vivotek IP Cameras", "hash": "43242d019fbb25470a7a87a6200ba66a"},
            {"model": "TP-Link IP Cameras", "hash": "5ae19a987cfae3351652008556fc8814"},
            {"model": "Logitech Circle", "hash": "4b3de2257f3c1192d661550f2c85b9d8"},
            {"model": "NETGEAR Arlo", "hash": "6e4a907392fa2924f798405e5cc94db4"},
            {"model": "Samsung SmartCam", "hash": "f97d4584fccb9de9bc50ef1858d6c7a1"},
            {"model": "Sony IP Cameras", "hash": "1c26fb09d268982a2d91b50f59e37345"},
            {"model": "Dahua IP Cameras", "hash": "dc4a40b1a269365bd6b78911d1a4d5d6"},
            {"model": "Amcrest IP Cameras", "hash": "63b2fc5054c4092e32e2fd8d0d2d6ac6"},
            {"model": "Toshiba IP Cameras", "hash": "201dcd953eb87f7c6845bba9cc70a7bc"},
            {"model": "Sricam IP Cameras", "hash": "494ae8e7ec4561bd7b8be2f36f0529c7"},
            {"model": "Reolink IP Cameras", "hash": "fda7303c0001529aa043c07098324d77"},
            {"model": "Zmodo IP Cameras", "hash": "6fc3cd798e5d2805c1b942c0b60ea482"}
        ]


        if not cls.paths: return
        space = "    "
        c1 = "bold red"
        c2 = "bold yellow"
        c3 = "bold blue"
        c4 = "bold green"

        
        for path in cls.paths:

            try:

                url = f"http://{ip}{path}"

                response = requests.get(url=url, timeout=timeout)
                headers = response.headers

                if response.status_code in [200,204]:

                     


                    favicon = mmh3.hash(response.content)
                    title = False
                    match = re.search(r"<title>(.*?)</title>", response.text, re.IGNORECASE | re.DOTALL)
                    if match: title = match.group(1).strip()
                    status = response.status_code
                    redirect = response.url if response.url != url else False
                    content_length = len(response.text) or False
                    server = headers.get("Server", False)
                    x_powered_by = headers.get("X-Powered-By", False)

                    
                    if False:
                        for var in cls.server_signatures:
                            if var == server.strip(): CONSOLE.print(f"Found: {server}")
                        
                        for var in cls.html_signatures:
                            if var == title.strip(): CONSOLE.print(f"Found: {title}")
                        

                        for camera in ip_camera_favicon_hashes:
                            if favicon == camera["hash"]:
                                CONSOLE.print(f"Match found: {camera['model']} at IP {ip} with hash {favicon}")
                        
                  
                  
                    with LOCK:
                        #if not t: CONSOLE.print(f"title: {title}  server: {server} favicon: {favicon}"); t = True
                        
                        CONSOLE.print(f"\n[{c4}][+] Active IP:[/{c4}] [{c2}]{ip}[/{c2}]:{port}")
                        CONSOLE.print(
                            f"{space}[{c4}][+] Directory:[{c2}] {url}",
                            f"\n{space}[{c4 if status else c1}][+] Status:[{c2}] {status}",
                            f"\n{space}[{c4 if title else c1}][+] Title:[{c2}] {title}",
                            f"\n{space}[{c4 if server else c1}][+] Server:[{c2}] {server}",
                            f"\n{space}[{c4 if redirect else c1}][+] Redirect:[{c2}] {redirect}",
                            f"\n{space}[{c4 if content_length else c1}][+] Content-Length:[{c2}] {content_length}",
                            f"\n{space}[{c4 if x_powered_by else c1}][+] Powered-by:[{c2}] {x_powered_by}",
                            f"\n{space}[{c4 if favicon else c1}][+] Favicon:[{c2}] {favicon}"
                        )
            
            except Exception as e: 
                if errors: CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")


    
    @classmethod
    def get_geo_info(cls, ip, CONSOLE, verbose=True):
        """This method will be used to get our own in house geo ip info"""

        
        p1 = "geo_lookup"
        path_asn  = str(Path(__file__).parent.parent / "database" /  p1 / "GeoLite2-ASN" / "GeoLite2-ASN.mmdb" )
        path_city = str(Path(__file__).parent.parent / "database" /  p1 / "GeoLite2-City" / "GeoLite2-City.mmdb" )

        
        try:

            reader_asn  = geoip2.database.Reader(path_asn)
            reader_city = geoip2.database.Reader(path_city)
            
            asn  = reader_asn.asn(ip)
            city  = reader_city.city(ip)


            info = {
                "country": city.country.name,
                "city":    city.city.name,
                "asn":     asn.autonomous_system_number,
                "org":     asn.autonomous_system_organization 
            
            }

            
            if info["country"] == "Mexico":
                CONSOLE.print(ip, info)
        


        except Exception as e: CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")






class File_Saver():
    """This class will save files"""




    @classmethod
    def _push_ips_found(cls, data, CONSOLE, verbose=True):
        """This will push current set of ips"""


        path = Path(__file__).parent.parent / "database" 

        
        if False:
            try:

                with open(path, "w") as file:json.dump(data, file, indent=4)
                if verbose: CONSOLE.print(f"[bold green][+] Successfully pushed new info")

            

            except Exception as e: CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")
        

        else:

            try:
                path = str(path / "ips.txt")
                clean = "\n".join(data)


                with open(path, "a") as file: file.write(clean)
                if verbose: CONSOLE.print(f"[bold green][+] Successfully pushed new info")

            
            except FileNotFoundError as e: 
                CONSOLE.print(f"[bold red][-] FileNotFoundError:[bold yellow] {e}")
                with open(path, "w") as file: 
                    file.write(data)
            
            except Exception as e: CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")




    #def _
  





class Deappreciated():
    """Out of use methods"""


    @classmethod
    def _check_database(cls, ip, port, CONSOLE, timeout=3):
        """This method will check for database"""
        

        try:

            client = MongoClient(f"mongodb://{ip}:{port}/", 
            serverSelectionTimeoutMS=1500,
            connectTimeoutMS=1500,
            socketTimeoutMS=1500
            )
            db = client.list_database_names()

            CONSOLE.print(f"[bold green][+] Dumped Your DB!!![/bold green] {db}")
        
        except Exception as e: CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")

    

    @classmethod
    def _snatch_path(cls, ip, CONSOLE, timeout=1, verbose=True):
        """Snatch the directory paths from js """  

        paths = []
        url = f"http://{ip}/"

        
        with sync_playwright() as p:
            
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url=url,  timeout=10000)
            page.wait_for_load_state("networkidle")

            elements = page.eval_on_selector(
            "a, script, link, form",
            "els => els.map(e => e.href || e.src || e.action).filter(Boolean)"
            )

            browser.close()

        
        for link in elements:
            parsed = urlparse(link)
            if parsed.path:
                paths.append(parsed.path)

                if verbose: CONSOLE.print(f"[bold green][+] Found path: {parsed.path}")
        

        return paths

    







if __name__ == "__main__":
    data = ["192.168.1.1", "10.0.0.1", "127.0.0.1"]
    File_Saver._push_ips_found(data=data)