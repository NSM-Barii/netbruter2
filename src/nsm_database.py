# THIS WILL HOUSE UTILITIES AND OR FILES

# UI IMPORTS
from rich.console import Console


# ETC IMPORTS
from pathlib import Path
import json


console = Console()




class Database():
    """This will hold database values"""



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