from tkinter import *
from tkinter import ttk
import tkinter.messagebox as tkm
import os
import yt_dlp as youtube_dl
from tkinter import filedialog
import threading
from tkinter import messagebox

urls = []


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """

    def __init__(self, widget, text='widget info'):
        self.waittime = 500  # miliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                      background="#ffffff", relief='solid', borderwidth=1,
                      wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


# Main Download Button Action
def downAction():
    global ydl_thread_global
    global urls
    urls = text_box.get("1.0", END).split(",")
    arcBool = arc.get()
    for i in range(len(urls)):
        urls[i] = urls[i].strip(" ")
    urls[-1] = urls[-1].strip('\n')
    if urls[0] == '':
        tkm.showinfo("Empty URL", "Please Enter Atleast 1 Valid URL")
        return
    ext = clicked.get()
    res = clickedRes.get()
    direc = directory.get("1.0", END)
    direc = direc.strip("\n")
    if direc == '':
        tkm.showinfo("Invalid Directory", "Enter Valid Directory")
        return
    myDown.configure(text='Downloading...', background='Red')
    size_lbl.place(anchor=W, relx=0.29, rely=0.85)
    speed_lbl.place(anchor=E, relx=0.54, rely=0.85)
    eta_lbl.place(anchor=W, relx=0.56, rely=0.85)
    now_lbl.place(anchor=CENTER, relx=0.5, rely=0.65)
    index_lbl_id.place(anchor=CENTER, relx=0.88, rely=0.25)
    of_lbl.place(anchor=CENTER, relx=0.9, rely=0.25)
    index_lbl_total.place(anchor=W, relx=0.91, rely=0.25)

    ydl_thread = threading.Thread(target=downloader, args=(
        urls, ext, direc, arcBool, res[:-1]))
    ydl_thread.start()


on_close = False
playlist_index = 1
# Live Updation


def progressHook(progress):
    global on_close, playlist_index
    if on_close:
        raise DownloadStoppedError()
        return
    file_name = progress["filename"].rsplit("\\", 1)[-1]
    if progress['status'] == 'downloading':
        myDown.configure(text='Downloading...', background='Red')
        total_bytes = progress.get('total_bytes')
        downloaded_bytes = progress.get('downloaded_bytes')
        size_lbl.configure(
            text=f"{format(downloaded_bytes/1048576, '.2f')}MB of {format(total_bytes/1048576, '.2f')}MB at ")
        speed_lbl.configure(
            text=f"{format(progress.get('speed')/1048576, '.2f')}Mib/s")
        eta_lbl.configure(
            text=f"{int(progress['eta']/60)} minutes remaining...")
        now_lbl.configure(text=f'Now downloading: {file_name}')
        if total_bytes and downloaded_bytes:
            percentage = (downloaded_bytes / total_bytes) * 100
            progress_bar['value'] = percentage
            percentage_lbl.configure(text=f'{int(percentage)}%')
            root.update_idletasks()
    elif progress['status'] == 'finished':
        playlist_index += 1
        playlist_index = min(playlist_index, int(index_lbl_total.cget('text')))
        index_lbl_id.configure(text=playlist_index)
        now_lbl.configure(text=f'Done downloading: {file_name}')
    else:
        myDown.configure(text='Downloading...', background='Red')


class DownloadStoppedError(Exception):
    pass

# Writing And Calling the Bat File


def downloader(urls, ext, direc, arcBool, res):
    global videoBool, auto_start_bool, playlist_index
    ext = ext.split(' ', 1)[0]
    ydl_opts = {
        'format': f'bestaudio[ext={ext}]/bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio[ext=flv]',
        'outtmpl': f'{direc}\%(title)s.%(ext)s',
        'progress_hooks': [progressHook],
    }
    if videoBool:
        ydl_opts['format'] = f"bv*[ext={ext}][height<={res}]+ba[ext={ext}][height<={res}]/b[ext={ext}][height<={res}]/bv*[ext={ext}][height<=1080]+ba[ext={ext}][height<=1080]/b[ext={ext}][height<=1080]/bv*+ba/b"

    if arcBool:
        ydl_opts['download_archive'] = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'archive.txt')
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            for video_url in urls:
                info_dict = ydl.extract_info(video_url, download=False)
                index_lbl_id.configure(text='1')
                of_lbl.configure(text='of ')
                try:
                    index_lbl_total.configure(text=info_dict['playlist_count'])
                except KeyError:
                    index_lbl_total.configure(text='1')
                ydl.download([video_url])
                if ydl.params.get('noplaylist') or ydl.params.get('max_downloads') is None:
                    myDown.configure(text='Download', background='Black')
                    playlist_index = 1
    except DownloadStoppedError:
        return
    except youtube_dl.DownloadError as err:
        messagebox.showinfo('Youtube Dlp Error Occured',
                            f'{err}')
        myDown.configure(text='Download', background='Black')
        playlist_index = 1


def autoStart():
    global on_close
    on_close = True
    if auto_start_bool.get() == 1:
        arcBool = arc.get()
        direc = directory.get("1.0", END)
        direc = direc.strip("\n")
        res = clickedRes.get()
        ext = clicked.get()
        urls = text_box.get("1.0", END).split(",")
        for i in range(len(urls)):
            urls[i] = urls[i].strip(" ")
        urls[-1] = urls[-1].strip('\n')
        ytdlp = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'ytdlp.bat')
        here = os.path.dirname(os.path.abspath(__file__))
        try:
            myBat = open(ytdlp, 'w+')
            myBat.truncate(0)
            ext = ext.split(' ', 1)
            if videoBool:
                if arcBool == 0:
                    myBat.write(
                        f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -S "res:{res}" -f {ext[0]} "{"".join(urls)}"')
                else:
                    myBat.write(
                        f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -S "res:{res}" -f "bv*+ba/b[ext={ext[0]}]"  --download-archive archive.txt "{"".join(urls)}"')
            else:
                if arcBool == 0:
                    myBat.write(
                        f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -f {ext[0]} "{"".join(urls)}"')
                else:
                    myBat.write(
                        f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -f "bv*+ba/b[ext={ext[0]}]"  --download-archive archive.txt "{"".join(urls)}"')
        finally:
            myBat.close()
        import win32com.client
        Shell = win32com.client.Dispatch("WScript.Shell")
        startup_folder = Shell.SpecialFolders("Startup")
        shortcut_file = open("auto_start.lnk", "w+")
        target_file = ytdlp
        shortcut = Shell.CreateShortCut(
            os.path.join(startup_folder, 'auto_start.lnk'))
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

    root.destroy()

# Open Saving Location File Picker


def openFile():
    filepath = filedialog.askdirectory()
    directory.delete("1.0", END)
    directory.insert("1.0", filepath)

# Resolution Drop Down


def videoRes(event):
    global videoBool
    global resDrop
    ext = clicked.get()
    if ext.split()[1] == '(Video)':
        myText2.place(anchor=W, relx=0.02, rely=0.43)

        videoBool = True
        resDrop['state'] = NORMAL
    else:
        videoBool = False
        resDrop['state'] = DISABLED
        myText2.place_forget()
    return


# Creating root window
root = Tk()
root.iconbitmap(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'icon.ico'))

# Resizing Root Window
root.geometry(f"{root.winfo_screenwidth()//2}x{root.winfo_screenheight()//2}")
root.title("YouTube dlp gui")
root.configure(background='Black')

# Heading
title = Label(root, text="YouTube dl Plus GUI ~ HauseMaster",
              font=("Aerial", 13))
title.place(anchor=CENTER, relx=0.5, y=10)
title.configure(foreground='White', background='Black')

# URL Label
myURL = Label(root, text="Enter URL (CSV):")
myURL.place(anchor=W, relx=0.02, rely=0.17)
myURL.configure(foreground='White', background='Black')


# Main URL Text Box
text_box = Text(root, fg="black", highlightthickness="1",
                height=2, bg="yellow")
text_box.place(anchor=CENTER, relx=0.5, rely=0.17, relwidth=0.6, relheight=0.1)
text_box.configure(foreground='Black')


# Main Download Button
myDown = Button(root, text="Download", command=downAction, padx=6, pady=10)
myDown.place(anchor=E, relx=0.96, rely=0.17)
myDown.configure(foreground='White', background='Black',
                 activebackground='Black', activeforeground='White', relief=SUNKEN, bd=0)


# Downloading Index
index_lbl_id = Label(root)
index_lbl_id.configure(background='black', foreground='#00d10a')
of_lbl = Label(root)
of_lbl.configure(background='black', foreground='White')
index_lbl_total = Label(root)
index_lbl_total.configure(background='black', foreground='#0096FF')


# Extension Drop Down Menu
myText1 = Label(root, text="Select Extension:")
myText1.place(anchor=W, relx=0.02, rely=0.32)
myText1.configure(foreground='White', background='Black')
clicked = StringVar()
drop = ttk.Combobox(root, width=27, textvariable=clicked)
drop['values'] = ["m4a (Audio)", "aac (Audio)", "flv (Audio)", "mp3 (Audio)",
                  "webm (Video)", "wav (Video)", "ogg (Video)",  "3gp (Video)", "mp4 (Video)"]
drop.current(0)
drop.place(anchor=W, relx=0.2, rely=0.32)


# Resolution Drop Down
myText2 = ttk.Label(root, text="Select Resolution:")
myText2.configure(foreground='White', background='Black')
clickedRes = StringVar()
lst = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
resDrop = ttk.Combobox(root, values=lst, width=27, textvariable=clickedRes)
resDrop.place(anchor=W, relx=0.2, rely=0.43)
resDrop.current(4)
resDrop['state'] = DISABLED
videoBool = False
drop.bind('<<ComboboxSelected>>', videoRes)


# Archive File Checkbox
arc = IntVar()
chkBox = Checkbutton(root, variable=arc)
chkBox.place(anchor=W, relx=0.48, rely=0.32)
chkBox.configure(foreground='Black', background='Black',
                 activebackground='Black', activeforeground='White')
chkBox_label = Label(root, text="Use Archive File  ?")
chkBox_label.place(anchor=W, relx=0.52, rely=0.32)
chkBox_label.configure(background='Black', foreground='White')

myTip1 = CreateToolTip(chkBox_label,
                       'Creates a text file which stores all the downloaded files.'
                       "So that it won't download the same file again.")


# Auto Start Checkbox
auto_start_bool = IntVar()
auto = Checkbutton(root, variable=auto_start_bool)
auto.place(anchor=W, relx=0.48, rely=0.43)
auto.configure(foreground='Black', background='Black',
               activebackground='Black', activeforeground='White')
auto_label = Label(root, text="Auto Start  ?")
auto_label.place(anchor=W, relx=0.52, rely=0.43)
auto_label.configure(background='Black', foreground='White')

myTip1 = CreateToolTip(auto_label,
                       'Creates a shortcut file pointing to the batch script in the default startup folder.'
                       'To delete the file just uncheck box and hit download.')

# Progress Bar
progress_bar = ttk.Progressbar(
    root, orient=HORIZONTAL, length=200, mode='determinate')
progress_bar.place(relwidth=0.75, anchor=CENTER, relx=0.5, rely=0.75)

# Percentage
percentage_lbl = Label(root, text='0%')
percentage_lbl.place(anchor=W, relx=0.9, rely=0.75)
percentage_lbl.configure(background='Black', foreground='#0096FF')

# Size of file
size_lbl = Label(root)
size_lbl.configure(background='black', foreground='White')

# Speed
speed_lbl = Label(root)
speed_lbl.configure(background='Black', foreground='#00d10a')


# ETA
eta_lbl = Label(root)
eta_lbl.configure(background='Black', foreground='Yellow')

# Now Downloading
now_lbl = Label(root)
now_lbl.configure(background='Black', foreground='White')


# Directory of Files Button
filePickerButton = Button(root, text="Saving Directory: ", command=openFile)
filePickerButton.place(anchor=W, relx=0.03, rely=0.55)
filePickerButton.configure(foreground='White', background='Black',
                           activebackground='Black', activeforeground='White', relief=GROOVE, borderwidth=1)

# Saving Path
directory = Text(root, fg="black", highlightthickness="1", height=1)
directory.place(anchor=W, relx=0.2, rely=0.55, relwidth=0.7)
directory.configure(background='#0D0901', foreground='White', highlightbackground='White',
                    highlightthickness=1, borderwidth=0, highlightcolor='Grey')


# Loop Main
root.protocol("WM_DELETE_WINDOW", autoStart)
root.mainloop()
