from pyzenfolio import PyZenfolio
import os.path
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *
from tkinter import scrolledtext as st
from ttkthemes import ThemedTk
import threading
import glob


"""
Zenfoloio_Uploader:
  - Log into Zenfolio with user input
  - Retrieve existing Groups and PhotoSets
     - Only supports top level groups
     - Groups within groups are currently not supported
  - Provide user option to either select existing Groups and PhotoSets to upload to
  - Also provide option to enter new Group/PhotoSet names to be created
  - Retrieve list of supported files from user selected directory (includes subdirectories)
"""


# Upload files to PhotoSets
def upload_to_zenfolio():
    # Initialization
    target_group_found = False
    photoset_found = False

    # Get ID, password and directory from user input
    zf_id = en_id.get()
    zf_password = en_password.get()
    target_dir = sel_link.get()

    # Get list of files to upload from target directory
    files = get_files(target_dir)

    # Update Group and PhotoSet drop down lists
    group_name = sel_group.get()
    ps_title = sel_photoset.get()

    # Log in to Zenfolio
    info_box.insert('insert', 'Logging into Zenfolio..... ')
    info_box.see(END)
    api = PyZenfolio(auth={'username': zf_id, 'password': zf_password})
    try:
        api.Authenticate()
    except:
        info_box.insert('insert', 'Failed\nPlease Check ID & Password and try again\n\n')
        return
    else:
        info_box.insert('insert', 'Success!\n\n')

    # Search Id of target group
    for e in groups:
        if e['Title'] == group_name:
            group_id = e['Id']
            target_group_found = True
            break

    # Create group if target group does not exist
    if not target_group_found:
        new_group = api.CreateGroup(groups[0]['Id'], group={'Title': group_name})
        group_id = new_group['Id']
        info_box.insert('insert', 'New Group Created: ' + group_name + '\n\n')
        info_box.see(END)

    # Load all groups from the top level group (RootGroup)
    sets = api.LoadGroup(group_id, recursive=True)

    for elem in sets.Elements:

        # Check if PhotoSet already exists
        if elem['Title'] == ps_title:
            photoset_found = True
            info_box.insert('insert', 'Existing PhotoSet Found\n\n')
            info_box.see(END)

            # Upload files
            upload_files(elem, files, api)
            break

    # Create new PhotoSet if it doesn't already exist,
    # then set Title, Custom URL & Access Types appropriately
    if not photoset_found:
        # Create a new PhotoSet with title and custom url as PhotoSet name
        new_ps = api.CreatePhotoSet(group_id, photoset={'Title': ps_title, 'CustomReference': ps_title})
        info_box.insert('insert', "PhotoSet " + ps_title + " created\n\n")
        info_box.see(END)

        # upload files
        upload_files(new_ps, files, api)

    # Enable Upload Button when complete for subsequent upload sessions
    btn_upload.configure(state=NORMAL)


# Upload all files to selected PhotoSet. If files already exist in Photoset, delete existing photos
# prior to uploading new files to avoid duplicates
def upload_files(photoset, files, api):
    num_uploaded = 0
    status['text'] = str(num_uploaded) + " of " + str(len(files)) + " Files Uploaded"

    for i in files:
        # Retrieve file name from full path
        name = os.path.basename(i)

        # Load all items in selected PhotoSet
        photos = api.LoadPhotoSetPhotos(photoset['Id'])

        # If the photo already exists, delete the original photo
        for ph in photos:
            if ph['FileName'] == name:
                api.DeletePhoto(ph['Id'])
                break

        # Upload files
        info_box.insert('insert', "Uploading " + name + "\n")
        api.UploadPhoto(photoset, i)
        num_uploaded += 1
        progress['value'] = num_uploaded / len(files) * 100
        status['text'] = str(num_uploaded) + " of " + str(len(files)) + " Files Uploaded"
        info_box.see(END)

    # Output summary of uploads
    info_box.insert('insert', '\n' + photoset['PageUrl'] + '\n')
    info_box.insert('insert', '\n===   ' + str(num_uploaded) + ' Files Uploaded Successfully   ===\n\n')
    info_box.see(END)


# Cancel Button: Exit System
def end_program():
    sys.exit()


# Browse Button: Get target directory from user and display number of files found
def get_directory():
    path = filedialog.askdirectory()
    if not path:
        info_box.insert('insert', 'Directory Selection Cancelled\n\n')
        info_box.see(END)
    else:
        path = path + '/'
        sel_link.delete(0, END)
        sel_link.insert('insert', path)
        num_files = len(get_files(path))
        if num_files > 0:
            info_box.insert('insert', 'Directory Selected: ' + path + '\n')
            info_box.insert('insert', 'Number of Files Found: ' + str(num_files) + '\n\n')
            info_box.see(END)
            status.config(text="Directory Selected. Found " + str(num_files) + " Files")
            btn_upload.configure(state=NORMAL)
        else:
            info_box.insert('insert', 'Supported Files Not Found' + '\n')
            status.config(text="Supported Files Not Found")
            info_box.see(END)
            btn_upload.configure(state=DISABLED)
    sel_photoset.set(os.path.basename(os.path.normpath(path)))


# Output list of supported files in directory
def get_files(path):
    files = []

    # Zenfolio Supported file formats for images and videos
    # Add RAW files to the list if desired ("RAW", "DNG", "NEF", "XMP", "PDF", "PSD", "AI")
    file_formats = ["JPG", "GIF", "PNG", "TIF",
                    "ASF", "ASX", "AVI", "DIVX", "DV", "DVX", "M4V", "MOV", "MP4", "MPEG",
                    "MPG", "QT", "WMV", "3G2", "3GP", "3IVX", "3VX"]

    # get list of all supported files in selected directory
    for fmt in file_formats:
        files_found = glob.glob(path + "*." + fmt)
        for i in files_found:
            files.append(i)
    return files


def login_btn():
    y = threading.Thread(target=login_and_get_groups)
    y.start()


def login_and_get_groups():
    btn_login.configure(state=DISABLED)

    # Remind user to enter ID/PW if fields are empty
    if not en_id.get() or not en_password.get():
        messagebox.showwarning(title='Zenfolio Uploader',
                               message='Please Enter ID & Password')
        btn_login.configure(state=NORMAL)
        return

    status.config(text="Logging into Zenfolio")

    # Get ID, password and directory from user input
    zf_id = en_id.get()
    zf_password = en_password.get()

    # Log in to Zenfolio
    info_box.insert('insert', 'Logging into Zenfolio..... ')
    info_box.see(END)
    api = PyZenfolio(auth={'username': zf_id, 'password': zf_password})
    try:
        api.Authenticate()
    except:
        info_box.insert('insert', 'Failed\nPlease Check ID & Password and try again\n\n')
        status.config(text="Please Log into Zenfolio")
        btn_login.configure(state=NORMAL)
        return
    else:
        info_box.insert('insert', 'Success!\n\n')

    # Obtain list of top level elements/groups
    info_box.insert('insert', 'Retrieving Groups & PhotoSets..... ')
    info_box.see(END)
    user = api.LoadPublicProfile()
    g = api.LoadGroup(user.RootGroup.Id, recursive=True)
    el = g.Elements

    # Initialize the first element of the list with top level (RootGroup) name
    group_list = ['RootGroup']
    grp_set = {"Title": "RootGroup", "Id": g['Id'], "PhotoSet": []}

    # Get list of PhotoSets at RootGroup
    for p in el:
        if p['$type'] == 'PhotoSet':
            grp_set['PhotoSet'].append(p['Title'])
    groups.append(grp_set.copy())

    # Create a database called groups with Title/ID and PhotoSets
    # Does not support Groups within groups
    for e in el:
        if e['$type'] == 'Group':
            grp_set['Title'] = e['Title']
            grp_set['Id'] = e['Id']
            grp_set['PhotoSet'] = []
            i_group = api.LoadGroup(grp_set['Id'], recursive=True)
            group_list.append(e['Title'])
            for i in i_group.Elements:
                if i['$type'] == 'PhotoSet':
                    grp_set['PhotoSet'].append(i['Title'])
            groups.append(grp_set.copy())

    # Populate Groups drop down list and set default Group to be 'Uploads'
    sel_group['value'] = group_list
    sel_group.set('Uploads')

    # Also populate PhotoSet drop down list
    set_ps_list()

    # Finish up with appropriate user notification and enable buttons
    info_box.insert('insert', 'Complete\n\n')
    status.config(text="Please Select a Directory to Upload")
    btn_login.configure(state=NORMAL)
    btn_browse.configure(state=NORMAL)


# Populate PhotoSet drop down list from existing PhotoSets in selected group
def set_ps_list():
    for j in groups:
        if j['Title'] == sel_group.get():
            ps_list = j['PhotoSet']
            sel_photoset['value'] = ps_list
            break


# Upload Button: Log into Zenfolio and upload all items
def start_upload():
    # Get number of items found in selected directory from status label
    num_files = None
    for i in status['text'].split():
        if i.isdigit():
            num_files = int(i)

    # Confirm all necessary information has been captured
    if not en_id.get() or not en_password.get():
        messagebox.showwarning(title='Zenfolio Uploader',
                               message='Please Enter ID & Password')
    elif not sel_link.get():
        messagebox.showwarning(title='Zenfolio Uploader',
                               message='Please Select a Directory')
    elif not num_files:
        messagebox.showwarning(title='Zenfolio Uploader',
                               message='No Files to Upload\nPlease Select a Different Directory')
    else:
        btn_upload.configure(state=DISABLED)
        x = threading.Thread(target=upload_to_zenfolio)
        x.start()


# global variables
groups = []

# setup GUI elements
root = ThemedTk(theme="breeze")
root.title("Zenfolio Uploader")
root.resizable(width=False, height=False)
progress = Progressbar(root, orient=HORIZONTAL, length=420, mode='determinate')
status = Label(text="Please Log into Zenfolio", font="calibri 11 bold")
l_group = Label(text="Group", font=("calibri bold", 8))
sel_group = Combobox(width=15, textvariable='')
sel_group.bind("<<ComboboxSelected>>", lambda _: set_ps_list())
l_photoset = Label(text="PhotoSet", font=("calibri bold", 8))
sel_photoset = Combobox(width=38, textvariable='')
info_box = st.ScrolledText(root, width=60, height=20, font=("calibri", 10), padx=5, pady=5)
btn_frame = Frame()
btn_upload = Button(btn_frame, text="Upload", command=start_upload, state=DISABLED)
btn_close = Button(btn_frame, text="Close", command=end_program)
btn_upload.pack(side="left", fill=None, expand=False, padx=5)
btn_close.pack(side="left", fill=None, expand=False, padx=5)
l_link = Label(text="Directory", font=("calibri bold", 8))
frame_browse = Frame()
sel_link = Entry(frame_browse, font="calibri 11", width=46)
btn_browse = Button(frame_browse, text="Browse", command=get_directory, state=DISABLED)
sel_link.pack(side="left", padx=(0, 10))
btn_browse.pack(side="right")
frame_login = Frame()
frame_login_label = Frame()
l_id = Label(frame_login_label, text="Zenfolio ID", font=("calibri bold", 8))
en_id = Entry(frame_login, width=25, font="calibri 11")
l_password = Label(frame_login_label, text="Password", font=("calibri bold", 8))
en_password = Entry(frame_login, show="*", width=18, font="calibri 11")
btn_login = Button(frame_login, text="Log In", command=login_btn)
en_id.pack(side="left", padx=(0, 10))
en_password.pack(side="left")
btn_login.pack(side="right", padx=(10, 0))
l_id.pack(side="left", padx=(0, 143))
l_password.pack(side="left")

# place in GUI window
progress.grid(column=0, columnspan=3, pady=(30, 0))
status.grid(column=0, columnspan=3, pady=(10, 15))
frame_login_label.grid(column=0, columnspan=3, sticky=W, padx=15)
frame_login.grid(column=0, columnspan=3, sticky=W + E, padx=(10, 25), pady=(0, 5))
l_link.grid(column=0, columnspan=3, sticky=W, padx=15)
frame_browse.grid(column=0, columnspan=3, sticky=W + E, padx=(10, 25), pady=(0, 5))
l_group.grid(row=6, column=0, columnspan=1, sticky=W, padx=15)
l_photoset.grid(row=6, column=1, columnspan=2, sticky=W, padx=5)
sel_group.grid(row=7, column=0, columnspan=1, sticky=W + E, padx=10)
sel_photoset.grid(row=7, column=1, columnspan=2, sticky=W, padx=(0, 25))
info_box.grid(column=0, columnspan=3, padx=10, pady=(15, 10))
btn_frame.grid(column=0, columnspan=3, pady=(0, 10))

root.mainloop()
