import random
import datetime
import time
import os

SERVER_LOG_FILE = ("C:/Users/hp/Desktop/PROGRAMMING LANGUAGES/Ai_Log_Analyzer/server.log")

SERVER_JSON_FILE = ("C:/Users/hp/Desktop/PROGRAMMING LANGUAGES/Ai_Log_Analyzer/server.json")

IPS = ['192.168.1.10', '192.168.1.11', '10.0.0.5', '172.16.0.4', '192.168.1.250']
ENDPOINTS=['/home','/about','/dashboard','/login','/checkout','/api/data']
STATUS_CODES=[200,201,400,403,404,500]
METHODS=['GET','POST','PUT','PATCH','DELETE']
TIMES = ['0.1','0.2','0.3','0.7','0.9','1.9','1.4']

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m" 

def color_status_code(status_code):
    if status_code == 200:
        return f"{GREEN}200{RESET}"
    elif status_code == 400:
        return f"{RED}400{RESET}"
    elif status_code == 404:
        return f"{RED}404{RESET}"
    elif status_code == 500:
        return f"{RED}500{RESET}"
    elif status_code == 201:
        return f"{GREEN}201{RESET}"
    elif status_code == 403:
        return f"{YELLOW}403{RESET}"
    elif status_code == 401:
        return f"{RED}401{RESET}"
    return str(status_code)

def main():
    with open(SERVER_LOG_FILE, 'a') as f:
        while True:
            DATE = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            STATUS = random.choice(STATUS_CODES)
            IPS_CHOICE = random.choice(IPS)
            METHODS_CHOICE = random.choice(METHODS)
            ENDPOINTS_CHOICE = random.choice(ENDPOINTS)
            TIMES_CHOICE = random.choice(TIMES)
            
            colored_status = color_status_code(STATUS)
            
            f.write(f"{DATE}||{IPS_CHOICE} || {METHODS_CHOICE} || {ENDPOINTS_CHOICE} || STATUS = {STATUS} || TIME = {TIMES_CHOICE}\n")
            f.flush()  
            print(f"{DATE} || {IPS_CHOICE} || {METHODS_CHOICE} || {ENDPOINTS_CHOICE} || STATUS = {colored_status} || TIME = {TIMES_CHOICE}")

            if STATUS == 200:
                f.write("OK!\n")
                print(f"{GREEN}OK!{RESET}")
            elif STATUS == 400:
                f.write("This is an ERROR!\n")
                print(f"{RED}This is an ERROR!{RESET}")
            elif STATUS == 500:
                f.write("Internal Server Error\n")
                print(f"{RED}Internal Server Error{RESET}")
            elif STATUS == 201:
                f.write("Success\n")
                print(f"{GREEN}Success{RESET}")
            elif STATUS == 403:
                f.write("ERROR\n")
                print(f"{RED}ERROR{RESET}")    
            elif STATUS == 404:
                f.write("NOT FOUND!\n")
                print(f"{YELLOW}NOT FOUND!{RESET}")
            time.sleep(1.3)



if __name__ == "__main__":
    main()