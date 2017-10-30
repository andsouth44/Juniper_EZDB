#!/usr/bin/python
# Andrew Southard andsouth44@gmail.com
# www.packetconsulting.ca

from Tkinter import *
from ttk import *
import ttk
import sqlite3
import subprocess
import os
from pprint import pprint
import paramiko

def main():

    #used in get_db_file function
    _SNDB_filename_ = 'INSERT_DB_Name.db'

    #retrieve db file from server when DB interface is run for the first time on a pc
    def get_db_file_new():
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print 'Opening connection to remote server'
            ssh.connect('INSERT_IP_of_server', username='INSERT_username', password='INSERT_password', timeout = 10)
        except:
            print 'Unable to connect'
            return
        try:
            print 'Opening sftp'
            sftp = ssh.open_sftp()
        except:
            print 'Unable to open sftp'
            return
        try:
            print 'Downloading latest version of DB'
            sftp.get('INSERT_path_to_db/INSERT_DB_Name.db', (os.path.join((os.getcwd()), _SNDB_filename_)))
        except:
            print 'Unable to download latest DB file'
            return
        sftp.close()
        ssh.close()
        print 'Update complete'

    # determines if the db file exists on the pc and if not runs 'get_db_file_new' to retrieve it from server
    if not os.path.isfile(os.path.join((os.getcwd()), 'INSERT_DB_Name.db')):
        get_db_file_new()

    # opens an sql connection to the db
    db = sqlite3.connect('INSERT_DB_Name.db')

    # retrieves time the db was created by accessing the timestamp in the db
    def get_time(db):
        db.text_factory = str
        cursor = db.execute('select * from Time')
        for row in cursor:
            return row[0]

    # assigns db timestamp time to _time variable
    _time = get_time(db)

    #retrieve db file from server as a result of 'Update DB' button being clicked. Also updates
    # db version label
    def get_db_file():
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print 'Opening connection to remote server'
            ssh.connect('INSERT_IP_of_server', username='INSERT_username', password='INSERT_password', timeout = 10)
        except:
            print 'Unable to connect'
            return
        try:
            print 'Opening sftp'
            sftp = ssh.open_sftp()
        except:
            print 'Unable to open sftp'
            return
        try:
            print 'Downloading latest version of DB'
            sftp.get('INSERT_path_to_db/INSERT_DB_Name.db', (os.path.join((os.getcwd()), _SNDB_filename_)))
        except:
            print 'Unable to download latest DB file'
            return
        sftp.close()
        ssh.close()
        _time2 = get_time(db)
        entry4.delete(0, END)
        entry4.insert(0, (_time2))
        print 'Update complete'
        print ''

    # retrieves data from db based on contents of combo boxes. Triggered by 'Search' button click
    def retrieve():
        db.text_factory = str
        try:
            cursor = db.execute('select {} from {} where {} = ?'.format(combobox3.get(), combobox1.get(),\
                                                                        combobox2.get()), (combobox4.get(),))
            for row in cursor:
                if combobox1.get()=='Facts' and combobox3.get()=='*':
                    print ('Facts\nHostname:\t{}\nReboot Reason:\t{}\nUptime:\t\t{}\nDomain:\t\t{}\nFQDN:\t\t{}\
\nInt Style:\t{}\nModel:\t\t{}\nPersonality:\t{}\nSerial Number:\t{}\nSwitch Style:\t{}\nVC Capable:\t{}\nVersion:\
\t{}\nVC Mode:\t{}\n'.format(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]),\
                             str(row[7]), str(row[8]), str(row[9]), str(row[10]), str(row[11]), str(row[12])))
                elif combobox1.get()=='FPCS' and combobox3.get()=='*':
                    print ('Hostname:\t{}\nFPC Number:\t{}\nVersion:\t{}\nModel:\t\t{}\nPart Number:\t{}\nSerial\
Number:\t{}\nDescription:\t{}\n'.format(str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]),\
                                        str(row[7])))
                elif combobox1.get()=='MICS' and combobox3.get()=='*':
                    print ('Hostname:\t{}\nFPC Number:\t{}\nMIC Number:\t{}\nVersion:\t{}\nDescription:\t{}\nPart\
Number:\t{}\nSerial Number:\t{}\n'.format(str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]),\
                                          str(row[7])))
                else:
                    print str(row[0])
        except:
            print 'Item not found or input error.'
        print ('\n')

    # used to populate combobox1,2,3 selection options based on the 'Select DB table to search'
    # selection. Triggered by a combobox1 selection
    def set_columns(event):
        if combobox1.get()=='FPCS':
            combobox2.config(values = _FPCSColumns_)
            combobox3.config(values = _FPCSColumns2_)
            retrieve_column_data_get('')
        elif combobox1.get()=='MICS':
            combobox2.config(values = _MICSColumns_)
            combobox3.config(values = _MICSColumns2_)
            retrieve_column_data_get('')
        elif combobox1.get()=='Facts':
            combobox2.config(values = _FactsColumns_)
            combobox3.config(values = _FactsColumns2_)
            retrieve_column_data_get('')
        else:
            print 'error'

    # populates 'Select value to search for' by retrieving all options from db based on current
    # selections in combobox1,2
    def retrieve_column_data(db, column, table):
        try:
            cursor = db.execute('select {} from {}'.format(column, table))
            colnames = [row[0] for row in cursor]
            colnames = sorted(list(set(colnames)))
            colnames = [x for x in colnames if x is not None]
            combobox4.config(values = colnames)
        except:
            print "Column not found"

    # used to call retrieve_column_data because retrieve_column_data cannot be called
    # directly from set_columns. Triggered by a combobox2 or 1 selection
    def retrieve_column_data_get(one):
    	retrieve_column_data(db, combobox2.get(), combobox1.get())

    # open help file for windows or Mac devices
    def open_help():
            if os.name == 'posix':
                    subprocess.call(('open', 'Help.txt'))
            else:
                    os.startfile('Help.txt')


    #test function
    #def callback():
            #print ('hello')
            #print (combobox3.get(), combobox1.get(), combobox2.get(), entry3.get())

    # Creates main TKInter root window
    root = Tk()
    root.title('EZDB 1.1')
    root.configure(bg = 'white')
    root.resizable(False, False)

    # opens the 2 logo files and shrinks them to fit
    pclogo = PhotoImage(file = 'pclogo.gif')
    axlogo = PhotoImage(file = 'Your_Logo.gif')
    small_axlogo = axlogo.subsample(5, 5)
    small_pclogo = pclogo.subsample(5, 5)

    # creates style and assigns canned theme 'clam' for T Buttons
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('new.TButton', font=('Trebuchet', 10), height = 1)


    # creates list of variables for use in combobox selections. Used by 'set_columns' function
    _FPCSColumns_ = ('hostname', 'key', 'ver', 'model', 'pn', 'sn', 'desc')

    _FPCSColumns2_ = ('*', 'hostname', 'key', 'ver', 'model', 'pn', 'sn', 'desc')

    _MICSColumns_ = ('hostname', 'fpc', 'key', 'ver', 'model', 'pn', 'sn', 'desc')

    _MICSColumns2_ = ('*', 'hostname', 'fpc', 'key', 'ver', 'model', 'pn', 'sn', 'desc')

    _FactsColumns_ = ('hostname', 'last_reboot_reason', 'up_time', 'domain', 'fqdn', 'ifd_style', 'model', 'personality',\
                   'serialnumber', 'switch_style', 'vc_capable', 'version', 'vc_mode')

    _FactsColumns2_ = ('*', 'hostname', 'last_reboot_reason', 'up_time', 'domain', 'fqdn', 'ifd_style', 'model', 'personality',\
                   'serialnumber', 'switch_style', 'vc_capable', 'version', 'vc_mode')

    # creates various TKInter labels, comboboxes and entry widgets as children of root TK window

    # Packet Consulting logo label
    label = ttk.Label(root)
    label.img = small_pclogo
    label.config(image = label.img, borderwidth = 0)
    label.grid(row = 7, column = 1, sticky = 'e', padx = 5, pady = 2)

    #Axia logo label
    label2 = ttk.Label(root)
    label2.img = small_axlogo
    label2.config(image = label2.img, borderwidth = 0)
    label2.grid(row = 7, column = 0, sticky = 'w', padx = 5, pady = 2)

    # Copyright label
    label9 = ttk.Label(root, text = 'Packet Consulting Inc.', font = ('Trebuchet', 8))
    label9.grid(row = 8, column = 0, sticky = 'w', padx = 5, pady = 5)
    label9.configure(background = 'white')

    # SN EZDB title label
    label3 = ttk.Label(root, text = 'EZDB', font =('Trebuchet', 26))
    label3.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5)
    label3.configure(background = 'white')

    # Label for 'select DB table to search' combobox1
    label5 = ttk.Label(root, text = 'Select DB Table to search:', font = ('Trebuchet', 10))
    label5.grid(row = 2, column = 0, sticky = 'sw', padx = 5, pady = 2)
    label5.configure(background = 'white')

    # combobox for 'Select DB table to search'. Values set from list. Defaults to 'Facts'.
    # set_columns is run when this box selected
    combobox1 = ttk.Combobox(root, width = 24)
    combobox1.grid(row = 3, column = 0, sticky = 'nw', padx = 5, pady = 2)
    combobox1.config(values = ('Facts', 'FPCS', 'MICS'))
    combobox1.insert(0, 'Facts')
    combobox1.bind('<<ComboboxSelected>>', set_columns)

    # Label for 'Select column to search' combobox2
    label6 = ttk.Label(root, text = 'Select column to search:', font = ('Trebuchet', 10))
    label6.grid(row = 2, column = 1, sticky = 'sw', padx = 5, pady = 2)
    label6.configure(background = 'white')

    # combobox for 'Select column to search'. Values retrieved from _FactsColumns_ list
    # at start up then uses retrieve_column_data_get. Defaults to 'hostname'.
    combobox2 = ttk.Combobox(root, width = 24)
    combobox2.grid(row = 3, column = 1, sticky = 'nw', padx = 5, pady = 2)
    combobox2.config(values = _FactsColumns_)
    combobox2.insert(0, 'hostname')
    combobox2.bind('<<ComboboxSelected>>', retrieve_column_data_get)

    # Label for 'Select value to search for' combobox 4
    label7 = ttk.Label(root, text = 'Select value to search for:', font = ('Trebuchet', 10))
    label7.grid(row = 4, column = 0, sticky = 'sw', padx = 5, pady = 2)
    label7.configure(background = 'white')

    # combobox for 'Select value to search for'. Values retrieved by retrieve_column_data based
    # on selections in other comboboxes
    combobox4 = ttk.Combobox(root, width = 24)
    combobox4.grid(row = 5, column = 0, sticky = 'nw', padx = 6, pady = 2)
    retrieve_column_data(db, combobox2.get(), combobox1.get())

    # Label for 'Select column to display' combobox3
    label4 = ttk.Label(root, text = 'Select column to display (* for all):', font = ('Trebuchet', 10))
    label4.grid(row = 4, column = 1, sticky = 'sw', padx = 5, pady = 2)
    label4.configure(background = 'white')

    # combobox for 'Select column to display'. Values set from _FactsColumns_ list. Defaults to *
    combobox3 = ttk.Combobox(root, width = 24)
    combobox3.grid(row = 5, column = 1, sticky = 'w', padx = 5, pady = 3)
    combobox3.config(values = _FactsColumns2_)
    combobox3.insert(0, '*')

    # Label for 'DB Version' entry4 widget
    label8 = ttk.Label(root, text = 'DB Version:', font = ('Trebuchet', 10))
    label8.grid(row = 1, column = 0, stick = 'w', padx = 5, pady = 5)
    label8.configure(background = 'white')

    # entry widget displays timestamp retrieved from current db file
    entry4 = ttk.Entry(root, width = 22, font = ('Trebuchet', 8))
    entry4.grid(row = 1, column = 0, sticky = 'e', padx = 5, pady = 5)
    entry4.insert(0, (_time))

    # Search button. Triggers retrieve function.
    button = ttk.Button(root, text = 'Search', width = 6, style = 'new.TButton', command = lambda: retrieve())
    button.grid(row = 6, column = 0, columnspan = 2, padx = 5, pady = 5)

    # Help button. Opens Help text file.
    button2 = ttk.Button(root, text = '?', width = 1, style = 'new.TButton', command = lambda: open_help())
    button2.grid(row = 0, column = 1, sticky = 'ne', padx = 5, pady = 5)

    # Update DB button. Triggers get_db_file function.
    button3 = ttk.Button(root, text = 'Update DB', style = 'new.TButton', width = 10, command = lambda: get_db_file())
    button3.grid(row = 1, column = 1, sticky = 'w', padx = 5, pady = 5)

    # starts main TKInter loop
    root.mainloop()

if __name__ == "__main__": main()
