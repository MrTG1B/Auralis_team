import back_end.data_base as dbdb
from datetime import datetime
import threading
import json
import pickle
import sqlite3
# from Data_Base.flask_server_ip import ip_get_server, shutdown_server,get_server_ips



current_year = datetime.now().year
current_month = datetime.now().month

table_name = dbdb.create_table_for_month(year=current_year,month=current_month)
def ip_input(lp_n, lp_ip,en=0 ,in_d=datetime.now().date().strftime("%d-%m-%Y"), man_d='00-00-0000', table_name=table_name):
    search = dbdb.search_data(table_name, 'IPAddress', lp_ip)
    # print(search)
    if not search:
        dbdb.insert_light_post(lp_n, lp_ip, en, in_d,man_d,table_name)
        
def add_ip(no_of_lp):
    # server_th = threading.Thread(target=ip_get_server)
    # server_th.start()
    ip_dict={}
    try:
        with open('Data_Base/no_of_light_post.txt', 'w') as file:
            file.write(str(no_of_lp))
    except Exception as e:
        print(f"Error writing to file: {e}")

    lp_n_ip = 'Data_Base/lp_n_ip.json'
    try:
        with open(lp_n_ip, 'r') as w_file:
            ip_dict = json.load(w_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(e)
        # ip_dict = {}

    sorted_dict = dict(sorted(ip_dict.items(), key=lambda x: int(x[0][3:])))            
    while len(ip_dict) <=no_of_lp:
        #,cursor=cursor,conn=conn,table_name=table_name

        try:
            with open(lp_n_ip, 'r') as w_file:
                ip_dict = json.load(w_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(e)
            # ip_dict = {}

        sorted_dict = dict(sorted(ip_dict.items(), key=lambda x: int(x[0][3:])))
        for name, ip in sorted_dict.items():
            ip_input(lp_n=name, lp_ip=ip)
        if (len(sorted_dict))==no_of_lp:
            break
    with open(lp_n_ip, 'w') as json_file:
        json.dump(sorted_dict, json_file)
    
def data_get(id_of_data, ip):
    """
    Retrieve data based on the provided ID of the data and IP address.

    Parameters:
    - id_of_data (int): The ID of the data to retrieve.
    (1-ID of the row,2-L/P name,3-IP address,4-Energy,5-Date of intallation,6-Date of Maintenance)
    - ip (str): The IP address of the lightpost that you want get data.

    Returns:
    - str: The retrieved data if found, or an error message if not found.
    """
    conn = sqlite3.connect('Data_Base/light_posts.db')
    cursor = conn.cursor()
    search = dbdb.search_data(table_name, 'IPAddress', str(ip),new_cursor=cursor)
    
    if not search:
        cursor.close()
        conn.close()
        return "No IP address found"
    elif id_of_data <= 0:
        cursor.close()
        conn.close()
        return "Invalid data ID"
    else:
        cursor.close()
        conn.close()
        search_result=search[0]
        return search_result[id_of_data - 1]
    
def data_update(id_of_data, ip,value):
    """
    Updates the database data based on the provided ID of the data and IP address.

    Parameters:
    - id_of_data (int): The ID of the data to be updated.
    (1-ID of the row,2-L/P name,3-IP address,4-Energy,5-Date of intallation,6-Date of Maintenance)
    - ip (str): The IP address of the lithpost that you want to update.
    -value(str):The new data.

    Returns:
    - str: If the data was updated or any error ocured
    """
    conn = sqlite3.connect('Data_Base/light_posts.db')
    cursor = conn.cursor()
    search=dbdb.search_data(table_name, 'IPAddress', str(ip),new_cursor=cursor)
    if not search:
        cursor.close()
        conn.close()
        return "No IP address found"
    elif id_of_data <= 0 or id_of_data > len(search[0]):
        cursor.close()
        conn.close()
        return "Invalid data ID"
    else:
        search_result = search[0]
        dbdb.edit_light_post(int(value) if id_of_data==1 else search_result[0],
                             value if id_of_data==2 else search_result[1],
                             value if id_of_data==3 else search_result[2],
                             float(value) if id_of_data==4 else search_result[3],
                             value if id_of_data==5 else search_result[4],
                             value if id_of_data==6 else search_result[5],table_name,new_cursor=cursor,new_conn=conn)
        conn.commit()
        cursor.close()
        conn.close()
        return "Data updated Successfully"

def delete_table():
    dbdb.delete_light_posts(table_name)

# def get_the_server_ip():
#     get_server_ips()    
# add_ip(2)