import customtkinter as ctk
import threading
import front_end.verification_window as vw
import front_end.area_select as ase
import back_end.back_end_function as bef

THEME_PATH='front_end/text_file/theme.txt'
THEME_COL_PATH="front_end/text_file/theme_color.txt"
APP_ICON_PATH="assets/icon.ico"
def main():
    root=ctk.CTk()
    with open(THEME_PATH, 'r') as file:
        theme=file.read()
    ctk.set_appearance_mode(theme)
    with open(THEME_COL_PATH, 'r') as file:
        theme_col=file.read()  
    ctk.set_default_color_theme(theme_col)
    root.geometry("800x600")
    root.title("Lumen")
    root.iconbitmap(bitmap=APP_ICON_PATH,default=APP_ICON_PATH)
    root.focus_set()
    def toggle_fullscreen(root):
        root.attributes('-fullscreen', not root.attributes('-fullscreen'))
        root.geometry("800x600")
    root.bind("<F11>", lambda event, root=root: toggle_fullscreen(root))
    LP_FLAG=threading.Event()
    LP_THREAD=threading.Thread(target=bef.run_in_bg,args=(LP_FLAG,))
    # vw.verification_interface(root)
    # if verific ==1:
    #     vw_root.pack_forget()
    ase.interface(root)
    LP_THREAD.start()
    # bedf.main_bg(root)
    
    root.mainloop()
    LP_FLAG.set()
    LP_THREAD.join()
main()