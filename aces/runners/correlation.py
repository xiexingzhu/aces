# -*- coding: utf-8 -*-
# @Author: YangZhou
# @Date:   2015-12-10 12:50:49
# @Last Modified by:   YangZhou
# @Last Modified time: 2017-06-19 12:27:03

import aces.tools as tl
import aces.config as config

from aces.runners.vdos import vdos
from aces.runners import Runner
from aces.lammpsdata import lammpsdata

# from aces.f import premitiveSuperMapper


class runner(Runner):

    def get_structure(self):
        m = self.m
        atoms = m.atoms_from_dump('minimize/range')
        satoms = atoms.repeat(m.correlation_supercell)

        a = lammpsdata(satoms, m.elements)
        a.writedata('correlation_structure', self.m.creatbonds)
        # psm=premitiveSuperMapper(atoms,satoms)
        # s2p,v,=psm.getS2p()
        s = "%s %d\n#l1 l2 l3 k tag\n" % (tl.toString(m.correlation_supercell),
                                          len(atoms))
        c = m.correlation_supercell
        n = 0
        for i in range(c[0]):
            for j in range(c[1]):
                for k in range(c[2]):
                    for p in range(len(atoms)):
                        u = [i, j, k, p, n + 1]
                        s += tl.toString(u) + "\n"
                        n += 1
        tl.write(s, 'phana.map.in')

    def generate(self):
        m = self.m
        self.get_structure()
        f = open("correlation.lmp", "w")
        print >> f, "units %s" % m.units
        print >> f, "dimension 3"
        pbcx = pbcy = pbcz = 'p'
        if m.corrNVT:
            pbcx = 's'

        print >> f, "boundary %s %s %s" % (pbcx, pbcy, pbcz)
        print >> f, m.getatomicstyle()
        print >> f, "read_data   correlation_structure"
        print >> f, "lattice fcc 5"  # needed to define the regions
        print >> f, "thermo %d" % m.dumpRate
        print >> f, "thermo_modify     lost warn"
        print >> f, m.masses
        print >> f, m.potential
        print >> f, "timestep %f" % m.timestep
        print >> f, "reset_timestep 0"

        if m.corrNVT:
            box = m.box
            deta = m.deta
            wfix = m.wfix
            xlo, xhi, ylo, yhi, zlo, zhi, lx, ly, lz = box
            fixl1 = xlo - deta
            fixl2 = fixl1 + deta * wfix
            fixr2 = xhi + deta
            fixr1 = fixr2 - deta * wfix
            print >>f, "region	stayl	block   %s  %s" % (fixl1, fixl2) + \
                " INF  INF INF  INF units box"
            print >>f, "region	stayr	block   %s  %s" % (fixr1, fixr2) + \
                " INF INF   INF  INF units box"
            print >> f, "region   stay    union  2 stayl stayr"
            print >>f, "region	main	block   %s  %s" % (fixl2, fixr1) + \
                " INF INF   INF  INF units box"
            print >> f, "group   stay    region  stay"
            print >> f, "group   main    region  main"
            print >> f, "velocity stay set 0 0 0"
        else:
            print >> f, "region	main	block   INF" + \
                "  INF INF  INF INF  INF units box"
            print >> f, "group    main    region  main"
        print >> f, "velocity main create %f %d mom" % (m.T, m.seed) + \
            " yes rot yes dist gaussian"
        if m.dimension == 1:
            print >> f, "velocity  main set NULL 0.0 0.0 units box"
        elif m.dimension == 2:
            print >> f, "velocity  main set NULL NULL 0.0 units box"
        print >> f, "fix getEqu  main  nvt temp %f %f %f" % (m.T, m.T, m.dtime)
        print >> f, "dump dump1 all atom %d dump.lammpstrj" % (
            m.Cinterval * 500)
        print >> f, "dump_modify  dump1 sort id"
        print >> f, "run %d" % m.equTime
        print >> f, "unfix getEqu"
        print >> f, "reset_timestep 0"
        if not m.nvt:
            print >> f, "fix nve main nve"
        else:
            print >> f, "fix getEqu  main  nvt temp %f %f %f" % (m.T, m.T,
                                                                 m.dtime)

        if m.usephana:
            print >> f, "fix phonon1 all phonon" + \
                " %s %s 0 phana.map.in phonon" % (m.Cinterval, m.Ctime)
        if m.runner == "dynaphopy":
            print >> f, "dump lala main custom %s" % m.Cinterval + \
                "  dynaphopy.lammpstrj x y z"
            print >> f, "dump_modify  lala sort id"
        elif not m.phanaonly:
            print >> f, "dump lala main h5md %s" % m.Cinterval +\
                " velocity.h5md velocity" + \
                "  box no create_group yes"
        print >> f, "run %s" % m.Ctime

        f.close()

        tl.passthru(
            config.mpirun +
            "  %s " %
            self.m.nodes *
            self.m.procs +
            config.lammps +
            " <correlation.lmp  >out.dat")
        if m.usephana:
            self.phana()
            self.phanados()
        if m.phanaonly:
            return
        if not m.runner == "dynaphopy" and not m.runner == 'lifetime':
            self.dos()
        # rm("velocity.txt")

    def dos(self):
        self.vd = self.getvdos()
        self.vd.run()

    def getvdos(self):
        return vdos(self.m.timestep)

    def phana(self):
        from aces.tools import read
        m = self.m
        bp = m.bandpath
        bpp = m.bandpoints
        v = ""
        for i in range(len(bp) - 1):
            v += "%s\n%s\n101\n" % (tl.toString(bpp[bp[i]]),
                                    tl.toString(bpp[bp[i + 1]]))
        s = """20
        1
        2
        phana.band.txt
        %sq
        0
        """ % v
        s = s.replace(r'^\s+', '')
        tl.write(s, 'phana.in')

        tl.passthru(config.phana + 'phonon.bin.%d <phana.in' % m.Ctime)
        s = read('pdisp.gnuplot')
        s = s.replace('pdisp.eps', 'phana.band.eps')
        tl.write(s, 'phana.band.gnuplot')
        tl.passthru('rm pdisp.gnuplot')
        tl.passthru('gnuplot phana.band.gnuplot')
        tl.passthru('convert -rotate 90 phana.band.eps phana.band.png')

    def phanados(self):
        from aces.tools import read
        m = self.m
        s = """20
        1
        1
        %s
        2
        y
        
        1000
        y
        phana.dos.txt
        0
        """ % tl.toString(m.kpoints)
        s = s.replace(r'^\s+', '')
        tl.write(s, 'phana.dos.in')

        tl.passthru(config.phana + 'phonon.bin.%d <phana.dos.in' % m.Ctime)
        s = read('pdos.gnuplot')
        s = s.replace('pdos.eps', 'phana.dos.eps')
        tl.write(s, 'phana.dos.gnuplot')
        tl.passthru('rm pdos.gnuplot')
        tl.passthru('gnuplot phana.dos.gnuplot')
        tl.passthru('convert -rotate 90 phana.dos.eps phana.dos.png')

    # *calculate the spectrum correlation length

    def getlc(self):
        vd = self.getvdos()
        vd.cal_lc(20, .5, self.m)
        # vd.fourier_atom(id)
