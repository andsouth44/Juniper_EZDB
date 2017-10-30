#!/usr/bin/python
# Andrew Southard andsouth44@gmail.com
# www.packetconsulting.ca

import sqlite3
from pprint import pprint
from jnpr.junos import Device
from jnpr.junos.op.fpc import FpcHwTable
from mic import MicHwTable
from person import PersonTable
import getpass
import time

def insert(db, row):
	if row['personality'] == 'MX' or row['personality'] == 'SRX_BRANCH':
		db.execute('insert into Facts (hostname, last_reboot_reason, up_time, domain, fqdn, ifd_style,\
		model, personality, serialnumber, switch_style, vc_capable, version) values (?,\
		?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (row['hostname'], row['RE0']['last_reboot_reason'], row['RE0']['up_time'],\
		row['domain'], row['fqdn'], row['ifd_style'], row['model'], row['personality'],\
		row['serialnumber'], row['switch_style'], row['vc_capable'], row['version']))
		db.commit()

	elif row['personality'] == 'SWITCH' or row['model'][:3] == 'ACX':
		db.execute('insert into Facts (hostname, last_reboot_reason, up_time, domain, fqdn, ifd_style,\
		model, personality, serialnumber, switch_style, vc_capable, version, vc_mode) values (?,\
		?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (row['hostname'], row['RE0']['last_reboot_reason'], row['RE0']['up_time'],\
		row['domain'], row['fqdn'], row['ifd_style'], row['model'], row['personality'],\
		row['serialnumber'], row['switch_style'], row['vc_capable'], row['version'], row['vc_mode']))
		db.commit()

	else:
		raise TypeError('Unsupported device type')

def insert_fpc(db, row, hostname):
	db.execute('insert into FPCS (key, ver, model, pn, sn, desc) values (?, ?, ?, ?, ?, ?)',\
	(row['key'], row['ver'], row['model'], row['pn'], row['sn'], row['desc']))
	db.execute('update FPCS set hostname = ? where sn = ?', (hostname, row['sn']))
	db.commit()

def insert_mic(db, row, hostname):
	db.execute('insert into MICS (fpc, key, ver, model, pn, sn, desc) values (?, ?, ?, ?, ?, ?, ?)',\
	(row.key[0], row.key[1], row['ver'], row['model'], row['pn'], row['sn'], row['desc']))
	db.execute('update MICS set hostname = ? where sn = ?', (hostname, row['sn']))
	db.commit()

def insert_personality(db, row, hostname):
        db.execute('update Facts set personality = ? where hostname = ?', (row, hostname))
        db.commit()

def disp_rows(db):
    cursor = db.execute('select * from Facts order by hostname')
    for row in cursor:
        print('{}: {}: {}: {}: {}: {}: {}: {}: {}: {}: {}: {}: {}:'.format(row['hostname'], row['model'], row['last_reboot_reason'],\
         row['up_time'], row['domain'], row['fqdn'], row['ifd_style'],\
          row['personality'], row['serialnumber'], row['switch_style'], row['vc_capable'],\
           row['version'], row['vc_mode']))

def disp_rows_fpc(db):
    cursor = db.execute('select * from FPCS')
    for row in cursor:
        print('{}: {}: {}: {}: {}: {}: {}: {}:'.format(row['id'], row['hostname'], row['key'], row['ver'], row['model'],\
         row['pn'], row['sn'], row['desc']))

def disp_rows_mic(db):
    cursor = db.execute('select * from MICS')
    for row in cursor:
        print('{}: {}: {}: {}: {}: {}: {}: {}:'.format(row['id'], row['hostname'], row['fpc'], row['key'], row['ver'], row['model'],\
         row['pn'], row['sn'], row['desc']))

def disp_time(db):
    cursor = db.execute('select * from Time')
    for row in cursor:
        print row[0]


def main():
        db = sqlite3.connect('INSERT_db_name.db')
        db.row_factory = sqlite3.Row
        today = time.strftime('%c')
        print 'Script starting at ' + (time.strftime('%c'))
        print ('Create table Time')
        db.execute('drop table if exists Time')
        db.execute('create table Time (creation_time text)')
        db.execute('insert into Time (creation_time) values (?)', (today,))
        db.commit()
        print('Create table Facts')
        db.execute('drop table if exists Facts')
        db.execute('create table Facts (hostname text PRIMARY KEY UNIQUE, last_reboot_reason text, up_time text, domain text, fqdn text,\
	 ifd_style text, model text, personality text, serialnumber text,\
	switch_style text, vc_capable text, version text, vc_mode text)')
        db.commit()
        print('Create table FPCS')
        db.execute('drop table if exists FPCS')
        db.execute('create table FPCS (id INTEGER PRIMARY KEY, hostname text, key text, ver text, model text, pn text, sn text UNIQUE,\
desc text, FOREIGN KEY(hostname) REFERENCES Facts(hostname))')
        print ('Create table MICS')
        db.execute('drop table if exists MICS')
        db.execute('create table MICS (id INTEGER PRIMARY KEY, hostname text, fpc text, key text, ver text, model text, pn text, sn text UNIQUE,\
desc text, FOREIGN KEY(hostname) REFERENCES Facts(hostname))')
        db.commit()
        username = 'INSERT_user_id_here'
        password = 'INSERT_password_here'
        port = '22'


        print('Create rows')
        with open('INSERT_devicelist_file_name') as infile:
                for hostname in infile:
                    try:
                        print "Working on:", hostname,
                        dev = Device(host=hostname.strip(), user=username, password=password, port=port)
                        dev.open()
                        facts = dev.facts
                        insert(db, facts)
                        if facts['model'] == 'MX480':
                                fpcs = FpcHwTable(dev)
                                fpcs.get()
                                mics = MicHwTable(dev)
                                mics.get()
                                for fpc in fpcs:
                                        insert_fpc(db, fpc, hostname.strip())
                                for mic in mics:
                                        insert_mic(db, mic, hostname.strip())
                        if facts['model'] == 'MX5-T' or facts['model'] == 'MX10-T' or facts['model'] == 'MX40-T' or facts['model'] == 'MX80-T':
                                personality = PersonTable(dev)
                                personality.get()
                                mics = MicHwTable(dev)
                                mics.get()
                                for person in personality:
                                        insert_personality(db, person.personality, hostname.strip())
                                for mic in mics:
					if mic.sn == 'BUILTIN':
						continue
                                        insert_mic(db, mic, hostname.strip())
                        dev.close()
                        print "Completed:", hostname
                    except Exception,e: print "Error:", e
                    continue

        disp_time(db)
        print 'Script finished at ' + (time.strftime('%c'))


if __name__ == "__main__": main()
