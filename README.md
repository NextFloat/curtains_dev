
# <img src="https://github.com/AbortLarboard/curtains_dev/blob/f4d56679000f5b01984972b1e24b9ec4106ed5cb/curtains/assets/curtains_32.png" /> Curtains
*Curtains is a GUI application made for Windows to hide specific windows from screen sharing.*

<img src="https://github.com/AbortLarboard/curtains_dev/blob/997bd5fb9ce96d513d75a9560bee00596d98dfd1/misc/curtains_demo_screenshot.png" />


```diff
- Right now Curtains is in early development, quite rudamentary. -
```
	
### Screen sharing can be a delicate process
Since the pandemic video calls and screen sharing became much more frequent. I noticed that many struggled at least once with keeping private content out of their screen while sharing it. Be it a windows notification, a messenger app, an open browser, alt+tab preview, or simply forgetting to turn screensharing off while returning to usual buisness.

Curtains goal is to solve the problem, **keep private  screen content private** and only share the processes that you want on screen. 

There few other tools targeting this problem, like [Invisiwind](https://github.com/radiantly/Invisiwind), which inspired me to do something similiar, add more functions and a simplistic GUI.  To my suprise i found none with those features.


# How does it work?

### Window un-/hiding

Windows can be hidden by using the Win32 API to change the [WindowDisplayAffinity](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity) of a window to `WDA_EXCLUDEFROMCAPTURE`.

Since those API calls need originate from the process that owns the windows, curtains uses sane dll-injection using [pyinjector](https://github.com/kmaork/pyinjector) (a python wrapper for [kubo/injector](https://github.com/kubo/injector)).
	
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
- some very rare processes cannot be hidden because they have some kind of protection built
- some processes cannot be hidden because they are running with higher priviliges. Solution: run Curtains with higher priviliges.
- hibernation might cause the GUI to be empty. Solution: Close and restart Curtains. 
- **BEWARE GAMERS**: if you play computer games with third party anti-cheat software you should **never** hide any of the game windows. Some anti-cheat software take automatic screenshots and a missing or
black screenshot could get your account banned.


# How to run / install
Either user downloaded the portable executable here or download the repository into a virtual environment and follow the instructions below.


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
```
python3 ./download_dll.py
```

### start curtains
    pyhon3 ./main.py

### pyinjector patch for Pyinstaller/flet pack (only needed if you wanna build an .exe file)
The script copies the pyinjector binar to the assets folder and patches pyinjector to check if running as a bundled executable to use the copies binary insides /assets/.

    python3 ./pyinjector_patch_for_pyinstaller.py

### building single file executable with flet pack

    flet pack -i curtains.ico --add-data "assets;assets" curtains_gui.py



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
Yes! 

### DLL-injection sounds dangerous.Will it trigger AV or any kind of malware scanner?
No, Curtains is safe software.
[DLL-Injection](https://en.wikipedia.org/wiki/DLL_injection) is the process of attaching external code to a running process. It is like telling a process to do something it was not intended to do. So it depends on what you tell the process to do.

In case of Curtains, all the injected process do is call the Win32 API with [SetDisplayAffinity](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity) and chage the value for given windows to `WDA_EXCLUDEFROMCAPTURE` or the other way around. The dll files to do this are open-source, can be checked or build by anyone. 


# Planned features & TODOs

 - hotkey to un-/hide the active window
 - *hide everything* mode (allowlist mode)
 - rule table to hide/not hide windows (allowlist/blocklist)
 - option to run as trayicon
 - option to run at startup
 - window manager to see all windows with position and title. 
	 - change window titles
 - windows notifications to alert when new unhidden window appears + prompt option
 - configuration menu
 - upload as pypi package


