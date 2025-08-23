import customtkinter as ctk
# import ttkbootstrap as ttk
import front_end.ctkMeter as ctkm
# import front_end.ctk_meter as ttk
import back_end.middle_man as mm
from PIL import Image

THEME_PATH='front_end/text_file/theme.txt'

def get_road_list():
    a_list=["ROAD 1","ROAD 2","ROAD 3","ROAD 4","Biswa Bangla Sarani"]
    return a_list

def interface(main_frame,i):
    # ttk.autostyle(False)
    frame=ctk.CTkFrame(main_frame)
    frame.pack(expand=True,fill='both')
    l_frame=ctk.CTkFrame(frame)
    l_frame.pack(side='left',fill='y',pady=10,padx=10)
    road_name=ctk.CTkLabel(l_frame,text=f"{get_road_list()[i]}",font=('Times',15))
    road_name.pack(side='top',padx=10,pady=5,fill='x')
    list_frame=ctk.CTkScrollableFrame(l_frame,label_text="List of All the Light Posts")
    list_frame.pack(side='top',fill='both',expand=True,padx=10,pady=5)
    
    r_frame=ctk.CTkFrame(frame)
    r_frame.pack(side='right',expand=True,padx=10,pady=10,fill='both')
        
    energy_s=120
    energy_saved_meter=ctkm.Meter(r_frame,
                                  value=energy_s,
                                  max_amount=200,
                                  progress_color='green',
                                  meter_label_text="Energy saved",
                                  suffix_text="kWh",
                                  )
    #ttk.Meter(energy_saved_frame,subtext=f'L/P{i+1}',#f"         L/P{i+1}\nEnergy Consumed",
                     #nteractive=False,textright="kWh",metertype='full',stripethickness=10,metersize=200,amountused=energy,subtextstyle="success")
    energy_saved_meter.grid(row=0,column=0,padx=10,pady=10)
    
    energy_u=80
    energy_used_meter=ctkm.Meter(r_frame,
                                 value=energy_u,
                                 max_amount=200,
                                 progress_color='red',
                                 meter_label_text="Energy used",
                                 suffix_text="kWh",
                                 )
    energy_used_meter.grid(row=0,column=1,padx=10,pady=10)
    
    
    