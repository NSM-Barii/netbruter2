# THIS WILL BE A TEST SCRIPT FOR NETBRUTER2.0



# UI IMPORTS
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
import pyfiglet


# NETWORK IMPORTS
import ipaddress, socket, requests


# ETC IMPORTS
import time, random, threading
from concurrent.futures import ThreadPoolExecutor, as_completed


# NSM IMPORTS
from nsm_database import File_Saver, Database

console = Console()
LOCK = threading.Lock()


class Mass_IP_Scanner():
    """This class will be responsible for finding active ips on user choosen port"""

    
    save = False
    lookup = False 
    api_key_ipinfo = False



    @classmethod
    def _generate_random_ip(cls, verbose=False):
        """This will generate a random ip and return it"""
        

        try:

            random_ip = (f"{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}")

            if verbose: console.print(f"[bold green]Generated IP:[bold yellow] {random_ip}")

        except Exception as e: print(e)

        cls.scanned_ips += 1
        return random_ip
    
    
    @classmethod
    def _random_ip_validator(cls, ports, timeout=3, verbose=False):
        """This will validate random ip"""



        # COLORS
        c1 = "bold red"
        c2 = "bold yellow"
        c3 = "bold blue"
        c4 = "bold green"

        
        ip = Mass_IP_Scanner._generate_random_ip(verbose=False)
        if not cls.scan: return False



        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            
            try:
                

                for port in ports:
                    s.settimeout(timeout)
                    result = s.connect_ex((ip, int(port)))

                    if result == 0:

                        with LOCK:
                            cls.current_ips.append(ip)
                            cls.online_ips += 1
                            console.print(f"\n[{c4}][+] Active IP:[/{c4}] [{c2}]{ip}[/{c2}]:{port}")

                            if cls.lookup: Mass_IP_Scanner._snatch_geo_info(ip=ip, setup=True)
                            Mass_IP_Scanner._parse_header(ip=ip, port=port) 
                            ##
                            #Database._snatch_path(ip=ip, CONSOLE=console)
    
                        return ip

                return False


            except Exception as e: console.print(f"[bold red]Exception Error:[bold yellow] {e}"); return False
    
    
    @classmethod
    def _parse_header(cls, ip, port, timeout=3):
        """This will be used to parse the header of response for http/https only"""


        url = f"http://{ip}:{port}"


        paths               = Database.paths
        server_signatures   = Database.server_signatures
        www_auth_signatures = Database.www_auth_signatures
        html_signatures     = Database.html_signatures
        
        

        #Database._check_paths(ip=ip, CONSOLE=console)


        #return 
        try:

            #print("fedsf")


            if port in [80,443,8080]:
            
                response = requests.get(url=url, timeout=timeout)
                headers = response.headers
                
                if response.status_code in [200,204]:
                    
                    server = headers.get("Server", False)
                    x_powered_by = headers.get("X-Powered-By", False)
                    content_type = headers.get("Content-Type", False)
                    location = headers.get("Location", False)
                    
                    
                    console.print(server, x_powered_by, url)
            

            elif port in Database.DATABASE_PORTS:

                
                #Database._check_database(ip=ip, port=port, CONSOLE=console)

                if response.status_code in [200,204]:

                    server = headers.get("Server", False)
                    x_powered_by = headers.get("X-Powered-By", False)
                    content_type = headers.get("Content-Type", False)
                    location = headers.get("Location", False)
                    
                    
                    console.print(server, x_powered_by, url)
            






        
        except Exception as e: 
            #return
            console.print(f"[bold red][-] Exception Error:[bold yellow] {e}")



    @classmethod
    def _snatch_geo_info(cls, ip, timeout=3, setup=True, verbose=False):
        """This method will be responsible for grabbing the geo info on said ip"""

        # COLORS
        c1 = "bold red"
        c2 = "bold yellow"
        c3 = "bold blue"
        c4 = "bold green"
        c5 = "white"
        space = "    "
        

        if cls.api_key_ipinfo:

            api_key =  cls.api_key_ipinfo   
            url     = f"https://ipinfo.io/{ip}/json/?token={api_key}"
        
        else: url   =  f"https://ipinfo.io/{ip}/json"



        try:

            response = requests.get(url=url, timeout=timeout,)
            data = response.json()
            text = response.text


            if response.status_code in [200,204]:

                if verbose: console.print(data)

                country   = data.get("country",  False)  
                region    = data.get("region",   False)
                city      = data.get("city",     False)
                org       = data.get("org",      False)
                postal    = data.get("postal",   False)
                timezone  = data.get("timezone", False)


                console.print(
                    f" [{c4}]{space}[+] Country:[{c5}] {country}"
                    f"\n [{c4}]{space}[+] region:[{c5}] {region}"
                    f"\n [{c4}]{space}[+] city:[{c5}] {city}"
                    f"\n [{c4}]{space}[+] org:[{c5}] {org}"
                    f"\n [{c4}]{space}[+] postal:[{c5}] {postal}"
                    f"\n [{c4}]{space}[+] timezone:[{c5}] {timezone}"
                )
            

            else:

                console.print(f" [{c1}]{space}[-] IPInfo Lookup Failed :[{c5}] {text}")
        

        except Exception as e: console.print(f"[bold red][-] Exception Error:[bold yellow] {e}")

    

    @classmethod
    def _ip_threader(cls, ports, max_workers=250, timeout=1):
        """This will start a multi-proccess thread"""

        # COLORS
        c1 = "bold red"
        c2 = "bold yellow"
        c3 = "bold blue"
        c4 = "bold green"
        c5 = "white"

        futures = set()
        last_save = time.time()
        panel = Panel(renderable="[bold red]Mass IP Scanner", border_style="bold purple", expand=False)


        try: max_workers = int(max_workers)
        except Exception: max_workers = 250

        try: portz  = [int(port) for port in ports.split(',')]; console.print(portz) 
        except Exception: portz = list(ports); console.print(ports)      


        
        with Live(panel, console=console, refresh_per_second=4):
            with ThreadPoolExecutor(max_workers=max_workers) as executor:

                try:
                
                    while cls.scan:

                        if len(futures) < max_workers: 

                            future = executor.submit(Mass_IP_Scanner._random_ip_validator, portz, timeout)
                            futures.add(future)
                            panel.renderable = (f"[{c1}]Active IPs: [{c2}]{cls.online_ips} / {cls.scanned_ips}  -  [{c1}]Port(s): [{c2}]{portz}  -  [{c1}]Max Workers:[{c2}] {max_workers}  -  Developed by NSM Barii")
                            
                        
                        with LOCK:
                            if time.time() - last_save > 10 and cls.save:
                                File_Saver._push_ips_found(data=cls.current_ips, CONSOLE=console, verbose=True)
                                cls.current_ips = []
                                last_save = time.time()
   

                        done = {f for f in futures if f.done()}
                        futures -= done

                except KeyboardInterrupt as e: console.print("[bold red][-] Killing ALL Threds...."); cls.scan=False
                except Exception as e: console.print(f"[bold red]Exception Error:[bold yellow] {e}"); cls.scan=False; exit()


    @classmethod
    def _main(cls, port, threads):
        """This will run class wide code"""

        
        cls.scan = True
        cls.scanned_ips = 0 
        cls.online_ips  = 0
        cls.current_ips = []


        if not port:
            port = console.input("\n[bold yellow]Enter port to mass scan for!: ") or 80
            threads = console.input("[bold yellow]Enter Thread count!: ") or 250; print('\n')

        Mass_IP_Scanner._ip_threader(ports=port, max_workers=threads or 250)


if __name__ =="__main__":
    Mass_IP_Scanner._main()