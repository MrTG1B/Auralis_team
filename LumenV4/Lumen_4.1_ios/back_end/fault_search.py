import requests
import pickle
ct=0.12
vt=12
timeout=1

espip_filename = 'fault_list.pkl'

def fault_check(espip):
    fault=[]
    for esp in espip:
        try:
            response=requests.get(f"http://{esp}/fss",timeout=timeout)
            fault.append(int(response.text))
        except requests.RequestException as e:
            fault.append(int(404))
    with open(espip_filename,'wb') as file:
        pickle.dump(fault, file)