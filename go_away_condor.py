#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 10:01:08 2017

@author: csh4

MAKE CONDOR GO AWAY

YOU ARE NOT WELCOME HERE

GOOD BYE
"""

import multiprocessing as mp
import numpy as np
import random
import gc
import subprocess
import time
import os
    
"""
Some functions to interface with the OS to figure out if Condor needs to go
"""

get_mem_p = ("for USER in $(ps haux | awk '{print $1}' | sort -u);"                                +
             "do "                                                                                 +
             "    ps haux | awk -v user=$USER '$1 ~ user { sum += $4} END { print user, sum; }'; " +
             "done")

get_cpu_p = ("for USER in $(ps haux | awk '{print $1}' | sort -u);"                                +
             "do "                                                                                 +
             "    ps haux | awk -v user=$USER '$1 ~ user { sum += $3} END { print user, sum; }'; " +
             "done")

def get_usage(resource):
    """
    Use subprocess.Popen to query the OS for resource usage

    @params 
        resource = 'mem_p' or 'cpu_p'
            Which resource to get the usage of by user   
    @returns a dictionary of resource usage by user
    """
    cmd = ""
    if    resource == "mem_p":    cmd = get_mem_p
    elif  resource == "cpu_p":  cmd = get_cpu_p
    else: raise ValueError(str(resource) +
                           " is not a valid input. Must be 'mem_p' or 'cpu_p'")
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    time.sleep(0.2)
    out, dct = str(popen.communicate()[0]).split("\\n")[1:-1], {}
    for line in out:
        separated = line.split()
        dct[separated[0]] = float(separated[1])
    return dct


"""
Some functions to busy the cores with to kick off Condor
"""

def inorder(x):
    """
    Check if the list is in order
    """
    i, j = 0, len(x)
    while i + 1 < j:
        if x[i] > x[i + 1]: return False
        i += 1
    return True

def bogo(x):
    """
    Bogosort the list x
    """
    while not inorder(x):
        random.shuffle(x)
    return x

def get_busy_bogo():
    """
    Figure out how effecient bogosort is
    
    Returns the average bogo time per item in a list, from 0 to 10000
    
    Spoiler alert: it's very inefficient! Bogo sort O(n) = (n-1)n!
    """
    n_arr, t_avg= [], []
    for n in range(1, 10000):
        n_t = []        
        for i in range(5):
            random_list = np.random.randint(0, high=100000, size=n)
            start_time = time.time()
            bogo(random_list)
            end_time   = time.time()
            n_t.append(end_time - start_time)
        t_avg.append(np.mean(n_t))
        n_arr.append(n)
        gc.collect()
    return np.array(t_avg)/np.array(n_arr)
    
"""
Functions to monitor usage and step in if necessary
"""
def busy_cores(n_cores, n_seconds):
    """
    Uses n_cores cores for a maximum of n_seconds seconds
    """
    processes = []
    for i in range(n_cores):
        processes.append(mp.Process(target=get_busy_bogo))
    for p in processes:
        p.start()           #Start the processes
    time.sleep(n_seconds)   #Wait n_seconds
    for p in processes:     
        p.terminate()       #End the processes
    gc.collect()            #Clean up
    
def check_usage(me=os.getlogin(), cpup_allowance=50, mem_allowance=15, slowdown=120,
                cores_to_use = mp.cpu_count(), verbose=True):
    """
    Check memory and cpu usage on this machine. If it exceeds the allowances
    given, busy the cores until it goes back down. 
    
    Default parameters are not too agressive but will get Condor to back down
    eventually. If you want more agressive monitoring, increase slowdown and
    decrease the allowances. 
    
    @params
        me = str
            Name of the user (PU ID) to not block the code usage of.
        cpup_allowance = int between 0 and 100*n_cores_total
            Total amount of cpu % use allowed for other users to use.
            This is core-percent units, so a max will be 100*n_cores
        mem_allowance = int between 0 and 100
            Percentage of memory other users are allowed to use
        slowdown = int
            Number of seconds to use the cores for
        cores_to_use = int
            Number of processes to spawn in order to convince Condor we're busy
        verbose = bool
            Whether or not to print out which user is hogging the CPUs
    """
    mem_usage, cpu_usage = get_usage("mem_p"), get_usage("cpu_p")
    mem_not_me, cpu_not_me = 0, 0
    for user in mem_usage:
        if user != me and user != "root":
            mem_not_me = mem_not_me + mem_usage[user]
            cpu_not_me = cpu_not_me + cpu_usage[user]
            if verbose and (mem_usage[user] > mem_allowance or
                            cpu_usage[user] > cpup_allowance):
                print(user + " is naughty!")
    if mem_not_me > mem_allowance or cpu_not_me > cpup_allowance:
        busy_cores(cores_to_use, slowdown)

def main(me=os.getlogin(), timeout=None, cpup_allowance=50, mem_allowance=15,
         slowdown=120, sampling=10, cores_to_use = mp.cpu_count(), verbose=True):
    """
    Monitor the memory usage by other users quietly. If it exceeds the allowed 
    usages, get Condor to leave by busying the cores.
    
    @params
        me = str
            Name of the user (PU ID) to not block the code usage of.
        timeout = int or None
            Maximum number of seconds to run this program before 
        cpup_allowance = int between 0 and 100*n_cores_total
            Total amount of cpu % use allowed for other users to use.
            This is core-percent units, so a max will be 100*n_cores
        mem_allowance = int between 0 and 100
            Percentage of memory other users are allowed to use
        sampling = int
            Number of seconds between checking what cores are in use
        slowdown = int
            Number of seconds to use the cores for
        cores_to_use = int
            Number of processes to spawn in order to convince Condor we're busy
        verbose = bool
            Whether or not to print out which user is hogging the CPUs
    """
    if verbose: print("Watching for Condor")
    if timeout == None:
        while True:
            check_usage(me,
                        cpup_allowance = cpup_allowance,
                        cores_to_use   = cores_to_use,
                        slowdown       = slowdown,
                        mem_allowance  = mem_allowance,
                        verbose        = verbose)
            time.sleep(sampling)
            if verbose: print(".", end="")
    else:
        for i in range(timeout):
            if i % sampling == 0:
                check_usage(me,
                            cpup_allowance = cpup_allowance,
                            cores_to_use   = cores_to_use,
                            slowdown       = slowdown,
                            mem_allowance  = mem_allowance,
                            verbose        = verbose)
            time.sleep(1)
            if verbose: print(".", end="")
                

if __name__ == "__main__":
    main()
