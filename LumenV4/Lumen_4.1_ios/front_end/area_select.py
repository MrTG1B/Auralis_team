import customtkinter as ctk
from PIL import Image
import json
from datetime import datetime
import front_end.fault_list as fl
import front_end.settings as set
import front_end.dashboard as dash

# FG_COLOR='#F2F2F2'
# FRAME_FG_COLOR='white'
# BUTTON_FG_COLOR='transparent'
# BUTTON_DISABLED_FG_COLOR='#406B5C'
# TEXT_COLOR='black'
# DISABLED_TEXT_COLOR='gray'

global MAINTENANCE_LIST
MAINTENANCE_LIST=[]
global OLD_MAINT_LIST
OLD_MAINT_LIST=[]
THEME_COL_PATH="front_end/text_file/theme_color.txt"

setting_dict={
        1:{
            'name':'Personalisation',
            'path':'assets/per_icon.png'
        },
        2:{
            'name':'Account',
            'path':'assets/acc_icon.png'
        },
        3:{
            'name':'Add New Road',
            'path':'assets/loc_add.png'
        }
    }

def update_datetime_label(time_label,date_label,root):
    time_label.lift()
    date_label.lift()
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%d-%m-%Y")
    date_label.configure(text=f'Date: {formatted_date}')
    formatted_time = current_datetime.strftime("%I:%M:%S %p")
    time_label.configure(text=f'Time: {formatted_time}')
    root.after(1000,lambda: update_datetime_label(time_label,date_label,root)) 


def get_area_list():
    with open("data.json", 'r') as w_file:
        ip_dict = json.load(w_file)
    a_list=list(ip_dict.keys())
    return a_list

def button_state_check():
    global OLD_MAINT_LIST,MAINTENANCE_LIST
    global area_button_list
    global fault_button_list
    if OLD_MAINT_LIST!=MAINTENANCE_LIST:
        OLD_MAINT_LIST=MAINTENANCE_LIST.copy()
        for button in area_button_list:
            if area_button_list.index(button) in MAINTENANCE_LIST:
                button.configure(state='disabled',
                                 fg_color='#406B5C',
                                 text=f"{get_area_list()[area_button_list.index(button)]}\nMaintaince Mode is on🔒")
            else:
                button.configure(state='normal',
                                 fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0],
                                 text=f"{get_area_list()[area_button_list.index(button)]}")
        for button in fault_button_list:
            if fault_button_list.index(button) in MAINTENANCE_LIST:
                button.configure(state='disabled',
                                 fg_color='#406B5C',
                                 text=f"{get_area_list()[fault_button_list.index(button)]}\nMaintaince Mode is on🔒")
            else:
                button.configure(state='normal',
                                 fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0],
                                 text=f"{get_area_list()[fault_button_list.index(button)]}")
    area_button_list[0].after(100,button_state_check)

def back_operation(cal_buttons_frame,area_frame_list,content_frame)->None:
    for i in area_frame_list:
        i.place_forget()
    content_frame.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.7,anchor='center')
    cal_buttons_frame.pack(expand=True,fill='both')

def toogle_frame(frame,cal_buttons_frame,content_frame,area_frame_list,s=0)->None:
    if s==0:
        content_frame.place(relx=0.5,rely=0.5,relwidth=1,relheight=1,anchor='center')
    else:
        content_frame.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.7,anchor='center')
    cal_buttons_frame.pack_forget()
    for i in area_frame_list:
        i.place_forget()
    if s==0:
        frame.place(relx=0.5,rely=0.5,relwidth=1,relheight=1,anchor='center')#pack(side='top',fill='both',expand=True)
    else:
        frame.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.7,anchor='center')
    frame.propagate(True)

def frame_maker(root,area_list,area_frame,area_button_frame,content_frame,s=0):
    area_frame_list=[]
    area_button_list=[]
    if s==0:
        for i in range(len(area_list)):
            frame=ctk.CTkFrame(root,
                               height=area_frame.winfo_height(),
                               )
            frame.place_forget()
            top_frame=ctk.CTkFrame(frame,)
            top_frame.pack(side='top',fill='x')
            back_button=ctk.CTkButton(top_frame,width=25,height=25,font=('Times',30),
                                    text="🔙",
                                    command=lambda:back_operation(area_button_frame,area_frame_list,content_frame))
            back_button.pack(side='left',padx=15,pady=10)
            
            button_image=ctk.CTkImage(light_image=Image.open('assets/road.png'),dark_image=Image.open('assets/road.png'),size=(30,30))
            
            road_name_label=ctk.CTkLabel(top_frame,text=f"  {area_list[i]}",font=('Times',25,'bold'),
                                         image=button_image,compound='left')
            road_name_label.place(relx=0.5,rely=0.5,anchor='center')
            
            area_frame_list.append(frame)
            
            # button_image=ctk.CTkImage(light_image=Image.open('assets/road.png'),dark_image=Image.open('assets/road.png'),size=(30,30))
            buttons=ctk.CTkButton(area_button_frame,
                                  command=lambda frame=frame:toogle_frame(frame,area_button_frame,content_frame,area_frame_list),
                                text=f"{area_list[i]}",
                                text_color='black',
                                image=button_image,
                                state='normal',
                                font=('Arial',15),
                                text_color_disabled='white')
            buttons.pack(side='top',expand=True,fill='x',padx=10,pady=10)
            area_button_list.append(buttons)
            MAINTENANCE_LIST.append(404)
    elif s==1:
        for i in range(len(area_list)):
            frame=ctk.CTkFrame(root,height=area_frame.winfo_height())
            frame.place_forget()
            top_frame=ctk.CTkFrame(frame)
            top_frame.pack(side='top',fill='x')
            back_button=ctk.CTkButton(top_frame,text="🔙",width=25,height=25,
                                    command=lambda:back_operation(area_button_frame,area_frame_list,content_frame),
                                    font=('Times',30))
            back_button.pack(side='left',padx=15,pady=10)
            
            area_frame_list.append(frame)
            
            button_image=ctk.CTkImage(light_image=Image.open(setting_dict[i+1]["path"]),dark_image=Image.open(setting_dict[i+1]["path"]),size=(30,30))
            buttons=ctk.CTkButton(area_button_frame,
                                  command=lambda frame=frame:toogle_frame(frame,area_button_frame,content_frame,area_frame_list,1),
                                text=setting_dict[i+1]["name"],state='normal',image=button_image,font=('Arial',15),
                                text_color_disabled='#c73126')
            buttons.pack(side='top',expand=True,fill='x',padx=10,pady=10)
            area_button_list.append(buttons)
    elif s==2:
        for i in range(len(area_list)):
            frame=ctk.CTkFrame(root,height=area_frame.winfo_height())
            frame.place_forget()
            top_frame=ctk.CTkFrame(frame)
            top_frame.pack(side='top',fill='x')
            back_button=ctk.CTkButton(top_frame,text="🔙",width=25,height=25,
                                    command=lambda:back_operation(area_button_frame,area_frame_list,content_frame),
                                    font=('Times',30))
            back_button.pack(side='left',padx=15,pady=10)
            
            area_frame_list.append(frame)
            
            button_image=ctk.CTkImage(light_image=Image.open("assets/faulty_road.png"),dark_image=Image.open("assets/faulty_road.png"),size=(30,30))
            buttons=ctk.CTkButton(area_button_frame,
                                  command=lambda frame=frame:toogle_frame(frame,area_button_frame,content_frame,area_frame_list,1),
                                text_color='black',
                                image=button_image,
                                state='normal',
                                font=('Arial',15),
                                text_color_disabled='white')
            buttons.pack(side='top',expand=True,fill='x',padx=10,pady=10)
            area_button_list.append(buttons)
    return area_button_list,area_frame_list
        
def area_buttons_interface(root,content_frame,area_button_frame,area_frame):
    global OLD_MAINT_LIST,MAINTENANCE_LIST
    global area_button_list
    area_list=get_area_list()
    area_button_list,area_frame_list=frame_maker(root,area_list,area_frame,area_button_frame,content_frame)
    for area_frame in area_frame_list:
        dash.interface(area_frame,area_frame_list.index(area_frame))

def fault_buttons_interface(root,content_frame,fault_button_frame,fault_frame):
    global OLD_MAINT_LIST,MAINTENANCE_LIST
    global fault_button_list
    fault_list=get_area_list()
    fault_button_list,fault_frame_list=frame_maker(root,fault_list,fault_frame,fault_button_frame,content_frame,2)
    for fault_frame in fault_frame_list:
        fl.interface(fault_frame,fault_frame_list.index(fault_frame))
        # dash.interface(area_frame,area_frame_list.index(area_frame))

def maint_buttons_interface(maint_button_frame):
    maint_button_frame.configure(label_text="Road Name\t\t\t\tMaintaince Mode")
    area_list=get_area_list()
    
    def switch_text_change(i):
        global MAINTENANCE_LIST
        sw_variable_list[i].set(switch_list[i].get())
        if switch_list[i].get()=='ON':
            MAINTENANCE_LIST[i]=i
        else:
            MAINTENANCE_LIST[i]=404
    sw_variable_list=[]
    switch_list=[]
    for area in area_list:
        fr=ctk.CTkFrame(maint_button_frame,
                        )
        fr.pack(side='top',fill='x')
        label=ctk.CTkLabel(fr,text=area,font=('Arial',15))
        label.pack(side='left',padx=10,pady=10)
        sw_var=ctk.StringVar(value="OFF")
        sw_variable_list.append(sw_var)
        switch=ctk.CTkSwitch(fr,onvalue="ON",offvalue="OFF",textvariable=sw_var,command=lambda i=area_list.index(area):switch_text_change(i))
        switch.pack(side='right',padx=10,pady=10)
        switch_list.append(switch)
    # maint_check()

def setting_buttons_interface(root,content_frame,setting_button_frame,setting_frame):
    setting_list=list(setting_dict.keys())
    setting_button_list,setting_frame_list=frame_maker(root,setting_list,setting_frame,setting_button_frame,content_frame,1)
    set.personalise_interface(setting_frame_list[0])
    set.account_interface(setting_frame_list[1])
    set.add_new_roads(setting_frame_list[2])
        
   
def interface(main_root):
    with open(THEME_COL_PATH, 'r') as file:
        theme_col=file.read()  
    ctk.set_default_color_theme(theme_col)
    main_root.geometry("800x600")
    main_root.resizable(True,True)
    
    root=ctk.CTkFrame(main_root,)    
    root.pack(expand=True,fill='both')
    
    bg_image_path="assets/bg1.png"
    
    bg_image=ctk.CTkImage(light_image=Image.open(bg_image_path),dark_image=Image.open(bg_image_path),size=(1920,1080))
    
    bg_image_label=ctk.CTkLabel(root,text="",image=bg_image)
    bg_image_label.pack(expand=True,fill='both')
    
    date_label=ctk.CTkLabel(root,text="Date",font=('Helvetica',15),fg_color='#626D7F',bg_color='#626D7F')
    date_label.place(relx=0.75,rely=0.05,anchor='center')
    time_label=ctk.CTkLabel(root,text="Time",font=('Helvetica',15),fg_color='#626D7F',bg_color='#626D7F')
    time_label.place(relx=0.9,rely=0.05,anchor='center')
    
    update_datetime_label(time_label,date_label,root)
    
    content_frame=ctk.CTkFrame(bg_image_label,)
    content_frame.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.7,anchor='center')

    my_tabs = ctk.CTkTabview(content_frame,)
    my_tabs.pack(side='top', fill='both', expand=True)
    
    area_tab=my_tabs.add("📍ROADS")
    area_frame=ctk.CTkFrame(area_tab)
    area_frame.pack(expand=True,fill='both')
    area_button_frame = ctk.CTkScrollableFrame(area_frame,)
    area_button_frame.pack(expand=True, fill='both')
    area_buttons_interface(root,content_frame,area_button_frame,area_frame)
        
    maint_tab=my_tabs.add("⚠️ MAINTENANCE")
    maint_frame=ctk.CTkFrame(maint_tab)
    maint_frame.pack(expand=True,fill='both')
    maint_button_frame = ctk.CTkScrollableFrame(maint_frame,)
    maint_button_frame.pack(expand=True, fill='both')
    maint_buttons_interface(maint_button_frame)
    
    fault_tab=my_tabs.add("⛔ Faulty List")
    fault_frame=ctk.CTkFrame(fault_tab)
    fault_frame.pack(expand=True,fill='both')
    fault_button_frame = ctk.CTkScrollableFrame(fault_frame,)
    fault_button_frame.pack(expand=True, fill='both')
    # fl.interface(fault_button_frame)
    fault_buttons_interface(root,content_frame,fault_button_frame,fault_frame)
    
    setting_tab=my_tabs.add("⚙️ SETTINGS")
    setting_frame=ctk.CTkFrame(setting_tab)
    setting_frame.pack(expand=True,fill='both')
    setting_button_frame = ctk.CTkScrollableFrame(setting_frame)
    setting_button_frame.pack(expand=True, fill='both')
    setting_buttons_interface(root,content_frame,setting_button_frame,setting_frame)
    
    button_state_check()