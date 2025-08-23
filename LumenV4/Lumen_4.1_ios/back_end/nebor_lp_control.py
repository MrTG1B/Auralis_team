import requests

timeout=4
def back_lp_run(esp):
    for i in range(len(esp)):
        try:
            res1 = requests.get(f"http://{esp[i]}/ir", timeout=timeout)
            rt1 = int(res1.content.decode('utf-8'))
            #print(rt1)
            if rt1==1:
                # a=requests.get(f"http://{esp[i]}/led/on", timeout=timeout_on)
                #print(a.text)
                # if i!=1 and i!=len(esp):
                #     requests.get(f"http://{esp[i-1]}/led/on", timeout=timeout_on)
                #     requests.get(f"http://{esp[i+1]}/led/on", timeout=timeout_on)
                if i>1:
                    # requests.get(f"http://{esp[i-1]}/led/on", timeout=timeout)
                    requests.get(f"http://{esp[i+1]}/led/on", timeout=timeout) 
                if i<len(esp):
                    requests.get(f"http://{esp[i-1]}/led/on", timeout=timeout)
                    # requests.get(f"http://{esp[i+1]}/led/on", timeout=timeout) 
            # if rt1==0:
            #     #for i in range(len(esp)):
            #         requests.get(f"http://{esp[i]}/led/off", timeout=timeout) 
            #         if i>0:
            #             requests.get(f"http://{esp[i-1]}/led/off", timeout=timeout)
            #         elif i<len(esp)-1:
            #             requests.get(f"http://{esp[i+1]}/led/off", timeout=timeout)
        except requests.RequestException as e:
            print(f"IR 404 could not connect : {e}") 
    