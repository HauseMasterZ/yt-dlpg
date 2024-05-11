import subprocess
import os
def downloader(urls, ext, direc):
    here = os.path.dirname(os.path.abspath(__file__))
    ytdlp = os.path.join(here, 'ytdlp.bat')
    try:
        myBat = open(ytdlp, 'w+')
        myBat.truncate(0)
        print(direc)
        myBat.write(f"cd {here}\n")
        ext = ext.split(' ', 1)
        for i in urls:
            myBat.write(f'start cmd.exe /k "yt-dlp.exe -P "{direc}" -f "ba[ext={ext[0]}]" --download-archive archivefile.txt {i}"')
    finally:
        myBat.close()
    subprocess.call([f'{ytdlp}'])
