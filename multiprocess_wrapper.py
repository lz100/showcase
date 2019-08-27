#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 19:37:13 2019

@author: lz
"""
import time
import multiprocessing
import click
import universal_functions as uf


class mp:
    """
    Multiprocess object, can know which processes are running and which are waiting.
    func = function to multiprocess
    mp_arg = the only argument to iterate in multiprocess
    fixed_arg = other args in function that is fixed in all process
    pool_size = how many processes to open
    timeout = how long to wait for a job until you call it failed
    job_names = jobs names in a list of strings with the same length as mp_arg
    flushtime = seconds you want the program to report status and fill in new jobs, should << than your job running time
    kwarg = other fixed key word args to function each iteration
    After creating object, call run() method to start the jobs
    """

    def __init__(self, func, mp_arg, *fixed_arg, pool_size=None, timeout=None, job_names=[], flushtime=5, **kwarg):
        self.func = func
        if isinstance(mp_arg, list):
            self.mp_arg = mp_arg
        else:
            raise ValueError('mp_arg must be a list')

        if isinstance(pool_size, int):
            self.mp_arg = mp_arg
        else:
            raise ValueError('must be an integer')

        if isinstance(job_names, list):
            if job_names and len(job_names) == len(mp_arg):
                self.job_names = job_names
            else:
                self.job_names = []
        else:
            raise ValueError('job_names must be a list')

        if not pool_size:
            self.pool_size = multiprocessing.cpu_count()
        else:
            self.pool_size = pool_size

        self.timeout = timeout
        self.fixed_arg = fixed_arg
        self.kwarg = kwarg
        self.res = []
        self._completed = set()
        self._failed = set()
        self.flushtime = flushtime
        self.jobs = None

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
        """Returns a list, first value how many completed, second how many failed"""
        return [len(self._completed), len(self._failed)]

    def run(self):
        _job_indices = {x for x in range(len(self.mp_arg))}
        _running = set()
        p = multiprocessing.Pool(self.pool_size)
        uf.info(f' Number of jobs {len(_job_indices)}', True)
        uf.info(f'Pool size is {self.pool_size}', True)
        _jobs = []
        time.sleep(3)
        _slots_remain = self.pool_size
        _submitted = set()
        _timer = time.perf_counter()

        with click.progressbar(length=len(self.mp_arg)) as bar:
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
                try:
                    time_last_flush
                except:
                    time_last_flush = self.flushtime
                if time.time() - time_last_flush < self.flushtime + 0.1:
                    pass
                else:
                    print_run = [f'{index}{self.job_names[index] if self.job_names else ""}' for index in list(_running)]
                    print_completed = [f'{index}{self.job_names[index] if self.job_names else ""}' for index in list(self._completed)]
                    print_waiting = [f'{index}{self.job_names[index] if self.job_names else ""}' for index in list(_job_indices)]
                    uf.info(f'jobs running: {print_run if len(print_run) <= 15 else len(print_run)}', True)
                    uf.info(f'jobs completed: {print_completed if len(print_completed) <= 15 else len(print_completed)}', True)
                    uf.info(f'jobs waiting: {print_waiting if len(print_waiting) <= 15 else len(print_waiting)}', True)
                    uf.info(f'number waiting: {len(_job_indices)}', True)
                    bar.update(len(self._completed))
                    print("")
                    time_last_flush = time.time()
                _running = set()

            # behavior after all jobs submitted
            while len(self._completed) != len(self.mp_arg):
                for index, job in enumerate(_jobs):
                    if job.ready():
                        self._completed.add(index)
                    else:
                        _running.add(index)

                try:
                    time_last_flush
                except:
                    time_last_flush = self.flushtime
                if time.time() - time_last_flush < self.flushtime + 0.1:
                    pass
                else:
                    print_run = [f'{index}{self.job_names[index] if self.job_names else ""}' for index in list(_running)]
                    print_completed = [f'{index}{self.job_names[index] if self.job_names else ""}' for index in list(self._completed)]
                    uf.info(f'jobs running: {print_run if len(print_run) <= 15 else len(print_run)}', True)
                    uf.info(f'jobs completed: {print_completed if len(print_completed) <= 15 else len(print_completed)}', True)
                    time_last_flush = time.time()
                _running = set()
                bar.update(len(self._completed))
                print("")
                time.sleep(self.flushtime)
                if self.timeout and time.perf_counter() - _timer > self.timeout:
                    break

            # Try to get results
            for i, job in enumerate(_jobs):
                # uf.info("im here 1")
                try:
                    # uf.info("i here 2")
                    self.res.append(job.get(timeout=1))
                except:
                    uf.info(f'Job {i} waited too long, time out', True)
                    self.res.append("Fail")
                    self._failed.add(i)
            if all([job.ready() and job.successful() for job in _jobs]):
                uf.info('All jobs are done running', True)
            elif all([job.ready() for job in _jobs]):
                uf.info('All jobs have been run but some failed', True)
        self.jobs = _jobs

########### test code
# mylist = [chr(x) for x in range(ord('a'), ord('k'))]
#
#
# def dummy(x):
#     try:
#         uf.info('processing ' + str(x))
#     finally:
#         time.sleep(10)
#
#
# aaa = mp(dummy, mylist)
# aaa.run()
#
# bbb = mp(max, mylist, 'b', 'c')
# bbb.run()
# bbb.res
