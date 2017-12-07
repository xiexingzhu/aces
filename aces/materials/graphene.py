# -*- coding: utf-8 -*-
# @Author: YangZhou
# @Date:   2017-06-12 22:01:42
# @Last Modified by:   YangZhou
# @Last Modified time: 2017-06-19 13:16:20
from aces.materials import Material
from .atomic import get_unique_atoms, swap, wrap
from ase import Atoms, Atom
from math import pi, sqrt
from ase.dft.kpoints import ibz_points
from aces import config
from aces.tools import debug


class structure(Material):

    def set_parameters(self):
        self.gnrtype = 'zigzag'
        self.tilt = False
        self.pi3 = False
        self.az = 10.0
        self.pot = False

    def setup(self):
        self.bandpoints = ibz_points['hexagonal']
        self.bandpath = ['Gamma', 'M', 'K', 'Gamma']
        if self.pot == 1:
            debug("graphene potential chosen:SiC_1994.tersoff")
            self.potential = 'pair_style	tersoff\npair_coeff	* * %s/SiC_1994.tersoff  %s' % (
                config.lammpspot, ' '.join(['C' for i in self.elements]))

    def lmp_structure(self):
        if self.tilt:
            prototype = self.prototype_tilt
        else:
            prototype = self.prototype
        bond = self.bond
        if self.gnrtype == 'armchair':
            col = prototype(self.latx, self.laty)
        elif self.gnrtype == 'zigzag':
            col = prototype(self.laty, self.latx)
            """
			col.rotate([1,1,0],pi,rotate_cell=True)
			cell=col.cell[[1,0,2]]
			cell[2]*=-1
			col.set_cell(cell)
			"""
            swap(col, 2)
        else:
            raise Exception('Unkown gnr type!')

        cell = col.cell * bond
        col.set_cell(cell, scale_atoms=True)

        col.translate([0.01, 0.01, 0.01])

        col.set_pbc([self.xp, self.yp, self.zp])
        atoms = get_unique_atoms(col)
        atoms.center()
        if self.pi3:
            if self.pi3:
                self.pi3 = pi / 3
            atoms.rotate('z', self.pi3, rotate_cell=True)
        return atoms

    def prototype_tilt(self, latx, laty):
        unit = Atoms()
        unit.append(Atom('C', [1.0 / 2, 0, 0]))
        unit.append(Atom('C', [0, sqrt(3) / 2, 0]))
        unit.set_cell((3.0 / 2, sqrt(3), 10.0))
        unit.cell[0, 1] = sqrt(3) / 2
        col = unit.repeat((latx, laty, 1))
        return col

    def prototype(self, latx, laty):
        # armchair
        unit = self.ring()
        col = unit.repeat((latx, laty, 1))
        return col

    def ring(self):
        # armchair ring
        atoms = Atoms()
        atom = Atoms('C', positions=[(1.0, 0.0, 0.0)])
        for i in range(6):
            unit = atom.copy()
            unit.rotate('z', pi / 3 * i)
            atoms.extend(unit)
        atoms.set_cell([3.0, sqrt(3), self.az])
        atoms.center()
        wrap(atoms)
        return atoms
