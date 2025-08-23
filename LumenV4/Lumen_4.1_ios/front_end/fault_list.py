import customtkinter as ctk
import json
import threading
from PIL import Image
import pickle
import front_end.dashboard as dash
import back_end.fault_search as fs

f_lp_filename = 'fault_list.pkl'

def get_area_list()-> list:
    with open("data.json", 'r') as w_file:
        ip_dict = json.load(w_file)
    a_list=list(ip_dict.keys())
    return a_list,ip_dict


def find_fault(i,scr_frame,strt):
    
    def create_list(frame):
        with open(f_lp_filename, 'rb') as file:
            faulty_lp_list= pickle.load(file)
        road_name=get_area_list()[0][i]
        lp_name_list=get_area_list()[1][road_name]['lp_name']
        text="\n\n"
        if all(x == 1 for x in faulty_lp_list):
            text += "No Fault Found!\n\n"
        else:
            for lp_name in lp_name_list:
                lp_index=lp_name_list.index(lp_name)
                f=faulty_lp_list[lp_index]
                if 0 ==f:
                    text=text+f"{lp_name}\t:\tPannel Fault!\n\n"
                elif 404 == f:
                    text=text+f"{lp_name}\t:\tCould not connect!\n\n"
        
        fr=ctk.CTkFrame(frame)
        fr.pack(side='top',pady=5,fill='x')
        fr.propagate(True)
        button_image=ctk.CTkImage(light_image=Image.open("assets/faulty_icon.png"),dark_image=Image.open("assets/faulty_icon.png"),size=(30,30))
        bu=ctk.CTkLabel(fr,
                            text=text,
                            # image=button_image,
                            justify='left',
                            compound='left',
                            font=('Helvetica',15),
                            text_color='red'
                        )
        bu.pack(anchor='center')
        FS_THREAD.join()
        dash.update_button(i)
        
    road_name=get_area_list()[0][i]
    FS_THREAD=threading.Thread(target=fs.fault_check, args=(get_area_list()[1][road_name]['lp_ip'],))
    FS_THREAD.start()
    
    fr=ctk.CTkFrame(scr_frame)
    fr.pack(expand=True,pady=30,fill='both')
    
    labe=ctk.CTkLabel(fr,text="Please Stand by Fault Search is running...")
    labe.pack(side='top',expand=True,fill='x',padx=10,pady=10)
    progress_bar=ctk.CTkProgressBar(fr)
    progress_bar.pack(side='top',expand=True)
    
    progress_bar.set(strt)
    def show_prog(strt):
        progress_bar.set(strt)
        if strt<1:
            strt=strt+0.1
            scr_frame.after(1000,lambda:show_prog(strt))
        else:
            fr.pack_forget()
            create_list(scr_frame)
    show_prog(strt)

def fault_search(frame,i):
    ICON_PATH = "assets/warning.ico"
    top_label = ctk.CTkToplevel(frame, takefocus=True)
    top_label.geometry(f"400x200+{frame.winfo_screenwidth()//2}+{frame.winfo_screenheight()//2}")
    top_label.title("Faulty Light List")
    top_label.grab_set()
    top_label.resizable(False, False)
    frame.after(500,lambda:top_label.wm_iconbitmap(ICON_PATH))
    
    scr_frame=ctk.CTkScrollableFrame(top_label)
    scr_frame.pack(expand=True,fill='both')

    find_fault(i,scr_frame,0)
    
def interface(frame,i):
    f_search_frame=ctk.CTkFrame(frame)
    f_search_frame.pack(side='top',pady=5,fill='x')

    f_search_label=ctk.CTkLabel(f_search_frame,text=f"Click the Button for Fault Search",font=("Helvetica",15,'bold'))
    f_search_label.pack(side='left',pady=5,padx=5)
    
    f_search_button=ctk.CTkButton(f_search_frame,text="Fault Search",command=lambda: fault_search(frame,i),font=("Helvetica",15,'bold'))
    f_search_button.pack(side='right',pady=5,padx=5)
    
    
        
        
            