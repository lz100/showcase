#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 19:37:13 2019

@author: lz
"""
import time
import multiprocessing as mp


class NewMp:
    """
    Multiprocess object, can know which processes are running and which are waiting.
    func = function to multiprocess
    mp_arg = the only argument to iterate in multiprocess
    fixed_arg = other args in function that is fixed in all process
    pool_size = how many processes to open
    timeout = how long to wait for a job until you call it failed
    flushtime = seconds you want the program to report status and fill in new jobs, should << than your job running time
    kwarg = other fixed key word args to function each iteration
    After creating object, call run() method to start the jobs
    """

    def __init__(self, func, mp_arg, *fixed_arg, pool_size=4, timeout=None, flushtime=5, **kwarg):
        self.func = func
        self.pool_size = pool_size
        if isinstance(mp_arg, list):
            self.mp_arg = mp_arg
        else:
            raise ValueError('must be a list')
        self.timeout = timeout
        self.fixed_arg = fixed_arg
        self.kwarg = kwarg
        self.res = []
        self._completed = set()
        self._failed = set()
        self.flushtime = flushtime

    def __str__(self):
        return (f'A self built multiprocess object. '
                f'Jobs completed {list(self._completed)} '
                f'Jobs failed {list(self._failed)} '
                )

    def __repr__(self):
        return 'A self built multiprocess object.'

    def completed(self):
        return list(self._completed)

    def failed(self):
        return list(self._failed)

    def status(self):
        """Returns a list, fisrt value how many completed, second how many failed"""
        return [len(self._completed), len(self._failed)]

    def run(self):
        _job_indices = {x for x in range(len(self.mp_arg))}
        _running = set()
        p = mp.Pool(self.pool_size)

        print(len(_job_indices), ' number of jobs, jobs waiting to run', _job_indices)
        print('pool size is', self.pool_size)
        _jobs = []
        time.sleep(3)
        _slots_remain = self.pool_size
        _submitted = set()

        while _job_indices != set():
            _slot_count = 0
            try:
                _slots_remain = self.pool_size - [job.ready() for job in _jobs].count(False)
            except:
                pass
            try:
                for i in _job_indices:
                    if _slot_count < _slots_remain:
                        _args = tuple([self.mp_arg[i]] + list(self.fixed_arg))
                        _jobs += [p.apply_async(self.func, args=_args, kwds=self.kwarg)]
                        _submitted.add(i)
                        _slot_count += 1
            except:
                pass
            for index, job in enumerate(_jobs):
                if job.ready():
                    self._completed.add(index)
                else:
                    _running.add(index)
            _job_indices -= _submitted
            print('jobs running', list(_running))
            print('jobs completed', list(self._completed))
            print('jobs waiting ', list(_job_indices))
            print('number waiting ', len(_job_indices))
            _running = set()
            time.sleep(self.flushtime)
        for i, job in enumerate(_jobs):
            try:
                job.wait(timeout=self.timeout)
                self.res.append(job.get(timeout=1))
            except:
                print('Job ', i, 'waited too long, time out')
                self._failed.add(i)
        if all([job.ready() and job.successful() for job in _jobs]):
            print('All jobs are successfully done')
        elif all([job.ready() for job in _jobs]):
            print('All jobs have been run but some failed')

########### test code
# mylist = [chr(x) for x in range(ord('a'), ord('k'))]
# def dummy(x):
#    try:
#        print('processing '+ str(x))
#    finally:
#        time.sleep(10)
#
# aaa = new_mp(dummy, mylist)
# aaa.run()
#
# bbb = new_mp(max, mylist, 'b', 'c')
# bbb.run()
# bbb.res
