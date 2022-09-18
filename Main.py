from tkinter import *
from tkinter import ttk
import tkinter.messagebox as tkm
import ctypes
import os
import subprocess
from tkinter import filedialog
urls = []

# Main Download Button Action
def downAction():
    global urls
    urls = text_box.get("1.0", END).split(",")
    arcBool = arc.get()
    for i in range(len(urls)):
        urls[i] = urls[i].strip(" ")
    urls[-1] = urls[-1].strip('\n')
    if urls[0]=='':
        tkm.showinfo("Empty URL", "Please Enter Atleast 1 Valid URL")
        return
    
    ext = clicked.get()
    direc = directory.get("1.0", END)
    direc = direc.strip("\n")
    if direc=='':
        tkm.showinfo("Invalid Directory", "Enter Valid Directory")
        return
    ytdldirec = ytdldirectory.get("1.0", END)
    ytdldirec = ytdldirec.strip("\n")
    if ytdldirec == '':
        tkm.showinfo("yt-dl.exe Invalid Directory", "Enter Valid yt-dl.exe Path")
    downloader(urls, ext, direc, ytdldirec, arcBool)

# Writing And Calling the Bat File
def downloader(urls, ext, direc, ytdldirec, arcBool):
    ytdldirec = list(reversed(ytdldirec))
    i = ytdldirec[0]
    while(i!="/"):
        ytdldirec.pop(0)
        i = ytdldirec[0]
    ytdldirec.pop(0)
    here = "".join(list(reversed(ytdldirec)))
    ytdlp = os.path.join(here, 'ytdlp.bat')
    here = here.replace("/", "\\")
    try:
        myBat = open(ytdlp, 'w+')
        myBat.truncate(0)
        ext = ext.split(' ', 1)
        for i in urls:
            if arcBool == 0:
                myBat.write(f'start /D {here} cmd /k "yt-dlp.exe -P "{direc}" -f "ba[ext={ext[0]}]" {i}"')
            else:
                myBat.write(f'start /D {here} cmd /k "yt-dlp.exe -P "{direc}" -f "ba[ext={ext[0]}]" --download-archive archivefile.txt {i}"')

    finally:
        myBat.close()
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
myURL.grid(row=1, column=0)
myText1 = Label(root, text="    ").grid(row=1, column=1)

# Main URL Text Box
text_box = Text(root, fg="black", highlightthickness="1", height=2, width=width_screen//12, bg="yellow")
text_box.grid(row=1, column=2)
myText1 = Label(root, text="   ").grid(row=1, column=3)

# Main Download Button
myDown = Button(root, text="Download", command = downAction, padx=5, pady=10)
myDown.grid(row=1, column=4)

# Extension Drop Down Menu
myText1 = Label(root, text="Select Extension:").place(x=0, y=115)
clicked = StringVar()
drop = ttk.Combobox(root, width = 27, textvariable = clicked)
drop['values'] = ["m4a (Audio)", "aac (Audio)", "flv (Audio)", "mp3 (Audio)", "webm (Audio)", "wav (Video)", "ogg (Video)",  "3gp (Video)", "mp4 (Video)"]
drop.current(1)
drop.place(x=110, y=115)

# Archive File Checkbox
arc = IntVar()
chkBox = Checkbutton(root, text="Use Archive File", variable=arc)
chkBox.place(x=330, y=110)


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







