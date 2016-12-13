from aces.materials.POSCAR import structure as material
class structure(material):
    def getPOSCAR(self):
    	#return self.getMinimized()
      return """Co2 S2
1.0
        3.7323811054         0.0000000000         0.0000000000
        0.0000000000         3.7323811054         0.0000000000
        0.0000000000         0.0000000000        13.1103467941
   Co    S
    2    2
Direct
     0.500000000         0.000000000         0.521173060
     0.000000000         0.500000000         0.521173060
     0.500000000         0.500000000         0.611771047
     0.000000000         0.000000000         0.430575103
"""
"""
    def csetup(self):
        import numpy as np
        b=np.array([-0.25038,-0.968148,0.01,
            0.968148,-0.25038,0.01,
            0.01,0.01,1.0]).reshape([3,3])
        a=np.array([
            [0,1.0,0],
            [-1.0,-1.0,0],
            [0,0,1.0]
            ])
        self.premitive=b.T.dot(a.T)
"""