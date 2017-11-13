#!/usr/bin/env python3
import datetime as dt
import shutil
from multiprocessing import Pool

from network_analysis import NetworkAnalysis
from network_parser import NetworkParser
from settings import *
from xml_parser import XMLParser

SNAPSHOT_TIME = dt.datetime.now()
OLDEST_TIME = dt.datetime(2000, 1, 1)
ONE_YEAR = 365
ONE_MONTH = 30
TIME_INCR = dt.timedelta(days=30)


def get_data_files(dir_path=None):
    if dir_path is None:
        dir_path = "../dataRaw"

    print("Getting files from " + dir_path)

    ret = {"current": set(), "full": set()}
    for f in os.listdir(dir_path):
        rel_path = os.path.join(dir_path, f)
        if os.path.isfile(rel_path):
            if f.endswith("_current.xml"):
                ret['current'].add(rel_path)
            elif f.endswith("_full.xml"):
                ret['full'].add(rel_path)
    print(str(len(ret["current"])) + " current files")
    print(str(len(ret["full"])) + " full files")
    return ret


def get_time():
    return SNAPSHOT_TIME


# Do the actual processing for time series
def time_process(data_file):
    curr_time = dt.datetime.now()
    # run loop
    fobj = XMLParser(data_file, curr_time)
    lim = fobj.find_oldest_time()
    while curr_time > lim:
        curr_time -= TIME_INCR
        print('running time analysis for ' + str(curr_time.date()))
        fobj.update_time(curr_time)
        d = fobj.parse_to_dict()
        if d:
            net = NetworkParser(d)
            print("Analyzing File " + data_file + ' at time ' + str(curr_time.date()))
            na = NetworkAnalysis(net.G, os.path.basename(data_file), output_path, curr_time.date())

            basic = na.d3dump(public_out_path, str(curr_time.date()))

            public_data_output = public_data + na.fileName + "/"
            if generate_data:  # write out decentralized results
                na.write_permanent_data_json(public_data_output, str(curr_time.date()), basic)

    print("Completed Analyzing: " + data_file)


def main():
    # Clear output
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    if os.path.exists(public_out_path):
        shutil.rmtree(public_out_path)
    os.makedirs(public_out_path)

    # Setting datafiles to the correct files
    data_files = set()
    parse_set = get_data_files().items()
    for (k, v) in parse_set:
        if time_series:  # If doing a time series, only worth checking out full stuff
            if k == 'full':
                data_files.update(v)
            else:
                continue
    if no_game:
        data_files = {f for f in data_files if no_game_name in f}
    if performance_mode:
        def check(f):
            for big in large_wikis:
                if big in f:
                    return False

            return True

        data_files = {f for f in data_files if check(f)}

    data_files = sorted(data_files, key=os.path.getsize)[::-1]

    # Processing the data_files
    with Pool(threads, maxtasksperchild=1) as pool:
        print(str(threads) + " Threads")
        pool.map(time_process, data_files)
        pool.close()
        pool.join()


# Main method
if __name__ == '__main__':
    main()  # Runs the actual processing.
