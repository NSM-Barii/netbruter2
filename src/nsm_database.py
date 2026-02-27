# THIS WILL HOUSE UTILITIES AND OR FILES

# UI IMPORTS
from rich.console import Console


# ETC IMPORTS
from pathlib import Path
import json, requests, mmh3
from pymongo import MongoClient
from urllib.parse import urljoin, urlparse




console = Console()




class Database():
    """This will hold database values"""

    DATABASE_PORTS = [
        3306,   # MySQL
        5432,   # PostgreSQL
        27017,  # MongoDB
        6379,   # Redis
        9200    # Elasticsearch
    ]


   
    paths = [
         "/onvif/device_service",
        "/snapshot.jpg",
        "/video.cgi",
        "/ISAPI/System/status",
        "/cgi-bin/magicBox.cgi",
        "/doc/page/login.asp",
        "/web/cgi-bin/"
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
    def _check_paths(cls, ip, CONSOLE, timeout=1):
        """This will check path signatures"""

        
        #CONSOLE.print("started")
        for path in cls.paths:

            try:

                url = f"http://{ip}{path}"

                response = requests.get(url=url, timeout=timeout)
                headers = response.headers

                if response.status_code in [200,204]:


                    #favicon = mmh3.hash(response.content); CONSOLE.print(favicon)
                    server = headers.get("Server", False)
                    x_powered_by = headers.get("X-Powered-By", False)
                    CONSOLE.print(f"[bold green][+] Camera Path:[bold yellow] {server}  {x_powered_by}  {url}")   
          

            except Exception as e: 
                return
                CONSOLE.print(f"[bold red][-] Exception Error:[bold yellow] {e}")



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