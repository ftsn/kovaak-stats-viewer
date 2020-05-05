from tkinter import *
from tkinter import filedialog, messagebox
from os import listdir
from os.path import isfile, isdir, join
import requests
import datetime

if isdir(r'C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats'):
    stats_dir = r'C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats'
else:
    stats_dir = None


def upload_btn_clicked():
    try:
        to_upload = [join(stats_dir, f) for f in listdir(stats_dir) if isfile(join(stats_dir, f))]
    except TypeError:
        messagebox.showerror('Error', 'No directory set')
        return
    if username_input.get() == '' or password_input.get() == '':
        messagebox.showerror('Error', 'No username or password')
        return

    try:
        if start_input.get() != '':
            start = datetime.datetime.timestamp(datetime.datetime.strptime(start_input.get(), '%Y-%m-%d %H:%M:%S'))
        else:
            start = 0
        if end_input.get() != '':
            end = datetime.datetime.timestamp(datetime.datetime.strptime(end_input.get(), '%Y-%m-%d %H:%M:%S'))
        else:
            end = 2147483647
    except ValueError:
        messagebox.showerror('Error', 'Wrong start or end date')
        return

    payload = []
    for cur_file in to_upload:
        splitted = cur_file.split(' ')
        splitted_raw_datetime = splitted[len(splitted) - 2].split('-')
        formatted = '{} {}'.format(splitted_raw_datetime[0].replace('.', '-'),
                                   splitted_raw_datetime[1].replace('.', ':'))
        timestamp_cur = datetime.datetime.timestamp(datetime.datetime.strptime(formatted, '%Y-%m-%d %H:%M:%S'))
        if start <= timestamp_cur <= end:
            payload.append(('files', (cur_file, open(cur_file, 'rb'), 'text/csv')))
    if len(payload):
        res = requests.post('{}/{}/stats'.format('http://127.0.0.1:9999/api/users', username_input.get()), files=payload,
                            data={'silent_fail': False}, auth=(username_input.get(), password_input.get()))
        if res.status_code == 204:
            messagebox.showinfo('Error', '{} file(s) uploaded'.format(len(payload)))
        else:
            messagebox.showerror('The upload failed', 'More info: {}'.format(res.content.decode('utf-8')))

    else:
        messagebox.showwarning('Error', 'No files to upload with the current settings')


window = Tk()
window.title("Kovaak stats viewer Uploader")
window.geometry('450x300')
lbl1 = Label(window, text="1)Select the stats directory")
lbl1.grid(column=0, row=0, sticky='w')
lbl2 = Label(window, text="2)Choose your upload settings")
lbl2.grid(column=0, row=1, sticky='w')
lbl3 = Label(window, text="3)Click on the upload button to send the files")
lbl3.grid(column=0, row=2, sticky='w')
dir_label = Label(window, text="Directory: " if stats_dir is None else "Directory: {}".format(stats_dir))
dir_label.grid(column=0, row=3, sticky='w')


def change_dir():
    global stats_dir
    stats_dir = filedialog.askdirectory()
    dir_label.configure(text='Directory: {}'.format(stats_dir))


Button(window, text="Change your stats directory", command=change_dir).grid(column=0, row=4, sticky='w')

start_label = Label(window, text="Start date: ")
start_label.grid(column=0, row=5, sticky='w')
start_input = Entry(window, width=20)
start_input.grid(column=1, row=5)
end_label = Label(window, text="End date: ")
end_label.grid(column=0, row=6, sticky='w')
end_input = Entry(window, width=20)
end_input.grid(column=1, row=6)

username_label = Label(window, text="Username: ")
username_label.grid(column=0, row=7, sticky='w')
username_input = Entry(window, width=20)
username_input.grid(column=1, row=7)
password_label = Label(window, text="Password: ")
password_label.grid(column=0, row=8, sticky='w')
password_input = Entry(window, width=20, show='*')
password_input.grid(column=1, row=8)

Button(window, text="Upload", command=upload_btn_clicked).grid(column=0, row=9, sticky='w')
window.mainloop()
