# -*- coding: utf-8 -*-
# @Author: YangZhou
# @Date:   2017-06-19 13:19:47
# @Last Modified by:   YangZhou
# @Last Modified time: 2017-06-19 13:22:24
from aces.config import libs
import aces.tools as tl
import time
import numpy as np
import pexpect


class pbs:

    def __init__(self, queue, nodes, procs, disp, path, content):
        self.queue, self.nodes, self.procs,\
            self.disp, self.path, self.content =\
            queue, nodes, procs, disp, path, content

    def writepbs(self, filename='aces.pbs'):
        self.filename = filename
        tl.write(self.getPbs(), filename)

    def submit(self):
        cmd = "cd %s;qsub %s 2>&1" % (self.path, self.filename)
        tl.debug(cmd)
        print(cmd)
        x = self.ssh_cmd('xggong', 'cluster', cmd)
        # assert not x.strip()==''
        tl.debug(x)

    def getPbs(self):
        queue, nodes, procs, disp, content =\
            self.queue, self.nodes, self.procs, self.disp, self.content
        ss = ':'.join(libs)
        s = """#!/bin/bash -x
        #PBS -l nodes=%s:ppn=%s
        #PBS -l walltime=240:00:00
        #PBS -j oe
        #PBS -q %s
        #PBS -N %s
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:%s
        cd $PBS_O_WORKDIR
        %s
        """ % (nodes, procs, queue, disp, ss, content)
        s = tl.headtrim(s)
        return s

    def ssh_cmd(self, user, ip, cmd):
        passwd = 'AdminYu@224'
        ssh = pexpect.spawn('ssh %s@%s "%s"' % (user, ip, cmd))
        try:
            i = ssh.expect(
                ['password:', 'continue connecting (yes/no)?'], timeout=5)
            if i == 0:
                ssh.sendline(passwd)
            elif i == 1:
                ssh.sendline('yes')
                ssh.expect('password: ')
                ssh.sendline(passwd)
        except pexpect.EOF:
            tl.debug("EOF")
        except pexpect.TIMEOUT:
            tl.debug("TIMEOUT")
        else:
            r = ssh.read()
            tl.debug(r)
            ssh.close()


class th:

    def __init__(self, path, disp):
        self.path = path
        self.disp = disp
        self.content = ""

    def writepbs(self, filename='aces.pbs'):
        self.filename = filename
        tl.write(self.getPbs(), filename)

    def submit(self):
        pass

    def getPbs(self):
        s = """#!/bin/bash -x
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/lib
        yhrun -n 24 -p work /HOME/fudan_xggong_1/soft/vasp.5.2.11/vasp >log.out
        %s
        """ % (self.content)
        s = tl.headtrim(s)
        return s


class jobManager:

    def __init__(self):
        self.jobs = []
        self.njob = 0

    def run(self):
        old = tl.pwd()
        for job in self.jobs:
            tl.cd(job.path)
            job.writepbs()
            job.submit()
        tl.cd(old)

    def check(self):
        jobdone = np.array(
            [tl.exists(job.path + "/done") for job in self.jobs])
        tl.debug('entering loop waiting for vasp...')
        while not jobdone.all():
            time.sleep(3)
            jobdone = np.array(
                [tl.exists(job.path + "/done") for job in self.jobs])
            # debug(paths[jobdone])
        tl.debug('done')

    def reg(self, pb):
        pb.disp = "jb%s." % self.njob + pb.disp
        pb.content += "\n  date>done"
        self.jobs.append(pb)
        self.njob += 1
