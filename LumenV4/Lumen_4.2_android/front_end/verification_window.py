import customtkinter as ctk
from PIL import Image
import front_end.area_select as ase

WI = 650
HI = 500

BG_IMG_PATH="assets/ORANGE_LOADING_1.png"
PASSWORD_FILE="front_end/text_file/security"

def verification_interface(main_root):
    def check_password():
        entered_username = username_entry.get()
        entered_password = password_entry.get()
        ent=entered_username+','+entered_password
        with open(PASSWORD_FILE, 'r') as file:
            stored_password = file.read().strip()
        if ent == stored_password:
            username_entry.configure(border_color='')
            password_entry.configure(border_color='')
            root.pack_forget()
            ase.interface(main_root)
            # result_var.set(1)
            # root.destroy()
        else:
            incorrect_label.pack(side='top', pady=10)
            # content_frame.pack(padx=50, pady=50,anchor='center')
            username_entry.configure(border_color='red')
            password_entry.configure(border_color='red')
    # main_root.attributes("-fullscreen", False)
    
    main_root.resizable(False, False)
    main_root.geometry(f"{WI}x{HI}")
    root=ctk.CTkFrame(main_root)
    root.pack(expand=True,fill='both')
    ctk.set_default_color_theme('green')
    
    bg_img=ctk.CTkImage(light_image=Image.open(BG_IMG_PATH),dark_image=Image.open(BG_IMG_PATH),size=(WI,HI))
    bg_label=ctk.CTkLabel(root,text='',image=bg_img)
    bg_label.pack(expand=True,fill='both')
    
    right_frame=ctk.CTkFrame(bg_label)
    right_frame.place(relx=0.5,rely=0.13,relheight=0.75,relwidth=0.4)
    
    content_frame=ctk.CTkFrame(right_frame)
    content_frame.place(relx=0.5,rely=0.5,relheight=0.8,relwidth=0.8,anchor='center')#pack(expand=True,anchor='center')
    
    
    
    incorrect_label = ctk.CTkLabel(content_frame, text="Incorrect Username or Password", font=("Times", 10),text_color='red')
    incorrect_label.pack_forget()
    username_label = ctk.CTkLabel(content_frame, text="Enter Username:", anchor="center")
    username_label.pack(side='top', pady=10, padx=10)
    username_entry = ctk.CTkEntry(content_frame, placeholder_text='Username')
    username_entry.pack(side='top', padx=10)
    
    password_label = ctk.CTkLabel(content_frame, text="Enter Password:", anchor="center")
    password_label.pack(side='top', pady=10, padx=10)
    password_entry = ctk.CTkEntry(content_frame, show="*", placeholder_text='Password')
    password_entry.pack(side='top', padx=10)
    
    submit_button = ctk.CTkButton(content_frame, text="Submit",#command=lambda: check_password(root, username_entry, password_entry, f"{p}", tx, result_var),
                                  command=check_password,
                                  state='disabled',cursor='hand2')
    submit_button.pack(side='top', pady=10, padx=10)
    
    def check_entries(entries, button):
        all_filled = all(entry.get() for entry in entries)
        button.configure(state='normal' if all_filled else 'disabled')

    username_entry.bind('<KeyRelease>', lambda event, entries=[username_entry, password_entry], button=submit_button: check_entries(entries, button))
    password_entry.bind('<KeyRelease>', lambda event, entries=[username_entry, password_entry], button=submit_button: check_entries(entries, button))
    
    
    
# root=ctk.CTk()
# verification_interface(root)
# root.mainloop()