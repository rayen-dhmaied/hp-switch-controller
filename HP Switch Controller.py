import sys
import subprocess
import pkg_resources

required = {'icmplib', 'getmac', 'netmiko', 'pandas'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)


from icmplib import multiping
from ipaddress import IPv4Network
from getmac import get_mac_address as MAC
from netmiko import ConnectHandler
from pandas import DataFrame
from os import system
import re

banner = '''
  _    _ _____     _____         _ _       _        _____            _             _ _           
 | |  | |  __ \   / ____|       (_) |     | |      / ____|          | |           | | |          
 | |__| | |__) | | (_____      ___| |_ ___| |__   | |     ___  _ __ | |_ _ __ ___ | | | ___ _ __ 
 |  __  |  ___/   \___ \ \ /\ / / | __/ __| '_ \  | |    / _ \| '_ \| __| '__/ _ \| | |/ _ \ '__|
 | |  | | |       ____) \ V  V /| | || (__| | | | | |___| (_) | | | | |_| | | (_) | | |  __/ |   
 |_|  |_|_|      |_____/ \_/\_/ |_|\__\___|_| |_|  \_____\___/|_| |_|\__|_|  \___/|_|_|\___|_|   
                                                                                                 
                                                                                                 '''

class Switch:
    
    def __init__(self, host, user, password):
        self.device = {'device_type': 'autodetect','ip': host,'username': user,'password': password ,'secret': password}
        self.conn = ConnectHandler(**self.device)
        self.conn.send_command('screen-length disable')
        self.version = self.get_version()
            
    def get_version(self):
        try :
            return re.search(r'H.*\+',self.conn.send_command('dis version').split('\n',3)[3].rsplit('\n',10)[0]).group()
        except:
            return 'Version error!'
            
    def get_uptime(self):
        try:
            return re.search(r'uptime.*(minutes|minute)',self.conn.send_command('dis version').split('\n',3)[3].rsplit('\n',10)[0]).group()
        except:
            return "couldn't get uptime"
        
    def interface_list(self):
        try:
            data = self.conn.send_command('dis interface brief').split('\n',12)[12].rsplit('\n',1)[0].split('\n')
            titles = ['Interface','Link','Speed','Duplex','Type','VLAN ID','Mac Address','IP Address']
            data_dic = { title : [] for title in titles }
            for line in data:
                x = line.split()
                i=0
                for column in x:
                    data_dic[titles[i]].append(column)
                    i = i+1
                data_dic[titles[i]].append('')
                data_dic[titles[i+1]].append('')
            mac = self.mac_list()
            for port in mac['Port']:
                x= port.split('/')
                data_dic['Mac Address'][int(x[2])-1]= mac['MAC Address'][mac['Port'].index(port)]
                mac_clean = data_dic['Mac Address'][int(x[2])-1].replace('-','')
                if mac_clean in hosts_dic['MAC']:
                    data_dic['IP Address'][int(x[2])-1] = hosts_dic['IP'][hosts_dic['MAC'].index(mac_clean)]
            df = DataFrame(data_dic)
            print(df)
            df.style.set_properties( ** {'text-align': 'center'}).to_excel(r'{} - interface_list.xlsx'.format(self.device['ip']), sheet_name = self.version, index = False)
        except:
            print('WARNING: Error occured while exracting interface list :/\n')


    def mac_list(self):
        try:
            data = self.conn.send_command('dis mac-address | exclude XGE1/0/49').split('\n',1)[1].rsplit('\n',3)[0].split('\n')
            titles = ['MAC Address','VLAN ID','State','Port','Aging Time']
            data_dic = { title : [] for title in titles }
            for line in data:
                x = line.split()
                i=0
                for column in x:
                    if i==0:
                        data_dic[titles[i]].append(column.upper())
                    else:
                        data_dic[titles[i]].append(column)
                    i = i+1
            return data_dic
        except:
            print('WARNING: Error occured while exracting mac-address list :/\n')

def IPsMac_gen(ran):
    system('cls')
    print('Loading data... Please wait :)')
    IPs = []
    for IP in IPv4Network(ran):
        IPs.append(str(IP))
    hosts = multiping(IPs,1,0.2,1)
    for host in hosts:
        if host.is_alive:
            hosts_dic['IP'].append(host.address)
            mac_addr = MAC(ip= host.address)
            if mac_addr is not None:
                hosts_dic['MAC'].append(mac_addr.upper().replace(':',''))
            else:
                hosts_dic['MAC'].append('')
            
def switch_register():
    while 1:
        print('Please add a valid switch configuration:\n')
        host = input('Host: ')
        user = input('Login: ')
        password = input('Password: ')
        try:
            switch = Switch(host,user,password)
            switches.append(switch)
        except:
            print('\nProblem with the provided switch! Please check and try again.\n')
            continue
        while 1:
            x = input('\nWould you like to add another switch ? (Y,N)\n')
            if x in ['N','n','Y','y']:
                break
        if x in ['N','n']:
            break
        else:
            print('\n')
            continue
    system('cls')
    
def menu():
    system('cls')
    print(banner)
    switch_register()
    while 1:
        print('1 - Get switch version & uptime')
        print('2 - Extract interface list')
        print('3 - Show hosts list')
        print('4 - Add another switch')
        print('5 - Update or add IP range (For Mac-IP binding)')
        print('6 - Exit\n')
        while 1:
            try:
                i = int(input('Please select an option: '))
                if i in range(1,7):
                    break
            except:
                print('Option number must be an integer and in range of the shown options!\n')
        print('\n')
        if i == 6:
            quit()
        if i == 5:
            ran = input('Please type valid IP range (Ex: 0.0.0.0/8): ')
            IPsMac_gen(ran)
        if i == 4:
            switch_register()
            continue
        if i == 3:
            s = 1
            for switch in switches:
                print(str(s)+' - '+switch.device['ip']+'@'+switch.device['username'])
                s = s+1
            print('\n')
            continue
        if len(switches) == 1:
            if i == 1:
                print(switches[0].device['ip']+' : '+switches[0].version+' and the '+switches[0].get_uptime())
            elif i == 2:
                print(switches[0].device['ip'])
                switches[0].interface_list()
            print('\n')
        else:
            while 1:
                try:
                    j = int(input('Please select switch number: (0 for all) '))
                    if 0<=j<=len(switches):
                        break
                except:
                    print('Switch number must be an integer and in range of provided switches number or 0!\n')
            if j==0:
                s = 0
                if i == 1:
                    print('\n')
                    for switch in switches:
                        print(str(s+1)+' - '+switch.device['ip']+' : '+switch.version+' and the '+switch.get_uptime())
                        s = s+1
                elif i == 2:
                    for switch in switches:
                        print('\n')
                        print(str(s+1)+' - '+switch.device['ip'])
                        switch.interface_list()
                        s = s+1
                print('\n')
            else:
                print('\n')
                if i == 1:
                    print(str(j)+' - '+switches[j-1].device['ip']+' : '+switches[j-1].version+' and the '+switches[j-1].get_uptime())
                elif i == 2:
                    print(str(j)+' - '+switches[j-1].device['ip'])
                    switches[j-1].interface_list()
                print('\n')


hosts_dic = {'IP':[],'MAC':[]}
switches = []
IPsMac_gen('192.168.1.0/24')
menu()
