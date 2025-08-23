import customtkinter as ctk
# import ttkbootstrap as ttk
from PIL import Image

THEME_PATH='front_end/text_file/theme.txt'
THEME_COL_PATH="front_end/text_file/theme_color.txt"
NAME_PASSWORD_PATH='front_end/text_file/security'

def personalise_interface(frame)->None:
    def theme_change(event):
        ctk.set_appearance_mode(event)
        # with open(THEME_PATH,"r") as file:
        #     theme=file.read()
        # if event.lower()=='light':
        #     ttk.Style().theme_use("litera")
            
        # else:
        #     ttk.Style().theme_use("darkly")
        with open(THEME_PATH, 'w') as file:
            file.write(event)
    theme_list=["System","Light","Dark"]
    them_menue_frame=ctk.CTkFrame(frame)
    them_menue_frame.pack(side='top',fill='x',pady=10,padx=10)
    
    them_img=ctk.CTkImage(light_image=Image.open("assets/theme_light.png"),dark_image=Image.open("assets/theme_dark.png"),size=(30,30))
    them_label=ctk.CTkLabel(them_menue_frame,text="  Choose your mode",image=them_img,compound='left')
    them_label.pack(side='left',padx=10,pady=10)
    theme_menue=ctk.CTkOptionMenu(them_menue_frame,values=theme_list,command=theme_change)
    theme_menue.pack(side='right',padx=10,pady=10)
    
    with open(THEME_PATH, 'r') as file:
        th=file.read()
    theme_menue.set(th.capitalize())
    
    def theme_col_change(event):
        ICON_PATH = "assets/warning.ico"
        top_label = ctk.CTkToplevel(frame, takefocus=True)
        top_label.geometry(f"400x200+{frame.winfo_screenwidth()//2}+{frame.winfo_screenheight()//2}")
        top_label.title("Warning")
        top_label.grab_set()
        top_label.resizable(False, False)
        frame.after(500,lambda:top_label.wm_iconbitmap(ICON_PATH))

        them_col_change_label = ctk.CTkLabel(top_label, text="Close the App and Open it again to apply changes",
                                            fg_color='white', text_color='#c73126', font=('Times', 20))
        them_col_change_label.pack(expand=True, fill='both')

        ctk.set_default_color_theme(event.lower())
        with open(THEME_COL_PATH, 'w') as file:
            file.write(event.lower())
    
    theme_color_list=["Blue","Dark-Blue","Green"]
    them_col_menue_frame=ctk.CTkFrame(frame)
    them_col_menue_frame.pack(side='top',fill='x',pady=10,padx=10)
    
    them_col_img=ctk.CTkImage(light_image=Image.open("assets/accent_col_light.png"),dark_image=Image.open("assets/accent_col_dark.png"),size=(30,30))
    
    them_col_label=ctk.CTkLabel(them_col_menue_frame,text="  Accent Colors",image=them_col_img,compound='left')
    them_col_label.pack(side='left',padx=10,pady=10)
    theme_color_menue=ctk.CTkOptionMenu(them_col_menue_frame,values=theme_color_list,command=theme_col_change)
    theme_color_menue.pack(side='right',padx=10,pady=10)
    
    with open(THEME_COL_PATH, 'r') as file:
            thc=file.read()
    theme_color_menue.set(thc.capitalize())
    
def account_interface(frame)->None:
    def save(fr,entr,check)->None:
        fr.place_forget()
        with open(NAME_PASSWORD_PATH,'r') as file:
            current_name_passwd = file.read().split(',')
        if check==0:
            new_name_passwd=entr.get()+','+current_name_passwd[1]
        elif check==1:
            new_name_passwd=current_name_passwd[0]+','+entr.get()
        with open(NAME_PASSWORD_PATH,'w') as file:
            file.write(new_name_passwd) 
         
    user_name_frame=ctk.CTkFrame(frame)
    user_name_frame.pack(side='top',fill='x',padx=10,pady=10)
    
    name_frame=ctk.CTkFrame(frame)
    name_frame.place_forget()
    content_frame_name=ctk.CTkFrame(name_frame)
    content_frame_name.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.5,anchor='center')
    name_label=ctk.CTkLabel(content_frame_name,text="Input a new username\nin the below form",font=('Arial',20))
    name_label.pack(side='top',expand=True)
    
    name_entry=ctk.CTkEntry(content_frame_name,width=200,placeholder_text="New username")
    name_entry.pack(side='top',expand=True)
    
    save_button=ctk.CTkButton(content_frame_name,text="Save",command=lambda:save(name_frame,name_entry,0))
    save_button.pack(side='top',expand=True)
    
    pass_frame=ctk.CTkFrame(frame)
    pass_frame.place_forget()
    content_frame_password=ctk.CTkFrame(pass_frame)
    content_frame_password.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.7,anchor='center')
    password_label=ctk.CTkLabel(content_frame_password,text="Input a new password\nin the below form",font=('Arial',20))
    password_label.pack(side='top',expand=True)
    
    password_entry=ctk.CTkEntry(content_frame_password,width=200,placeholder_text="New password")
    password_entry.pack(side='top',expand=True)
    
    save_button=ctk.CTkButton(content_frame_password,text="Save",command=lambda:save(pass_frame,password_entry,1))
    save_button.pack(side='top',expand=True)
        
    user_label=ctk.CTkLabel(user_name_frame,text="To Change your username")
    user_label.pack(side='left',padx=10,pady=10)
    
    def change_username():
        name_entry.delete(0,'end')
        name_frame.place(relx=0.5,rely=0.5,relwidth=1,relheight=1,anchor='center')
        name_frame.lift()
        
    ch_user_name=ctk.CTkButton(user_name_frame,text="Change",command=change_username)
    ch_user_name.pack(side='right',padx=10,pady=10)
    
    password_frame=ctk.CTkFrame(frame)
    password_frame.pack(side='top',fill='x',padx=10,pady=10)
    
    password_label=ctk.CTkLabel(password_frame,text="To Change your password")
    password_label.pack(side='left',padx=10,pady=10)
    
    def change_password():
        password_entry.delete(0,'end')
        pass_frame.place(relx=0.5,rely=0.5,relwidth=1,relheight=1,anchor='center')
        pass_frame.lift()
    
    ch_password=ctk.CTkButton(password_frame,text="Change",command=change_password)
    ch_password.pack(side='right',padx=10,pady=10)

def add_new_roads(frame)->None:
    pass