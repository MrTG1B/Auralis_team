import customtkinter as ctk
import json
import pickle
import front_end.ctkMeter as ctkm
import back_end.middle_man as mm
import back_end.weather as weather
import back_end.back_end_function as bef
from PIL import Image
from datetime import date,datetime

# current_weather=weather.weather_current()['current']
current_air=weather.current_air_quality()['list'][0]['main']
THEME_PATH='front_end/text_file/theme.txt'
f_lp_filename = 'fault_list.pkl'

def get_area_list()->list:
    with open("data.json", 'r') as w_file:
        ip_dict = json.load(w_file)
    a_list=list(ip_dict.keys())
    return a_list,ip_dict

def update_button(i):
    with open(f_lp_filename, 'rb') as file:
        faulty_lp_list= pickle.load(file)
    global variable_details_arr
    global lp_button_arr
    global lp_details_label_arr
    road_name=get_area_list()[0][i]
    lp_name_list=get_area_list()[1][road_name]['lp_name']
    for label in variable_details_arr:
        index=variable_details_arr.index(label)
        if faulty_lp_list[index] == 0 or faulty_lp_list[index] == 404:
            lp_details_label_arr[index].pack_forget()
            lp_button_arr[index].configure(state='disabled',
                                           fg_color='#FF5454',
                                           text=f"{lp_name_list[index]}\n⛔Faulty Light Post"
                                           )
        else:
            lp_button_arr[index].configure(state='normal',
                                           fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0],
                                           text=f"{lp_name_list[index]}"
                                           )

def auto_update_data(root,i):
    with open(f_lp_filename, 'rb') as file:
        faulty_lp_list= pickle.load(file)
        
    global variable_details_arr
    global lp_details_label_arr
    road_name=get_area_list()[0][i]
    lp_name_list=get_area_list()[1][road_name]['lp_name']
    current_list=get_area_list()[1][road_name]['lp_current']
    print(current_list)
    for label in variable_details_arr:
        index=variable_details_arr.index(label)
        print(index)
        cur=current_list[index]
        print(cur)
        if faulty_lp_list[index] == 404:
            vol=0
        else:
            vol=12
        label.configure(text=f"Light Post Number: {lp_name_list[index]}\nCurrent: {cur} A\nVoltage: {vol} V\nPower: {vol*cur} W\nEnergy Consumed: {get_area_list()[1][road_name]['lp_energy_consumed'][index]} units",)
    root.after(1000,lambda:auto_update_data(root,i))

def air_quality(frame):
    
    heading_la=ctk.CTkLabel(frame,text='Air Quality',font=("Roboto",15,"underline","bold"))
    heading_la.pack(side='top')
    
    temp_label=ctk.CTkLabel(frame,text=f"Temperature :{current_weather['temperature']}\u00b0C ")
    temp_label.pack(side='top',padx=10,pady=5,anchor='w')
    
    rel_humi=ctk.CTkLabel(frame,text=f"Relative Humidity: {current_weather['humidity']}%")
    rel_humi.pack(side='top',padx=10,pady=5,anchor='w')
    
    bio_pressure=ctk.CTkLabel(frame,text=f"Biometric Pressure: {current_weather['pressure']} millibar")
    bio_pressure.pack(side='top',padx=10,pady=5,anchor='w')
    
    # gas_res=ctk.CTkLabel(frame,text='Gas Resistance: ')
    # gas_res.pack(side='top',padx=10,pady=5,anchor='w')
    
    aiq=ctk.CTkLabel(frame,text=f"Air Quality Index: {current_air['aqi']}")
    aiq.pack(side='top',padx=10,pady=5,anchor='w')

def solar_detials(frame):
    heading_la=ctk.CTkLabel(frame,text='Solar Details',font=("Roboto",15,"underline","bold"))
    heading_la.pack(side='top')
    
    total_solar_produc=ctk.CTkLabel(frame,text=f"Total Soalar Pannel Production: 10 kW")
    total_solar_produc.pack(side='top',padx=10,pady=5,anchor='w')
    
    total_power_consum=ctk.CTkLabel(frame,text=f"Total Power Consumed: 9.4 kW ")
    total_power_consum.pack(side='top',padx=10,pady=5,anchor='w')
    
    total_no_light=ctk.CTkLabel(frame,text=f"Total No. of Light Posts: 10")
    total_no_light.pack(side='top',padx=10,pady=5,anchor='w')
    
    av_battery_per=ctk.CTkLabel(frame,text=f"Average Battery Percetage: 80%")
    av_battery_per.pack(side='top',padx=10,pady=5,anchor='w')
    
def lp_list_creator(list_frame,i,light_post_detail_frame):
    cur=1
    vol=12
    road_name=get_area_list()[0][i]
    global variable_details_arr
    global lp_button_arr
    global lp_details_label_arr
    variable_details_arr=[]
    lp_button_arr=[]
    lp_details_label_arr=[]
    def toogle_lable(i):
        for label in lp_details_label_arr:
            label.pack_forget()
        lp_details_label_arr[i].pack(side='top',expand=True,fill='both',pady=10,padx=10)
    
    
    
    for lp_name in get_area_list()[1][road_name]['lp_name']:
        lp_ind=get_area_list()[1][road_name]['lp_name'].index(lp_name)
        fr=ctk.CTkFrame(list_frame)
        fr.pack(side='top',fill='x',pady=5)
        button=ctk.CTkButton(fr,
                             text=lp_name,
                             command=lambda i=lp_ind:toogle_lable(i),
                             text_color_disabled='black',
                             )
        button.pack(side='top',pady=5)
        lp_button_arr.append(button)
        lp_details_frame=ctk.CTkFrame(light_post_detail_frame)
        lp_details_frame.pack_forget()
        variable_details=ctk.CTkLabel(lp_details_frame,
                                      text=f"Light Post Number: {lp_name}\nCurrent: {cur} A\nVoltage: {vol} V\nPower: {vol*cur} W\nEnergy Consumed: {get_area_list()[1][road_name]['lp_energy_consumed'][lp_ind]} units",
                                      font=('Helvetica',13),
                                      justify='left',
                                      anchor='w',
                                      )
        variable_details.pack(side='left',ipadx=5,expand=True)
        variable_details_arr.append(variable_details)
        
        static_details=ctk.CTkLabel(lp_details_frame,
                                      text=f"IP Address: {get_area_list()[1][road_name]['lp_ip'][lp_ind]}\nDate of Installation: {get_area_list()[1][road_name]['lp_date_install'][lp_ind]}\nLast Maintaince Date: --/--/----",
                                      font=('Helvetica',13),
                                      justify='left',
                                      anchor='e',
                                      )
        static_details.pack(side='right',ipadx=5,expand=True)
        
        lp_details_label_arr.append(lp_details_frame)

def interface(main_frame,i):
    # ttk.autostyle(False)
    frame=ctk.CTkFrame(main_frame)
    frame.pack(expand=True,fill='both')
    l_frame=ctk.CTkFrame(frame)
    l_frame.pack(side='left',fill='y',pady=10,padx=10)
    # road_name=ctk.CTkLabel(l_frame,text=f"{get_road_list()[i]}",font=('Times',15))
    # road_name.pack(side='top',padx=10,pady=5,fill='x')
    list_frame=ctk.CTkScrollableFrame(l_frame,label_text="List of All the Light Posts")
    list_frame.pack(side='top',fill='both',expand=True,padx=10,pady=5)
    
    
    
    r_frame=ctk.CTkFrame(frame)
    r_frame.pack(side='right',expand=True,padx=10,pady=10,fill='both')
    
    road_name=get_area_list()[0][i]
    energy_u=sum(float(x) for x in get_area_list()[1][road_name]["lp_energy_consumed"])
    
    user_date = datetime.strptime(get_area_list()[1][road_name]['lp_date_install'][0], '%d/%m/%Y').date()
    current_date = datetime.now().date()
    date_diff = ((current_date - user_date).days)
    trad_till_date_energy_consumed = round(date_diff *0.0144, 2)*5
    # print(trad_till_date_energy_consumed)
    # print(energy_u)
    energy_s=round(trad_till_date_energy_consumed-energy_u,2)
    # print(energy_s)
    energy_saved_meter=ctkm.Meter(r_frame,
                                  value=energy_s,
                                  max_amount=200,
                                  progress_color='green',
                                  meter_label_text="Energy saved",
                                  suffix_text="kWh",
                                  )
    #ttk.Meter(energy_saved_frame,subtext=f'L/P{i+1}',#f"         L/P{i+1}\nEnergy Consumed",
                     #nteractive=False,textright="kWh",metertype='full',stripethickness=10,metersize=200,amountused=energy,subtextstyle="success")
    energy_saved_meter.grid(row=0,column=0,padx=10,pady=5)
    
    
    energy_used_meter=ctkm.Meter(r_frame,
                                 value=float("{:.2f}".format(float(energy_u))),
                                 max_amount=200,
                                 progress_color='red',
                                 meter_label_text="Energy used",
                                 suffix_text="kWh",
                                 )
    energy_used_meter.grid(row=0,column=1,padx=10,pady=5)
    
    air_quality_other_details_frame=ctk.CTkFrame(r_frame,width=410,height=260)
    air_quality_other_details_frame.grid(row=0,column=2,padx=10,pady=5)
    air_quality_other_details_frame.propagate(False)
    
    # air_quality(air_quality_other_details_frame)
    
    # air_quaity_detail_label=ctk.CTkLabel(air_quality_other_details_frame,text="Air Quality Details Here...",font=('Times',30))
    # air_quaity_detail_label.pack(expand=True,fill='both')
    
    light_post_detail_frame=ctk.CTkFrame(r_frame,width=540,height=280)
    light_post_detail_frame.grid(row=1,column=0,columnspan=2,rowspan=2,padx=10,pady=5)
    light_post_detail_frame.propagate(False)
    heading=ctk.CTkLabel(light_post_detail_frame,text="Light Post Details",font=("Roboto",15,"underline","bold"),justify='left',anchor='w')
    heading.pack(side='top',fill='x',padx=5,pady=5)
    lp_list_creator(list_frame,i,light_post_detail_frame)
    # light_post_detail_label=ctk.CTkLabel(light_post_detail_frame,text="Light Post Details Here...",font=('Times',30))
    # light_post_detail_label.pack(expand=True,fill='both')
    
    solar_details_frame=ctk.CTkFrame(r_frame,width=410,height=280)
    solar_details_frame.grid(row=1,column=2,padx=10,pady=5)
    solar_details_frame.propagate(False)
    
    # solar_detials_label=ctk.CTkLabel(solar_details_frame,text="Solar Details Here...",font=('Times',30))
    # solar_detials_label.pack(expand=True,fill='both')
    solar_detials(solar_details_frame)
    auto_update_data(frame,i)
    
    
    
    
    # bef.run_in_bg()
    
    