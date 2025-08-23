import customtkinter as ctk
from PIL import Image
import front_end.settings as set
import front_end.dashboard as dash

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


def get_area_list():
    a_list=["ROAD 1","ROAD 2","ROAD 3","ROAD 4","Biswa Bangla Sarani"]
    return a_list

def button_state_check():
    global OLD_MAINT_LIST,MAINTENANCE_LIST
    global area_button_list
    global info_button_list
    if OLD_MAINT_LIST!=MAINTENANCE_LIST:
        OLD_MAINT_LIST=MAINTENANCE_LIST.copy()
        for button in area_button_list:
            if area_button_list.index(button) in MAINTENANCE_LIST:
                button.configure(state='disabled',text=f"{get_area_list()[area_button_list.index(button)]}\nMaintaince Mode is on🔒")
            else:
                button.configure(state='normal',text=f"{get_area_list()[area_button_list.index(button)]}")
        for button in info_button_list:
            if info_button_list.index(button) in MAINTENANCE_LIST:
                button.configure(state='disabled',text=f"Info of {get_area_list()[info_button_list.index(button)]}\nMaintaince Mode is on🔒")
            else:
                button.configure(state='normal',text=f"Info of {get_area_list()[info_button_list.index(button)]}")
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
            frame=ctk.CTkFrame(root,height=area_frame.winfo_height())
            frame.place_forget()
            top_frame=ctk.CTkFrame(frame)
            top_frame.pack(side='top',fill='x')
            back_button=ctk.CTkButton(top_frame,width=25,height=25,font=('Times',30),
                                    text="🔙",command=lambda:back_operation(area_button_frame,area_frame_list,content_frame))
            back_button.pack(side='left',padx=15,pady=10)
            
            area_frame_list.append(frame)
            
            # button_image=ctk.CTkImage(light_image=Image.open(buttons_dict[str(i+1)]["icon_path"]),dark_image=Image.open(buttons_dict[str(i+1)]["icon_path"]),size=(30,30))
            buttons=ctk.CTkButton(area_button_frame,command=lambda frame=frame:toogle_frame(frame,area_button_frame,content_frame,area_frame_list),
                                text=area_list[i],state='normal',font=('Arial',15),text_color='white',text_color_disabled='#c73126')
            buttons.pack(side='top',expand=True,fill='x',padx=10,pady=10)
            area_button_list.append(buttons)
            MAINTENANCE_LIST.append(404)
    else:
        for i in range(len(area_list)):
            frame=ctk.CTkFrame(root,height=area_frame.winfo_height())
            frame.place_forget()
            top_frame=ctk.CTkFrame(frame)
            top_frame.pack(side='top',fill='x')
            back_button=ctk.CTkButton(top_frame,text="🔙",width=25,height=25,
                                    command=lambda:back_operation(area_button_frame,area_frame_list,content_frame),font=('Times',30))
            back_button.pack(side='left',padx=15,pady=10)
            
            area_frame_list.append(frame)
            
            button_image=ctk.CTkImage(light_image=Image.open(setting_dict[i+1]["path"]),dark_image=Image.open(setting_dict[i+1]["path"]),size=(30,30))
            buttons=ctk.CTkButton(area_button_frame,command=lambda frame=frame:toogle_frame(frame,area_button_frame,content_frame,area_frame_list,1),
                                text=setting_dict[i+1]["name"],state='normal',image=button_image,font=('Arial',15),text_color='white',text_color_disabled='#c73126')
            buttons.pack(side='top',expand=True,fill='x',padx=10,pady=10)
            area_button_list.append(buttons)
    return area_button_list,area_frame_list
        
def area_buttons_interface(root,content_frame,area_button_frame,area_frame):
    global OLD_MAINT_LIST,MAINTENANCE_LIST
    global area_button_list
    area_list=get_area_list()
    area_button_list,area_frame_list=frame_maker(root,area_list,area_frame,area_button_frame,content_frame)
    
def info_buttons_interface(root,content_frame,info_button_frame,info_frame):
    global info_button_list
    info_list=get_area_list()
    info_button_list,info_frame_list=frame_maker(root,info_list,info_frame,info_button_frame,content_frame)
    for i_frame in info_frame_list:
        dash.interface(i_frame,info_frame_list.index(i_frame))

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
        fr=ctk.CTkFrame(maint_button_frame)
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
    root=ctk.CTkFrame(main_root)
    root.pack(expand=True,fill='both')
    bg_image_path="assets/2.jpg"
    
    bg_image=ctk.CTkImage(light_image=Image.open(bg_image_path),dark_image=Image.open(bg_image_path),size=(1920,1080))
    
    bg_image_label=ctk.CTkLabel(root,text="",image=bg_image)
    bg_image_label.pack(expand=True,fill='both')
    
    content_frame=ctk.CTkFrame(bg_image_label)
    content_frame.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.7,anchor='center')

    my_tabs = ctk.CTkTabview(content_frame)
    my_tabs.pack(side='top', fill='both', expand=True)
    
    area_tab=my_tabs.add("📍ROADS")
    area_frame=ctk.CTkFrame(area_tab)
    area_frame.pack(expand=True,fill='both')
    area_button_frame = ctk.CTkScrollableFrame(area_frame)
    area_button_frame.pack(expand=True, fill='both')
    area_buttons_interface(root,content_frame,area_button_frame,area_frame)
    
    info_tab=my_tabs.add("ℹ️INFO")
    info_frame=ctk.CTkFrame(info_tab)
    info_frame.pack(expand=True,fill='both')
    info_button_frame = ctk.CTkScrollableFrame(info_frame)
    info_button_frame.pack(expand=True, fill='both')
    info_buttons_interface(root,content_frame,info_button_frame,info_frame)
    
    maint_tab=my_tabs.add("⚠️ MAINTENANCE")
    maint_frame=ctk.CTkFrame(maint_tab)
    maint_frame.pack(expand=True,fill='both')
    maint_button_frame = ctk.CTkScrollableFrame(maint_frame)
    maint_button_frame.pack(expand=True, fill='both')
    maint_buttons_interface(maint_button_frame)
    
    setting_tab=my_tabs.add("⚙️ SETTINGS")
    setting_frame=ctk.CTkFrame(setting_tab)
    setting_frame.pack(expand=True,fill='both')
    setting_button_frame = ctk.CTkScrollableFrame(setting_frame)
    setting_button_frame.pack(expand=True, fill='both')
    setting_buttons_interface(root,content_frame,setting_button_frame,setting_frame)
    
    button_state_check()