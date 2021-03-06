from aces.materials.POSCAR import structure as material
class structure(material):
  def getPOSCAR(self):
		return """POSCAR file written by OVITO
1.0
        4.0949149132         0.0000000000         0.0000000000
       -2.0474572182         3.5462999282         0.0000000000
        0.0000000000         0.0000000000        26.8897285461
   In   Se
    6    6
Direct
     0.000000000         0.000000000         0.220288754
     0.000000000         0.000000000         0.115002766
     0.666666985         0.333332986         0.553622723
     0.666666985         0.333332986         0.448335797
     0.333332986         0.666666985         0.886955798
     0.333332986         0.666666985         0.781669796
     0.666666985         0.333332986         0.067873783
     0.666666985         0.333332986         0.267467767
     0.333332986         0.666666985         0.401207775
     0.333332986         0.666666985         0.600800753
     0.000000000         0.000000000         0.734540701
     0.000000000         0.000000000         0.934134722
"""
  def csetup(self):
    from ase.dft.kpoints import ibz_points
    self.bandpoints=ibz_points['hexagonal']
    self.bandpath=['Gamma','K','M','Gamma','L']
			
		