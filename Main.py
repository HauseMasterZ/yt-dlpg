from tkinter import *
from tkinter import ttk
import tkinter.messagebox as tkm
import ctypes
import os
import subprocess
from tkinter import filedialog
import win32com.client
from idlelib.tooltip import Hovertip
import sys
Shell = win32com.client.Dispatch("WScript.Shell")       
startup_folder = Shell.SpecialFolders("Startup")

urls = []

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
def tempOpen():
    os.popen(resource_path('yt-dlp.exe'))
    print('ytdlp opened')


# Main Download Button Action
def downAction():
    global urls
    tempOpen()
    urls = text_box.get("1.0", END).split(",")
    arcBool = arc.get()
    for i in range(len(urls)):
        urls[i] = urls[i].strip(" ")
    urls[-1] = urls[-1].strip('\n')
    if urls[0]=='':
        tkm.showinfo("Empty URL", "Please Enter Atleast 1 Valid URL")
        return
    
    ext = clicked.get()
    res = clickedRes.get()
    direc = directory.get("1.0", END)
    direc = direc.strip("\n")
    if direc=='':
        tkm.showinfo("Invalid Directory", "Enter Valid Directory")
        return
    ytdldirec = ytdldirectory.get("1.0", END)
    ytdldirec = ytdldirec.strip("\n")
    if ytdldirec == '':
        tkm.showinfo("yt-dl.exe Invalid Directory", "Enter Valid yt-dl.exe Path")
    downloader(urls, ext, direc, ytdldirec, arcBool, res[:-1])

# Writing And Calling the Bat File
def downloader(urls, ext, direc, ytdldirec, arcBool, res):
    global videoBool, auto_start_bool, startup_folder
    ytdldirec = list(reversed(ytdldirec))
    i = ytdldirec[0]
    while(i!="/"):
        ytdldirec.pop(0)
        i = ytdldirec[0]
    ytdldirec.pop(0)
    here = "".join(list(reversed(ytdldirec)))
    ytdlp = os.path.join(here, 'ytdlp.bat')
    here = here.replace("/", "\\")
    print(here)
    try:
        myBat = open(ytdlp, 'w+')
        myBat.truncate(0)
        ext = ext.split(' ', 1)
        for i in urls:
            if videoBool:
                if arcBool == 0:
                    myBat.write(f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -S "res:{res}" -f {ext[0]} {i}"')
                else:
                    myBat.write(f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -S "res:{res}" -f "bv*+ba/b[ext={ext[0]}]"  --download-archive archivefile.txt {i}"')
            else:
                if arcBool == 0:
                    myBat.write(f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -f {ext[0]} {i}"')
                else:
                    myBat.write(f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -f "bv*+ba/b[ext={ext[0]}]"  --download-archive archivefile.txt {i}"')
    finally:
        myBat.close()
    if auto_start_bool.get() == 1:
        shortcut_file = open("auto_start.lnk", "w+")
        target_file = ytdlp
        shortcut = Shell.CreateShortCut(os.path.join(startup_folder, 'auto_start.lnk'))
        shortcut.Targetpath = target_file
        shortcut.WindowStyle = 7 
        shortcut.save()
        shortcut_file.close()
    else:
        try:
            os.remove(os.path.join(startup_folder, 'auto_start.lnk'))
        except:
            pass
    try:
        os.remove(os.path.join(here, 'auto_start.lnk'))
    except:
        pass
    subprocess.call([f'{ytdlp}'])

# Open Saving Location File Picker
def openFile():
    filepath = filedialog.askdirectory()
    directory.delete("1.0", END)
    directory.insert("1.0", filepath)

# Open Ytdl File Picker
def openYtdl():
    ytdlpath = filedialog.askopenfilename()
    ytdldirectory.delete("1.0", END)
    ytdldirectory.insert("1.0", ytdlpath)



def videoRes(event):
    global videoBool
    global resDrop
    ext = clicked.get()
    if ext.split()[1] == '(Video)':
        myText2.grid(padx = 0, pady = 65)

        videoBool = True
        resDrop['state'] = NORMAL
    else:
        videoBool = False
        resDrop['state'] = DISABLED
        myText2.grid_remove()
    return



# Creating root window
user32 = ctypes.windll.user32
screensize = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
root = Tk()

# Resizing Root Window
width_screen = int(int(screensize[0])//2)
height_screen = int(int(screensize[1])//2)
root.geometry(f"{width_screen}x{height_screen}")
root.title("YouTube dlp gui")

# Heading
title = Label(root, text="YouTube dl Plus GUI ~ HauseMaster", font=("Aerial", 13))
title.place(x=width_screen//4+30, y=0)

# URL Label
myText1 = Label(root, text="\n    \n").grid(row=0, column=4)
myURL = Label(root, text="Enter URL (CSV):")
myURL.grid(row=1, column=0, padx= 5)
myText1 = Label(root, text="    ").grid(row=1, column=1)

# Main URL Text Box
text_box = Text(root, fg="black", highlightthickness="1", height=2, width=width_screen//12, bg="yellow")
text_box.grid(row=1, column=2, padx=5)
myText1 = Label(root, text="   ").grid(row=1, column=3)

# Main Download Button
myDown = Button(root, text="Download", command = downAction, padx=6, pady=10)
myDown.grid(row=1, column=4)

# Extension Drop Down Menu
myText1 = Label(root, text="Select Extension:").place(x=0, y=115)
clicked = StringVar()
drop = ttk.Combobox(root, width = 27, textvariable = clicked)
drop['values'] = ["m4a (Audio)", "aac (Audio)", "flv (Audio)", "mp3 (Audio)", "webm (Audio)", "wav (Video)", "ogg (Video)",  "3gp (Video)", "mp4 (Video)"]
drop.current(1)
drop.place(x=110, y=115)
myText2 = ttk.Label(root, text="Select Resolution:")
clickedRes = StringVar()
lst = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
resDrop = ttk.Combobox(root, values=lst, width = 27, textvariable = clickedRes)
resDrop.place(x=100, y=160)
resDrop.current(4)
resDrop['state'] = DISABLED
videoBool = False
drop.bind('<<ComboboxSelected>>',videoRes)

# Archive File Checkbox
arc = IntVar()
chkBox = Checkbutton(root, text="Use Archive File", variable=arc)
chkBox.place(x=330, y=110)
#Tooltip for Archile file Checkbox
tool_tip = Label(root, text="?")
tool_tip.place(x=445, y=111)
myTip = Hovertip(tool_tip,"Creates a text file which stores all the downloaded files\nSo that it won't download the same file again.")


# Auto Start Checkbox
auto_start_bool = IntVar()
auto = Checkbutton(root, text="Auto Start", variable=auto_start_bool)
auto.place(x=330, y=155)

#Tooltip For Auto Start Checkbox
tool_tip = Label(root, text="?")
tool_tip.place(x=420, y=157)
myTip = Hovertip(tool_tip,'Creates a shortcut file pointing to the batch script in the default startup folder.\n To delete the file just uncheck box and hit download.')



# Directory of Files Button
filePickerButton = Button(root, text="Saving Directory: ", command=openFile)
filePickerButton.place(x=40, y=200)

# Saving Path
directory = Text(root, fg="black", highlightthickness="1", height=1, width=width_screen//12)
directory.place(x=150, y=202)

# Directory of ytdl.exe Button
ytdlPickerButton = Button(root, text="yt-dlp.exe Directory: ", command=openYtdl)
ytdlPickerButton.place(x=20, y=300)

# ytdl Path
ytdldirectory = Text(root, fg="black", highlightthickness="1", height=1, width=width_screen//12)
ytdldirectory.place(x=150, y=302)

# Loop Main
root.mainloop()







