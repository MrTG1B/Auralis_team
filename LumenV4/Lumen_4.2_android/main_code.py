import customtkinter as ctk
# import ttkbootstrap as ttk
import front_end.verification_window as vw
import front_end.area_select as ase

THEME_PATH='front_end/text_file/theme.txt'
THEME_COL_PATH="front_end/text_file/theme_color.txt"
APP_ICON_PATH="assets/icon.ico"
def main():
    root=ctk.CTk()
    with open(THEME_PATH, 'r') as file:
        theme=file.read()
    ctk.set_appearance_mode(theme)
    # with open(THEME_PATH,"r") as file:
    #     theme=file.read()
    # if theme=='light':
    #     ttk.Style().theme_use("litera")
        
    # else:
    #     ttk.Style().theme_use("darkly")
    with open(THEME_COL_PATH, 'r') as file:
        theme_col=file.read()  
    ctk.set_default_color_theme(theme_col)
    # ctk.set_default_color_theme('green')
    root.geometry("800x600")
    root.title("Lumen")
    root.iconbitmap(bitmap=APP_ICON_PATH,default=APP_ICON_PATH)
    
    # vw.verification_interface(root)
    # if verific ==1:
    #     vw_root.pack_forget()
    ase.interface(root)
    
    
    root.mainloop()
main()