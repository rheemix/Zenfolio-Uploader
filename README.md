# Zenfolio Uploader
 Upload files to Zenfolio
## Description
Uploads all supported files in a directory (and all subdirectories) to selected Group and PhotoSet in Zenfolio
![Screenshot](https://i.imgur.com/vMy68AJ.png)

## Instructions
- Log into Zenfolio with ID & Password
- Select directory with support files
- Select Group and PhotoSet
- 	Or provide new names for Group and PhotoSet, and they will be created
## Requirements
Python 3
Windows executable also included

### Required Libraries
- [pyzenfolio](https://pypi.org/project/pyzenfolio/) - Light-weight Zenfolio API Python wrapper
  - Slight modification to the library is required to upload video files
- [ttkthemes](https://pypi.org/project/ttkthemes/) - A group of themes for the ttk extentions for Tkinter