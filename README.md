# <img src="https://github.com/AbortLarboard/curtains_dev/blob/1561b61e66ffb00adffc2482000e5fa70ed98fdc/misc/curtains%20075.png" width=50 /> Curtains 0.75a_dev

*Curtains is a GUI application made for Windows to hide specific windows from screen sharing.*

<img src="https://github.com/AbortLarboard/curtains_dev/blob/6e556fbaca2fcfb281131a08af1b4e67712c9efc/misc/curtains_windows_nofilter_0.75.png"  width=30% height=30% /><img src="https://github.com/AbortLarboard/curtains_dev/blob/6e556fbaca2fcfb281131a08af1b4e67712c9efc/misc/curtains_windows_filter.0.75.png"  width=30% height=30% /><img src="https://github.com/AbortLarboard/curtains_dev/blob/6e556fbaca2fcfb281131a08af1b4e67712c9efc/misc/curtain_0.75_preview.png"  width=30% height=30% />
	
### Screen sharing can be a delicate process
Since the pandemic video calls and screen sharing became much more frequent. I noticed that many struggled at least once with keeping private content out of their screen while sharing it. Be it a windows notification, a messenger app, an open browser, alt+tab preview, or simply forgetting to turn screensharing off while returning to usual buisness.

Curtains goal is to solve the problem, **keep private  screen content private** and only share the processes that you want on screen. 

There are a few other tools targeting this problem, like [Invisiwind](https://github.com/radiantly/Invisiwind), which inspired me to do something similiar, add more functions and a simplistic GUI.  To my suprise i found none with those features.

# How to run / install
Either download the latest portable executable or download the repository, unpack it into a virtual environment and follow the instructions below.

requirements for source to run:
- [flet==0.4.0](https://github.com/flet-dev/flet)
- [Pillow==9.4.0](https://github.com/python-pillow/Pillow)
- [psutil==5.9.4](https://github.com/giampaolo/psutil)
- [pyinjector==1.1.1](https://github.com/kmaork/pyinjector)
- [pywin32==305](https://github.com/mhammond/pywin32)
- [mss=7.0.1´](https://github.com/BoboTiG/python-mss)


# How does it work?

### Window un-/hiding

Windows can be hidden by using the Win32 API to change the [WindowDisplayAffinity](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity) of a window to `WDA_EXCLUDEFROMCAPTURE` or `WDA_NONE`.

Since those API calls need to originate from the process that owns the windows, curtains uses sane dll-injection using [pyinjector](https://github.com/kmaork/pyinjector) (a python wrapper for [kubo/injector](https://github.com/kubo/injector)).
	
The code for the dll files is copied from [Invisiwind](https://github.com/radiantly/Invisiwind).   
	
To find the windows/parent processes and collect other informations about them the windows API is called via ctypes commands, psutil, pywin32 and win32gui (see curtains.py).

### GUI
Thanks to [flet](https://github.com/flet-dev/flet) the whole interface could be build in pure python while using Flutter. I am still working on it, codewise and designewise. both will probably change a lot until the first stable production release. 


# Features

- hide/unhide all windows of a running process from any kind of screencapture (e.g. screensharing)
	- new windows of hidden processes will be hidden too
	- remembered proccesesses will be hidden/unhidden as soon as they show up, even after closing and restarting the app (lock symbol). 
- see all processes with existing windows that belong to the current active user
	- search processes by name
- preview a scaled down screenshot to check if windows are really hidden/visible
	- interval between screenshots can be configured
	- preview can be turned off
- single file executable is fully portable


# Caveats
 - right now only all windows of a process can be hidden/unhidden.
	- some processes e.g. the main explorer.exe (running taskbar, trays, wallpaper, etc.) have non visible, non clickable windows which will be visible when unhiding the processs windows. Workaround: Either
   don't hide those processes or keep them hidden until logout.
- some processes cannot be hidden because they are running with higher priviliges/other users. Solution: run Curtains with higher priviliges.
- hibernation might cause the GUI to be empty. Solution: Close and restart Curtains. 
- **BEWARE GAMERS**: if you play computer games with third party anti-cheat software you should **never** hide any of the game windows. Some anti-cheat software take automatic screenshots and a missing or
black screenshot could get your account banned. Use at your own risk.


### install requirements
```
pip install -r requirements.txt
```

### cd to curtains folder
```
cd curtains
```

### download DLL files
Either manually download the dll_assets.zip in latest release and extract all .dll files to `/curtains/assets/` or run the script to do it.
You can find the sourcecode in src_dll folder if you want to [build the dynamic link libraries yourself](https://learn.microsoft.com/en-us/cpp/build/walkthrough-creating-and-using-a-dynamic-link-library-cpp?view=msvc-170)
```
python3 ./download_dll.py
```

### start curtains
    cd curtains
    pyhon3 ./main.py

### pyinjector patch for Pyinstaller/flet pack (only needed if you wanna build an .exe file)
The script copies the pyinjector binar to the assets folder and patches pyinjector to check if running as a bundled executable to use the copies binary insides /assets/.

    python3 ./pyinjector_patch_for_pyinstaller.py

### building single file executable with flet pack

    flet pack -i curtains.ico --add-data "assets;assets" main.py



# Questions

### Why does it take the .exe so long to start?
It is the way how executables *frozen* with pyinstaller work. Since the executable file is not compiled but a whole python runtime bundled with scripts and ressources together which will be unpacked at startup. 
This can take up to some few seconds. Of course a compiled executable would be much nicer, but sadly nuitka/cpython don't work well with GUI applications.
It is not because python is slower than compiled languages. There is no heavy lifting happening in Curtains.  

### Why Python for a desktop app?
- I love python!
- i am a beginner still learning other languages and frameworks.
- i lack time lately and python development is kinda fast
- it does the job.
- after playing around with a douzend different GUI frameworks, flet finally looks and feels like what i was looking for. I had to build something with it. 

### Can i run it on machines without admin rights?
Yes! but it will only work on processes owned by your user, that are running without admin rights.

### DLL-injection sounds dangerous.Will it trigger AV or any kind of malware scanner?
Curtains is safe software.
[DLL-Injection](https://en.wikipedia.org/wiki/DLL_injection) is the process of attaching external code to a running process. It is like telling a process to do something it was not intended to do. So it depends on what you tell the process to do. Despite this i cannot rule out AV software flagging Curtains as potentially dangerous because pyinstaller and pyinjector are both known for some false positives.

In case of Curtains, all the injected process do is call the Win32 API with [SetDisplayAffinity](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity) and changes the value for given windows to `WDA_EXCLUDEFROMCAPTURE` or the other way around to `WDA_NONE`. The dll files to do this are open-source, can be checked or build by anyone. Curtains will only be able to do this if it has the needed priviliges aka. it will only work on windows run by the user that runs curtains.

# Planned features & TODOs

 - hotkey to un-/hide the active window
 - option to run as trayicon
 - option to run at startup
 - edit window titles / aka custom titles
 - windows notifications to alert when new unhidden window appears + prompt option
 - upload as pypi package
 - dynamic window size (in hope for flet update to call parent/children soon)
 - implementing a method to verify and validate the dll files befor injection for safety reasons


