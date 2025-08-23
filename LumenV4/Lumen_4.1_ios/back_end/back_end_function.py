import json
import back_end.data as bd
import back_end.nebor_lp_control as nlp
from datetime import datetime

def get_area_list()->list:
    with open("data.json", 'r') as w_file:
        ip_dict = json.load(w_file)
    a_list=list(ip_dict.keys())
    return a_list,ip_dict

road_name=get_area_list()[0][0]
user_date = datetime.strptime(get_area_list()[1][road_name]['lp_date_install'][0], '%d/%m/%Y').date()
current_date = datetime.now().date()
date_diff = (current_date - user_date)
print(date_diff)
till_date_energy_consumed = round(date_diff.days *(8.64/1000), 2)
en_list = []
for i in range(5):
    en_list.append(str(till_date_energy_consumed))
with open("data.json", 'r') as w_file:
    ip_dict = json.load(w_file)
a_list=list(ip_dict.keys())
ip_dict[a_list[0]]["lp_energy_consumed"]=en_list
with open("data.json", 'w') as w_file:
    json.dump(ip_dict, w_file)


def get_ip():
    with open("data.json", 'r') as w_file:
        ip_dict = json.load(w_file)
    a_list=list(ip_dict.keys())
    ip_list=ip_dict[a_list[0]]["lp_ip"]
    return ip_list

def save_dict(value_list):
    with open("data.json", 'r') as w_file:
        ip_dict = json.load(w_file)
    a_list=list(ip_dict.keys())
    ip_dict[a_list[0]]["lp_current"]=value_list
    with open("data.json", 'w') as w_file:
        json.dump(ip_dict, w_file)

def run_in_bg(flag):
    while not flag.is_set():
        ip_list=get_ip()
        current_list=bd.get_current(ip_list)
        save_dict(current_list)
        nlp.back_lp_run(ip_list)
