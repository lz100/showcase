#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 16:40:50 2018

Some basic functions that can be used in all scripts


"""

import os
import sys
import time

import click
import wrapt
import hashlib
import multiprocessing as mp
from datetime import datetime
from colorama import Fore
from decorator import decorator


def humansize(nbytes):
    """
    output byte size in human readable format
    modified from a stack overflow post
    credit: nneonneo@ https://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes
    
    """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < 5:
        nbytes /= 1024.
        i += 1

    if nbytes > 1024:
        print('''
              \x1b[1;31m▀█████████▄   ▄█     ▄██████▄
              \x1b[0;31m  ███    ███ ███    ███    ███  
              \x1b[1;33m  ███    ███ ███    ███    █▀   
              \x1b[1;32m ▄███▄▄▄██▀ ███   ▄███         
              \x1b[0;36m ▀███▀▀▀██▄ ███   ▀███ ████▄  
              \x1b[1;34m  ███    ██▄ ███    ███    ███   
              \x1b[1;35m  ███    ███ ███    ███    ███  
              \x1b[0;38m▄█████████▀  █▀     ████████▀  
                                                                                                                                                     
             ''')

    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return ('{} {}'.format(f, suffixes[i]))


def exists(dir_or_file):
    """
    check if the file or dir is there.
    Don't forget the dependency 'huamansize'
    """
    if os.path.exists(dir_or_file):
        if os.path.isfile(dir_or_file):
            print('The file size is ' + str(humansize(os.path.getsize(dir_or_file))))
        else:
            print('dir detected')
        return (True)
    else:
        print('The file or dir is not there')
        return (False)


# function
def stamp(level='INFO', note_after_time_stamp=None):
    """
    Define the time format for time stamp
    """
    time_format = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    stamp_format = f'[{str(level)}]: ' + time_format + ' '
    note_after_time_stamp = '0' if note_after_time_stamp == 0 else note_after_time_stamp
    if not note_after_time_stamp:
        return stamp_format
    else:
        return stamp_format + ' ' + str(note_after_time_stamp)


def shutdown(message, level="Error"):
    sys.stdout.flush()
    sys.stderr.flush()
    click.secho(stamp(level), fg='red', bold=True)
    click.secho(message=message, fg='red', bold=True)
    sys.exit(1)


def exit0(message, level="INFO"):
    sys.stdout.flush()
    sys.stderr.flush()
    click.secho(stamp(level), fg='blue', bold=True)
    click.secho(message=message, fg='blue', bold=True)
    sys.exit(0)


# A decorator class record time and duration
class wflog:
    '''
    A class of methods to log the workflow for the PD project
    some can be used as decorators. 
    '''

    # decorator
    @decorator
    def logging_mp(func, *args, **kwargs):
        """
        A self-defined logging method
        can work in multiprocess module
        This decorator uses decorator module, note:
            Need to run `inspect.getsource(func.__wrapped__)` to get source code
        """
        print(wflog.log_stamp('Start ' + func.__name__))
        timer_start = time.time()
        job = func(*args, **kwargs)
        print(wflog.log_stamp('End ' + func.__name__))
        # record running time
        timer_end = round(time.time() - timer_start, 2)
        if timer_end < 60:
            time_running = str(timer_end) + 's'
        elif timer_end >= 60 and timer_end < 3600:
            time_running = str(timer_end / 60) + 'mins'
        else:
            time_running = str(timer_end / 3600) + 'hours'
        print(Fore.WHITE + 'This process used: ' + time_running + Fore.RESET)
        return (job)

    # decorator

    def logging(*, time_stamp=True, level='INFO'):
        """
        This decorator uses wrapt and is more powerful,
        but does not work in multiprocess module
        It takes inputs so need to be used as @wflog.logging() as default
        can turn on/off time stamp
        can change debug level
        
        """
        levels = ['DEBUG', 'INFO']
        if level not in levels:
            print('Recommend DEBUG or INFO as your level.')

        @wrapt.decorator
        def log_wrapper(func, instance, args, kwargs):

            time_stamp and print(wflog.log_stamp('Start ' + func.__name__, level))
            timer_start = time.time()
            job = func(*args, **kwargs)
            time_stamp and print(wflog.log_stamp('End ' + func.__name__, level))
            # record running time
            timer_end = round(time.time() - timer_start, 2)
            if timer_end < 60:
                time_running = str(timer_end) + 's'
            elif timer_end >= 60 and timer_end < 3600:
                time_running = str(timer_end / 60) + 'mins'
            else:
                time_running = str(timer_end / 3600) + 'hours'
            print(Fore.WHITE + 'This process used: ' + time_running + Fore.RESET)
            return (job)

        return (log_wrapper)


class Md5:
    """For single file, use md5.file(),
       For more than one and compare existing md5s, use md5.files()
    """

    # optimal blocksize at 1m, 10m, 100m, >1g
    # 2**8 -> 0.25kb, 2**11 -> 2kb, 2**14 -> 16kb, 2**16 -> 64kb, 2**17 -> 128kb
    # tested by myself, can be slightly different on machines
    # 5-10% faster >1g files than md5sum on SSD.
    @staticmethod
    def file(filename):

        file_size = os.path.getsize(filename)
        blocksets = (128, 4096, 16384, 65536, 131072)
        # determine the blocksize
        i = n = 0
        while file_size > 1024000 * (10 ** n) and i <= 4:
            i += 1
            n += 1
        blocksize = blocksets[i - 1]
        # start to compute md5
        m = hashlib.md5()
        with open(filename, "rb") as f:
            while True:
                buffer = f.read(blocksize)
                if not buffer:
                    break
                m.update(buffer)
        return m.hexdigest()

    # to generate md5s for many files and check md5s
    @staticmethod
    def files(file_names, md5s=None, cpus=None, verbose=False):
        """
        1. generate md5 for a list of files.
        2. compare md5s from a list of files to a list of md5s if provided
        Note:
            will use n - 1 of your all CPUs by default
        3. return: a list, first item is a sub list of md5s or compare T/F
            dependent on if the compare mode is running, second item is if all
            md5s calculations are successful.
        """
        # checkers
        if not isinstance(file_names, (list, set)):
            raise TypeError('file_names need to be a list or set')
        else:
            file_names = list(file_names)

        # env setting
        cpus = cpus if cpus and isinstance(cpus, int) else mp.cpu_count() - 1

        if md5s is None:
            file_names = list(set(file_names))

        # wrapper function for the multiprocess to run
        def md5_mp(_file_names, _cpus, _verbose):
            _completed = set()
            _failed = set()
            with mp.Pool(_cpus) as p:
                _jobs = [p.apply_async(Md5.file, (file_name,)) for file_name in _file_names]
                _num_job_running = len(_jobs)
                _res = [None for x in range(_num_job_running)]
                if _verbose: print(
                    stamp('INFO', 'Checking md5 for {} files in {} threads'.format(_num_job_running, _cpus)))
                while not all([job.ready() for job in _jobs]):
                    for index, job in enumerate(_jobs):
                        if job.ready():
                            _completed.add(index)
                    if _verbose: print(stamp('INFO', 'Finished job: {}'.format(_completed)))
                    time.sleep(5)
                else:
                    for index, job in enumerate(_jobs):
                        if job.ready() and not job.successful():
                            _failed.add(index)
                            _failed_names = [_file_names[file] for file in _failed]

            if len(_failed) == 0:
                if _verbose: print('No job failed')
                _all_done = True
            else:

                print(stamp('WARN', f'Md5 failed: {_failed_names}'))
                _all_done = False
            for index, job in enumerate(_jobs):
                if job.ready() and job.successful():
                    _res[index] = job.get()
            return _res, _all_done

        # Run in different modes
        if md5s is not None:

            if len(file_names) == len(md5s):
                for a in md5s:
                    print(type(a))
                print(md5s)
                if len(set(md5s)) > len(set(file_names)):
                    print(stamp('WARN', 'Duplications detected but some identical paths are given different md5s'))
                res = md5_mp(file_names, cpus, verbose)
                if verbose: print(stamp('INFO', 'md5s done computing, now compare'))
                compare = [j == md5s[i] for i, j in enumerate(res[0])]
                return compare, res[1]  # sorted order but still in the right pairs
            else:
                raise ValueError('numbers of file and numbers of md5 do not match')
        else:
            return md5_mp(file_names, cpus, verbose)
