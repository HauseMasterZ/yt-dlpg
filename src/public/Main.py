import datetime
import os
import threading
import tkinter.messagebox as tkm
from tkinter import *
from tkinter import filedialog, messagebox, ttk

import yt_dlp as youtube_dl

urls = []
on_close = False
playlist_index = 1
is_running = False
is_windows = os.name == "nt"
ffmpeg_installed = os.system("ffmpeg -version") == 0


class DownloadStoppedError(Exception):
    pass


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """

    def __init__(self, widget, text="widget info"):
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
        label = Label(
            self.tw,
            text=self.text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            wraplength=self.wraplength,
        )
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


def downAction() -> None:
    global urls, is_running
    urls = [url.strip() for url in text_box.get("1.0", END).split(",")]
    arcBool = arc.get()
    if urls[0] == "":
        tkm.showinfo("Empty URL", "Please Enter Atleast 1 Valid URL")
        return
    ext = clicked.get().split(" ", 1)[0]
    res = clickedRes.get()
    direc = directory.get("1.0", END).strip("\n")
    if direc == "":
        tkm.showinfo("Invalid Directory", "Enter Valid Directory")
        return
    direc = direc.replace("/", "\\")
    myDown.configure(text="Downloading...", background="Red")
    size_lbl.place(anchor=E, relx=0.4, rely=0.85)
    speed_lbl.place(anchor=E, relx=0.54, rely=0.85)
    eta_lbl.place(anchor=W, relx=0.56, rely=0.85)
    now_lbl.place(anchor=CENTER, relx=0.5, rely=0.65)
    index_lbl_id.place(anchor=CENTER, relx=0.88, rely=0.25)
    of_lbl.place(anchor=CENTER, relx=0.9, rely=0.25)
    index_lbl_total.place(anchor=W, relx=0.91, rely=0.25)
    start_time = starting_timestamp.get()
    end_time = ending_timestamp.get()
    valid_time_format = "%H:%M:%S"
    try:
        start_time_obj = datetime.datetime.strptime(
            start_time, valid_time_format
        ).time()
        end_time_obj = datetime.datetime.strptime(end_time, valid_time_format).time()
    except ValueError:
        messagebox.showinfo(
            "Invalid time format", "Please enter time in HH:MM:SS format"
        )
        myDown.configure(text="Download", background="Black")
        return
    if start_time_obj > end_time_obj:
        messagebox.showinfo(
            "Invalid time format", "Start time should be before end time"
        )
        myDown.configure(text="Download", background="Black")
        return
    if not is_running:
        ydl_thread = threading.Thread(
            target=downloader,
            args=(urls, ext, direc, arcBool, res[:-1], start_time, end_time),
        )
        is_running = True
        ydl_thread.daemon = True
        ydl_thread.start()
    else:
        messagebox.showinfo(
            "Current download is not finished",
            "Please Wait till the current dowload is finished.",
        )


def progressHook(progress: dict) -> None:
    global on_close, playlist_index, videoBool
    if on_close:
        raise DownloadStoppedError()
        return
    file_name = progress["filename"].rsplit("\\", 1)[-1]
    if "downloading" in progress["status"]:
        myDown.configure(text="Downloading...", background="Red")
        if progress.get("total_bytes"):
            total_bytes = progress.get("total_bytes")
        else:
            total_bytes = progress.get("total_bytes_estimate")
        downloaded_bytes = progress.get("downloaded_bytes")

        try:
            total_size = float(format(total_bytes / 1048576, ".2f"))
            if total_size > 1024:
                total_size = format(total_size / 1024, ".2f")
                total_size = str(total_size) + "GiB"
            else:
                total_size = str(total_size) + "MiB"
            curr_size = float(format(downloaded_bytes / 1048576, ".2f"))
            if curr_size > 1024:
                curr_size = format(curr_size / 1024, ".2f")
                curr_size = str(curr_size) + "GiB"
            else:
                curr_size = str(curr_size) + "MiB"
            size_lbl.configure(text=f"{curr_size} of {total_size}")
            if progress["speed"] != None:
                speed_lbl.configure(
                    text=f"at {format(progress.get('speed')/1048576, '.2f')}MiB/s"
                )
            if progress["eta"] != None:
                if int(progress["eta"]) > 60:
                    eta_lbl.configure(
                        text=f"{int(progress['eta']/60)} minutes remaining..."
                    )
                else:
                    eta_lbl.configure(
                        text=f"{int(progress['eta'])} seconds remaining..."
                    )
            now_lbl.configure(text=f"Now downloading: {file_name}")
        except Exception as e:
            print(e)
        if total_bytes and downloaded_bytes:
            percentage = (downloaded_bytes / total_bytes) * 100
            progress_bar["value"] = percentage
            percentage_lbl.configure(text=f"{int(percentage)}%")
            root.update_idletasks()
    elif progress["status"] == "finished":
        playlist_index += 1
        playlist_index = min(playlist_index, int(index_lbl_total.cget("text")))
        index_lbl_id.configure(text=playlist_index)

        now_lbl.configure(text=f"Done downloading: {file_name}")
    else:
        myDown.configure(text="Downloading...", background="Red")


def downloader(
    urls: list[str],
    ext: str,
    direc: str,
    arcBool: bool,
    res: int,
    start_time: str,
    end_time: str,
) -> None:
    global videoBool, auto_start_bool, playlist_index, is_running, ffmpeg_installed
    hours, minutes, seconds = map(int, start_time.split(":"))
    start_total_seconds = (hours * 3600) + (minutes * 60) + seconds
    hours, minutes, seconds = map(int, end_time.split(":"))
    end_total_seconds = (hours * 3600) + (minutes * 60) + seconds
    format = ""
    if videoBool:
        if ffmpeg_installed:
            format = f"bv*[ext={ext}][height<={res}]+ba[ext=m4a]/b[ext={ext}][height<={res}]/bv*[height<={res}]+ba[ext=m4a]/b[ext=m4a][height<={res}]/bv*[height<={res}]+ba[ext=m4a]/b[ext=mp3][height<={res}]/bv*[height<={res}]+ba[ext=m4a]/b[ext=flv][height<={res}]"
        else:
            format = f"b[ext={ext}][height<={res}]"
    else:
        format = f"bestaudio[ext={ext}]/bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio[ext=flv]"
    ydl_opts = {
        "format": format,
        "outtmpl": f"{direc}/%(title)s.%(ext)s",
        "progress_hooks": [progressHook],
        "postprocessor_args": (
            [
                "-ss",
                f"{start_total_seconds}",  # Start time in seconds
                "-to",
                f"{end_total_seconds}",  # End time in seconds
            ]
            if start_time != end_time
            else []
        ),
        "download_archive": (
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "archive.txt")
            if arcBool
            else None
        ),
        "yesplaylist": True,
    }

    try:
        download_videos(ydl_opts, urls, start_total_seconds, end_total_seconds)
    except DownloadStoppedError:
        return
    except youtube_dl.DownloadError as err:
        playlist_index = 1
        is_running = False
        myDown.configure(text="Download", background="Black")
        messagebox.showerror("Youtube Dlp Error Occured", f"{err}")


def download_videos(ydl_opts, urls, start_total_seconds, end_total_seconds):
    global videoBool, auto_start_bool, playlist_index, is_running
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for video_url in urls:
            info_dict = ydl.extract_info(video_url, download=False)
            index_lbl_id.configure(text="1")
            of_lbl.configure(text="of ")
            try:
                if (
                    end_total_seconds > info_dict["duration"]
                    or start_total_seconds > info_dict["duration"]
                ):
                    messagebox.showinfo(
                        "Invalid time", "Time is greater than video duration"
                    )
                    myDown.configure(text="Download", background="Black")
                    return
                index_lbl_total.configure(text=info_dict["playlist_count"])
            except KeyError:
                index_lbl_total.configure(text="1")
            ydl.download([video_url])
            if ydl.params.get("noplaylist") or ydl.params.get("max_downloads") is None:
                myDown.configure(text="Download", background="Black")
                is_running = False
                playlist_index = 1


def autoStart() -> None:
    global on_close
    on_close = True
    if auto_start_bool.get() == 1:
        import win32com.client

        Shell = win32com.client.Dispatch("WScript.Shell")
        startup_folder = Shell.SpecialFolders("Startup")
        arcBool = arc.get()
        direc = directory.get("1.0", END)
        direc = direc.strip("\n")
        res = clickedRes.get()
        ext = clicked.get()
        urls = text_box.get("1.0", END).split(",")
        for i in range(len(urls)):
            urls[i] = urls[i].strip(" ")
        urls[-1] = urls[-1].strip("\n")
        ytdlp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ytdlp.bat")
        here = os.path.dirname(os.path.abspath(__file__))
        try:
            myBat = open(ytdlp, "w+")
            myBat.truncate(0)
            ext = ext.split(" ", 1)
            if videoBool:
                if arcBool == 0:
                    myBat.write(
                        f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -S "res:{res}" -f {ext[0]} "{"".join(urls)}"'
                    )
                else:
                    myBat.write(
                        f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -S "res:{res}" -f "bv*+ba/b[ext={ext[0]}]"  --download-archive archive.txt "{"".join(urls)}"'
                    )
            else:
                if arcBool == 0:
                    myBat.write(
                        f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -f {ext[0]} "{"".join(urls)}"'
                    )
                else:
                    myBat.write(
                        f'start /D "{here}" cmd /k "yt-dlp.exe -P "{direc}" -f "bv*+ba/b[ext={ext[0]}]"  --download-archive archive.txt "{"".join(urls)}"'
                    )
        finally:
            myBat.close()

        startup_folder = Shell.SpecialFolders("Startup")
        shortcut_path = os.path.join(startup_folder, "auto_start.lnk")
        target_file = ytdlp
        shortcut = Shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_file
        shortcut.WindowStyle = 7
        shortcut.save()
    else:
        try:
            os.remove(os.path.join(startup_folder, "auto_start.lnk"))
        except:
            pass
    try:
        os.remove(os.path.join(here, "auto_start.lnk"))
    except:
        pass
    root.destroy()


def set_focus(event: Event) -> None:
    if event.widget == root:
        root.focus_set()


def on_entry(event: Event) -> None:
    ending_timestamp.configure(foreground="black")


def on_focus(event: Event) -> None:
    if ending_timestamp.get().strip() == "":
        ending_timestamp.insert(0, "00:00:00")  # Add the placeholder text
    ending_timestamp.configure(foreground="gray")


def openFile() -> None:
    filepath = filedialog.askdirectory()
    directory.delete("1.0", END)
    directory.insert("1.0", filepath)


def videoRes(event: Event) -> None:
    global videoBool
    global resDrop
    ext = clicked.get()
    if ext.split()[1] == "(Video)":
        myText2.place(anchor=W, relx=0.02, rely=0.43)
        videoBool = True
        resDrop["state"] = NORMAL
    else:
        videoBool = False
        resDrop["state"] = DISABLED
        myText2.place_forget()
    return


if __name__ == "__main__":
    root = Tk()
    try:
        if is_windows:
            root.iconbitmap(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "static",
                    "icons",
                    "icon.ico",
                )
            )
        else:
            root.iconbitmap(
                "@"
                + os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "static/icons/icon.xbm"
                )
            )
    except:
        messagebox.showinfo("Iconbitmap icon not found", "Window Icon Cannot be loaded")

    root.geometry(f"{root.winfo_screenwidth()//2}x{root.winfo_screenheight()//2}")
    root.title("YouTube dlp gui")
    root.configure(background="Black")

    title = Label(root, text="YouTube dl Plus GUI ~ HauseMaster", font=("Aerial", 13))
    title.place(anchor=CENTER, relx=0.5, y=10)
    title.configure(foreground="White", background="Black")

    myURL = Label(root, text="Enter URL (CSV):")
    myURL.place(anchor=W, relx=0.02, rely=0.17)
    myURL.configure(foreground="White", background="Black")

    text_box = Text(root, fg="black", highlightthickness="1", height=2, bg="yellow")
    text_box.place(anchor=CENTER, relx=0.5, rely=0.17, relwidth=0.6, relheight=0.1)
    text_box.configure(foreground="Black")

    myDown = Button(root, text="Download", command=downAction, padx=6, pady=10)
    myDown.place(anchor=E, relx=0.96, rely=0.17, relheight=0.1, relwidth=0.1)
    myDown.configure(
        foreground="White",
        background="Black",
        activebackground="Black",
        activeforeground="White",
        relief=RIDGE,
        borderwidth=1,
        highlightthickness=0,
        highlightcolor="Black",
    )

    index_lbl_id = Label(root)
    index_lbl_id.configure(background="black", foreground="#00d10a")
    of_lbl = Label(root)
    of_lbl.configure(background="black", foreground="White")
    index_lbl_total = Label(root)
    index_lbl_total.configure(background="black", foreground="#0096FF")

    myText1 = Label(root, text="Select Extension:")
    myText1.place(anchor=W, relx=0.02, rely=0.32)
    myText1.configure(foreground="White", background="Black")
    clicked = StringVar()
    drop = ttk.Combobox(root, width=27, textvariable=clicked)
    drop["values"] = [
        "m4a (Audio)",
        "aac (Audio)",
        "flv (Audio)",
        "mp3 (Audio)",
        "wav (Audio)",
        "webm (Video)",
        "ogg (Video)",
        "3gp (Video)",
        "mp4 (Video)",
    ]
    drop.current(0)
    drop.place(anchor=W, relx=0.2, rely=0.32)
    myText2 = ttk.Label(root, text="Select Resolution:")
    myText2.configure(foreground="White", background="Black")
    clickedRes = StringVar()
    lst = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
    resDrop = ttk.Combobox(root, values=lst, width=27, textvariable=clickedRes)
    resDrop.place(anchor=W, relx=0.2, rely=0.43)
    resDrop.current(4)
    resDrop["state"] = DISABLED
    videoBool = False
    drop.bind("<<ComboboxSelected>>", videoRes)
    arc = IntVar()
    chkBox = Checkbutton(root, variable=arc)
    chkBox.place(anchor=W, relx=0.48, rely=0.32)
    chkBox.configure(
        foreground="Black",
        background="Black",
        activebackground="Black",
        activeforeground="White",
        highlightthickness=0,
        highlightcolor="Black",
    )
    chkBox_label = Label(root, text="Use Archive File  ?")
    chkBox_label.place(anchor=W, relx=0.53, rely=0.32)
    chkBox_label.configure(background="Black", foreground="White")

    myTip1 = CreateToolTip(
        chkBox_label,
        "Creates a text file which stores all the downloaded files."
        "So that it won't download the same file again.",
    )

    auto_start_bool = IntVar()
    auto = Checkbutton(root, variable=auto_start_bool)
    auto.place(anchor=W, relx=0.48, rely=0.43)
    auto.configure(
        foreground="Black",
        background="Black",
        activebackground="Black",
        activeforeground="White",
        bd=0,
        highlightthickness=0,
        highlightcolor="Black",
        state=NORMAL if is_windows else DISABLED,
    )
    auto_label = Label(root, text="Auto Start  ?")
    auto_label.place(anchor=W, relx=0.52, rely=0.43)
    auto_label.configure(background="Black", foreground="White")

    myTip1 = CreateToolTip(
        auto_label,
        "(WINDOWS ONLY) Creates a shortcut file pointing to the batch script in the default startup folder."
        "To delete the file just uncheck box",
    )

    def on_entry_click(event: Event) -> None:
        starting_timestamp.configure(foreground="black")

    def on_focus_out(event: Event) -> None:
        if starting_timestamp.get().strip() == "":
            starting_timestamp.insert(0, "00:00:00")  # Add the placeholder text
        starting_timestamp.configure(foreground="gray")

    starting_timestamp_lbl = Label(root, text="Start:")
    starting_timestamp_lbl.place(anchor=E, relx=0.79, rely=0.32)
    starting_timestamp_lbl.configure(background="Black", foreground="White")
    starting_timestamp = Entry(root, foreground="gray", bd=1, relief=GROOVE)
    starting_timestamp.configure(highlightthickness=0)
    starting_timestamp.place(anchor=W, relwidth=0.1, relx=0.8, rely=0.32)
    starting_timestamp.insert(0, "00:00:00")  # Insert the placeholder text
    starting_timestamp.configure(foreground="gray")
    starting_timestamp.bind("<FocusIn>", on_entry_click)
    starting_timestamp.bind("<FocusOut>", on_focus_out)

    ending_timestamp_lbl = Label(root, text="End:")
    ending_timestamp_lbl.place(anchor=E, relx=0.79, rely=0.43)
    ending_timestamp_lbl.configure(background="Black", foreground="White")
    ending_timestamp = Entry(root, foreground="gray", bd=1, relief=GROOVE)
    ending_timestamp.configure(highlightthickness=0)
    ending_timestamp.place(anchor=W, relwidth=0.1, relx=0.8, rely=0.43)
    ending_timestamp.insert(0, "00:00:00")  # Insert the placeholder text
    ending_timestamp.configure(foreground="gray")

    ending_timestamp.bind("<FocusIn>", on_entry)
    ending_timestamp.bind("<FocusOut>", on_focus)

    progress_bar = ttk.Progressbar(
        root, orient=HORIZONTAL, length=200, mode="determinate"
    )
    progress_bar.place(relwidth=0.75, anchor=CENTER, relx=0.5, rely=0.75)

    percentage_lbl = Label(root, text="0%")
    percentage_lbl.place(anchor=W, relx=0.89, rely=0.75)
    percentage_lbl.configure(background="Black", foreground="#0096FF")

    note_lbl = Label(root, text=" ? ")
    note_lbl.place(anchor=W, relx=0.94, rely=0.75)
    note_lbl.configure(background="Black", foreground="White")
    myTip3 = CreateToolTip(
        note_lbl,
        "If the format of download is different than the one you selected then "
        "the format is not available and its choosing the next best available format.",
    )

    size_lbl = Label(root)
    size_lbl.configure(background="black", foreground="White")

    speed_lbl = Label(root)
    speed_lbl.configure(background="Black", foreground="#00d10a")

    eta_lbl = Label(root)
    eta_lbl.configure(background="Black", foreground="Yellow")

    now_lbl = Label(root)
    now_lbl.configure(background="Black", foreground="White")

    filePickerButton = Button(root, text="Saving Directory: ", command=openFile)
    filePickerButton.place(anchor=E, relx=0.17, rely=0.55)
    filePickerButton.configure(
        foreground="White",
        background="Black",
        activebackground="Black",
        activeforeground="White",
        relief=GROOVE,
        borderwidth=1,
        highlightthickness=0,
        highlightcolor="Black",
    )

    directory = Text(root, fg="black", highlightthickness="1", height=1)
    directory.place(anchor=W, relx=0.2, rely=0.55, relwidth=0.7)
    directory.configure(
        background="#0D0901",
        foreground="White",
        highlightbackground="White",
        highlightthickness=1,
        borderwidth=0,
        highlightcolor="Grey",
    )

    ffmpeg_label = Label(root, text="FFmpeg: ")
    ffmpeg_label.place(anchor=E, relx=0.5, rely=0.93)
    ffmpeg_label.configure(background="Black", foreground="White")
    ffmpeg_helper_label = Label(root)
    ffmpeg_helper_label.place(anchor=W, relx=0.5, rely=0.93)
    if ffmpeg_installed:
        ffmpeg_helper_label.configure(
            background="Black", foreground="#66f542", text="Dectected  ?"
        )
    else:
        ffmpeg_helper_label.configure(
            background="Black", foreground="Red", text="Not Dectected  ?"
        )

    myTip4 = CreateToolTip(
        ffmpeg_helper_label,
        "Incase ffmpeg is not installed then yt-dlp's ability to download video at specific format and resolution will be limited.",
    )

    root.protocol("WM_DELETE_WINDOW", autoStart)
    root.bind("<Button-1>", set_focus)
    root.mainloop()
