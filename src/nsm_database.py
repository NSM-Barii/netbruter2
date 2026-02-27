# THIS WILL HOUSE UTILITIES AND OR FILES

# UI IMPORTS
from rich.console import Console


# ETC IMPORTS
from pathlib import Path
import json, requests, mmh3, re
from pymongo import MongoClient
from urllib.parse import urljoin, urlparse




console = Console()




class Database():
    """This will hold database values"""

    selection = ""
    ports = False
    paths = False


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
    
    
    """


   
    @classmethod
    def _check_paths(cls, ip, port, CONSOLE, timeout=1, errors=False):
        """This will check path signatures"""


        if not cls.paths: return
        space = "    "
        c1 = "bold red"
        c2 = "bold yellow"
        c3 = "bold blue"
        c4 = "bold green"

        
        #CONSOLE.print("started")
        for path in cls.paths:

            try:

                url = f"http://{ip}{path}"

                response = requests.get(url=url, timeout=timeout)
                headers = response.headers

                if response.status_code in [200,204]:

                     


                    favicon = mmh3.hash(response.content)
                    title = False
                    match = re.search(r"<title>(.*?)</title>", response.text, re.IGNORECASE | re.DOTALL)
                    if match:
                        title = match.group(1).strip()
                    status = response.status_code
                    redirect = response.url if response.url != url else False
                    content_length = len(response.text) or False
                    server = headers.get("Server", False)
                    x_powered_by = headers.get("X-Powered-By", False)



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

    
    #def _
  



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










if __name__ == "__main__":
    data = ["192.168.1.1", "10.0.0.1", "127.0.0.1"]
    File_Saver._push_ips_found(data=data)