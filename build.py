import PyInstaller.__main__
import os

def build_exe():
    PyInstaller.__main__.run([
        'main.py',
        '--name=Zwanski-Unlocker-Pro',
        '--onedir',
        '--windowed',
        '--icon=assets/icons/app.ico',
        '--add-data=core;core',
        '--add-data=gui;gui',
        '--add-data=utils;utils',
        '--add-data=translations;translations',
        '--add-data=config;config',
        '--add-data=tools;tools',
        '--hidden-import=PyQt5',
        '--hidden-import=requests',
        '--hidden-import=packaging'
    ])

if __name__ == '__main__':
    build_exe()