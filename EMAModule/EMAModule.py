import csv
import numpy as np
import os
from pathlib import Path
import pandas as  pd
import heartpy as hp
from datetime import datetime
import json
import random

from .EMA_Trigger_SampleSlotDensity import EMATriggerDensity
from .EMA_Trigger_WatchWear import EMATriggerWatch
from .EMA_FeatureExtraction import FeatureExtractionModule
from .EMA_Trigger_LastTrigger import EMATriggerLastTriggerTime


class MainModule():
    def __init__(self):
        pass

    def main(self, datapath, filepath, user_id, realtime=True, sleep = False, debug=False):
        #filepath:       Directory in which distribution files are or will be stored
        #datafile:        Address to the new coming 2m window signals including ppg
        #user_id:         e.g. "uniterct446"
        #realtime:        whether the signal is real time or it's delayed signal, which was stored on the watch
        #sleep:           Whether the user is asleep or not

        #do not notify between midnight and 7am:
        #rest_time = datetime.strptime(str(datapath)[-23:-4], '%Y-%m-%d-%H-%M-%S').hour < 7
        #load data
        raw_data = pd.read_csv(datapath, header=0, delimiter='\t')
        mod = FeatureExtractionModule(raw_data)
        headers, ppg_features = mod.FeatureExtract()

        watch_mod = EMATriggerWatch(raw_data, None, user_id, filepath)
        watch_trigger = watch_mod.return_trigger()

        json_filename = filepath / ('userinfo_'+user_id+'.json')
        if not os.path.exists(json_filename):
            with open(json_filename, 'w') as f:
                f.write(json.dumps({}))

        #print('Watch trigger is', watch_trigger)

        dense_mod = EMATriggerDensity(raw_data, ppg_features, user_id, filepath)
        dense_trigger = dense_mod.return_trigger()

        #print('Dense trigger is', dense_trigger)

        lasttime_mod = EMATriggerLastTriggerTime(raw_data, ppg_features, user_id, filepath)
        lasttime_trigger = lasttime_mod.return_trigger()

        #print('Last Time trigger is', lasttime_trigger)

        # Trigger every 2 hours of wearing the watch.
        if debug:
            print('Wearing watch trigger', watch_trigger)
            print('Last EMA time < 2 hours trigger', lasttime_trigger)
            print('Real time', realtime)
            print('Sleep', sleep)
        if watch_trigger and lasttime_trigger and realtime:
            triggered = True
        else:
            triggered = False

        # logfile = open(filepath / ("log/"+user_id+".log"), 'w')
        # logfile.write('watch trigger: ' + str(watch_trigger) + '\n')
        # logfile.write('lasttime_trigger: ' + str(lasttime_trigger) + '\n')
        # logfile.write('realtime: ' + str(realtime) + '\n')
        # logfile.write('sleep: ' + str(sleep) + '\n')
        # logfile.close()


        # Save the sample file alongside whether EMA is triggered or not to Sample_userid file
        Sample = ppg_features.copy()
        # save_features_to_file(Sample, True, filepath)
        Sample.insert(0,raw_data.loc[0].timestamp)

        if not((filepath / ("Sample_"+user_id+".csv")).exists()):
            f_list = headers
            f_list.insert(0,'timestamp')
            f_list.append('triggered')
            f_list.append('filename')
            with open(filepath / ('Sample_'+user_id+'.csv'), 'a', newline='') as file:
                file_writer = csv.writer(file, delimiter=',')
                file_writer.writerow(f_list)

        SS = pd.read_csv(filepath / ('Sample_'+user_id+'.csv'))

        if SS.shape[1]==16:
            SS['realtime'] = [-1]*SS.shape[0]
            SS['sleep'] = [-1]*SS.shape[0]
            SS.to_csv(filepath / ('Sample_'+user_id+'.csv'), sep = ',', index = False)

        Sample.append(int(triggered))
        #Sample.append(str(datapath)[-40:])
        locs = str(datapath).find('data_unite2rct')
        Sample.append(str(datapath)[locs:])
        Sample.append(int(realtime))
        Sample.append(int(sleep))

        # Update user_info file based on decision made and data received
        user_info = json.load(open(json_filename))

        if triggered == True:
            current_timestamp = datetime.fromtimestamp(raw_data.timestamp.iloc[-1]/1000).timestamp()
            if 'dailyTotalTrigger' not in user_info:
                user_info['dailyTotalTrigger'] = 0
            if 'lastTrigger' not in user_info:
                user_info['lastTrigger'] = 0
            old_timestamp = user_info['lastTrigger']

            if datetime.fromtimestamp(old_timestamp).day == datetime.fromtimestamp(current_timestamp).day:
                user_info['dailyTotalTrigger'] += 1
            else:
                user_info['dailyTotalTrigger'] = 1

            user_info['lastTrigger'] = current_timestamp
            with open(json_filename, 'w') as f:
                f.write(json.dumps(user_info))

        with open(filepath / ('Sample_'+user_id+'.csv'), 'a', newline='') as file:
            file_writer = csv.writer(file, delimiter=',')
            file_writer.writerow(Sample)

        return triggered


    def e4device_trigger(self, datapath, filepath, user_id, realtime=True, sleep = False, debug=False):
        #filepath:       Directory in which distribution files are or will be stored
        #datafile:        Address to the new coming 2m window signals including ppg
        #user_id:         e.g. "uniterct446"
        #realtime:        whether the signal is real time or it's delayed signal, which was stored on the watch
        #sleep:           Whether the user is asleep or not
        triggered = True

        time_between_trigger = 2*3600 # 2 hours difference, number of seconds
        current_timestamp = datetime.now().timestamp()

        json_filename = filepath / ('userinfo_'+user_id+'.json')
        if not os.path.exists(json_filename):
            with open(json_filename, 'w') as f:
                print('Creating user info at', json_filename)
                f.write(json.dumps({}))


        try:
            user_info = json.load(open(json_filename))
        except:
            user_info = {}

        if 'lastTrigger' in user_info:
            print('Last trigger in user_info')
            print(current_timestamp, user_info['lastTrigger'])
            if current_timestamp - int(user_info['lastTrigger']) >= time_between_trigger:
                triggered = True
            else:
                triggered = False


        if triggered == True:
            if 'dailyTotalTrigger' not in user_info:
                user_info['dailyTotalTrigger'] = 0
            if 'lastTrigger' not in user_info:
                user_info['lastTrigger'] = 0
            old_timestamp = user_info['lastTrigger']

            if datetime.fromtimestamp(old_timestamp).day == datetime.fromtimestamp(current_timestamp).day:
                user_info['dailyTotalTrigger'] += 1
            else:
                user_info['dailyTotalTrigger'] = 1

            user_info['lastTrigger'] = current_timestamp
            with open(json_filename, 'w') as f:
                f.write(json.dumps(user_info))

        return triggered



#%%
if __name__ == "__main__":
    mod = MainModule()
    datapath = '/Users/james/Documents/UCI_Research/MicroRCT/Github/UNITE/EMA_Triggering_Module/test_data/data_uniterct552-2020-11-09-08-41-01.csv'
    filepath = Path('/Users/james/Documents/UCI_Research/MicroRCT/Github/UNITE/EMA_Triggering_Module/test_data/test_file_path')
    user_id = 'uniterct552'
    mod.main(datapath, filepath, user_id)