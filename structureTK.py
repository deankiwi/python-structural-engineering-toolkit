import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np


def kValue(M,b,d,fck):
    k = M/(b*(d**2)*fck)
    if k < 0.05:
        k = 0.05
    return k

def zValue(d,k):
    if k > 0.168:
        return 1
    return (d/2)*(1 + (1-3.53*k)**0.5)

def tensionReinforcement(M,fyd,z):
    return M/(fyd*z)

def dValue(h,cover = 30,bar=16,links = 0):
    return h - cover-links-bar/2

def tensileConcrete(fck):
    fctmDic = {'25':2.6,'28':2.8,'30':2.9,'35':3.2,'40':3.5}
    #print(fctmDic[str(fck)])
    return fctmDic[str(fck)]

def minimumSteel(fck,b,d,fyk=500):
    fctm = tensileConcrete(fck)
    return (0.26*fctm*b*d)/fyk

def maximumSteel(h,b):
    return 0.04*h*b

def ConcreteShearCapacity(fck,d,b,Asl):
    '''
    from EC2 6.2.a. Asl is percentage of reinforcement
    Vmin needed to be added
    '''
    k = 1 + (200/d)**0.5
    if k > 2: k = 2
    p1 = Asl/(b*d)
    if p1 > 0.02: p1 = 0.02

    Crdc = 0.12

    return (Crdc*k * (100*p1*fck)**(1/3))


def beamDesign(h,b,M,fck):
    d = dValue(h)
    k = kValue(M,b,d,fck)
    z = zValue(d,k)
    Asreq = tensionReinforcement(M,435,z)
    Asmin = minimumSteel(fck,b,d)
    Asmax = maximumSteel(h,b)
    print(Asmax)
    if Asmin > Asmax or Asreq > Asmax:
        return 'Fail in Max'
    if Asmin > Asreq:
        return Asmin
    else:
        return Asreq



def beamPlotDesign(startDepth,endHeight,b,M,fck):
    AsreqList = []
    depthList = []

    for i in range(startDepth,endHeight,20):
        #print('beam depth ',i,' Asreq ',end ='')
        Asreq = beamDesign(i,b,M,35)
        print('Asreq', Asreq)
        if Asreq == 'Fail in Max':
            pass
        else:
            AsreqList.append(Asreq)
            depthList.append(i)


    plt.plot(depthList,AsreqList)
    #plt.show()


def plot_beam_no_links():
    #plots the maximum capacity of a beam that doesn't require shear links

    resolution = 20
    for index, p1 in enumerate( [0.0016+((0.02-0.0016)/resolution)*i for i in range(resolution+1)]):
        depthlist = []
        pileCapacityList = []
        for pileCapacity in range(500,10000,100):
            pileCapacity = pileCapacity*10**3 #kN to N

            #run throught pilecapacity
            pileSize = 750
            length = pileSize*3
            bw = pileSize + 300
            Ned = pileCapacity*2
            Ved = Ned/2
            
            Med = (Ned*length)/400
            for depth in range(200,5000,25):
                beta = (pileSize*1.2)/(depth)
                if beta > 1: beta =1
                elif beta < 0.25: beta = 0.25
                Ved2 = Ved*beta #shear inchancement
                ved = Ved2/(0.9*bw*depth) #nts look into if z should be used if worst case!
                vrc = ConcreteShearCapacity(35,depth,bw,p1*depth*bw)
                #print(ved,vrc)
                if vrc > ved:
                    #print('Pilecapacity: ',pileCapacity,'  Depth: ',depth)
                    depthlist.append(depth)
                    pileCapacityList.append(pileCapacity*10**-3)
                    break
        #print(p1)
        #print(pileCapacityList,depthlist)
        if index == 0 or index == resolution:
            col = '0.1'
            
        else:
            col = '0.90'
        if index == 0 or index == resolution or index%5 ==0:
            plt.text(pileCapacityList[-1]+20,depthlist[-1]+ 20, str(p1*100)+'%('+
                str(int(depth*bw*p1))+'mm²)'
            )

        lines = plt.plot(pileCapacityList,depthlist, color=col)

        lines[0].set_linestyle( 'dashed')
        
    plt.show()



class punchingshear():

    def __init__(self):
        self.width = 200
        self.hight = 100
        self.slapdepth = 250
        self.concretegrade = 32
        self.topcover = 30
        self.bottomcover = 30
        self.topreinforcement = [[16,200,0],[16,200,1],[20,200,1]] #[[diameter, spacing, layer]] = layer starts at 0

    
    def show(self):
        
        fig, ax = plt.subplots()
        ax.plot([1,5,2],[2,3,4],color="cyan")
        ax.add_patch(Rectangle((-self.width/2, -self.hight/2), self.width, self.hight, color="yellow"))
        plt.xlabel("X-AXIS")
        plt.ylabel("Y-AXIS")
        plt.title("PLOT-1")
        plt.show()

    def uout(self):
        pass

    def effectivedepthcalulator(self):
        maxRebarPerLayer = {} # {str(dia), layer}
        for diamater, _ , layer in self.topreinforcement:
            if str(layer) not in maxRebarPerLayer:
                maxRebarPerLayer[str(layer)] = diamater
            
            else:
                if maxRebarPerLayer[str(layer)] < diamater:
                    maxRebarPerLayer[str(layer)] = diamater
        
        deff = self.slapdepth - self.topcover - sum(maxRebarPerLayer.values())

        return deff


col1 = punchingshear()
print(col1.effectivedepthcalulator())

print('done')