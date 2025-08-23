import requests

timeout=1
def get_current(ip_list):
    current_list=[]
    for ips in ip_list:
        try:
            current_response= requests.get(f"http://{ips}/cs",timeout=timeout)
            current_list.append(float(current_response.text))
        except requests.RequestException as e:
            current_list.append(0.0)
    return current_list

def get_energy(ip_list):
    energy_list=[]
    for ips in ip_list:
        try:
            energy_response= requests.get(f"http://{ips}/en",timeout=timeout)
            energy_list.append(float(energy_response.text))
        except requests.RequestException as e:
            energy_list.append(0.0)
    return energy_list