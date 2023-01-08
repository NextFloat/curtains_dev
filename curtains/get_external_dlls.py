import os
import zipfile
from distutils.core import setup

setup(
    name='Curtains',
    version='0.0.1a_dev',
    author='AbortLarbord',
    author_email='',
    packages=['curtains', 'curtains_gui', 'database', 'injector_patch'],
    scripts=['curtains_gui.py', 'database.py', 'injector_patch.py'],
    url='tba',
    license='LICENSE.txt',
    description='privacy tool to hide all windows of specific processes from screencapture/screensharing/screenshots. Desktop GUI application for Win10/Win11.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.1.1",
        "caldav == 0.1.4",
    ],
)




def download_latest_release(user, repo, asset_name):
    command = f'curl -fsSL github.com/{user}/{repo}/releases/latest/download/{asset_name} -O'
    os.system(command)

def create_assets_dir():
    if not os.path.exists(assets_dir):
        os.mkdir('assets')

def unpack_dll_files():
    zip_file = zipfile.ZipFile((basedir + '/' + asset_name), 'r')
    for file in zip_file.namelist():
        if file in dll_files:
            zip_file.extract(file,assets_dir)

    zip_file.close()

if __name__ == '__main__':
    user = 'radiantly'
    repo = 'Invisiwind'
    asset_name = 'invisiwind.zip'
    dll_files = ['Hide.dll', 'Hide_32bit.dll', 'Unhide.dll', 'Unhide_32bit.dll']
    basedir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = basedir + '/assets'

    download_latest_release(user, repo, asset_name)
    create_assets_dir()
    unpack_dll_files()
    os.remove(basedir + '/' + asset_name) #cleanup
