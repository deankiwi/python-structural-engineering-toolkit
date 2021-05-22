import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import Wedge
import numpy as np
import math


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
        self.width = 400
        self.height = 200
        self.slapdepth = 250
        self.concretegrade = 32
        self.topcover = 30
        self.bottomcover = 30
        self.topreinforcement = [[16,200,0],[16,200,1],[20,200,1]] #[[diameter, spacing, layer]] = layer starts at 0
        self.openings = [[0, 300, 200, 200], [-400,-200, 150, 500]] #[[x, y, width, height]] 

    
    def show(self):
        
        fig, ax = plt.subplots()
        axes = plt.gca()
        plt.axis('equal')
        xmax = self.width + self.slapdepth
        ymax = self.height + self.slapdepth
        axes.set_xlim([-xmax,xmax])
        axes.set_ylim([-ymax,ymax])
            
        self.drawuout(ax)
        ax.add_patch(Rectangle((-self.width/2, -self.height/2), self.width, self.height, color="yellow"))
        plt.xlabel("X-AXIS")
        plt.ylabel("Y-AXIS")
        plt.title("PLOT-1")
        plt.show()

    def drawopenings(self, ax):
        for x, y, width, height in self.openings:
            ax.add_patch(Rectangle((x, y), width, height, color="b"))
            ax.plot([x, x + width],[y, y + height])
            ax.plot([x + width, x],[y, y + height])

    
    def drawuout(self, ax):
        d = self.effectivedepthcalulator()*2

        fov1 = Wedge((self.width/2,self.height/2), d, 0, 90, linewidth = 0, color="r", alpha=0.5)
        fov2 = Wedge((-self.width/2,-self.height/2), d, 180, 270, linewidth = 0, color="r", alpha=0.5)
        fov3 = Wedge((-self.width/2,self.height/2), d, 90, 180, linewidth = 0, color="r", alpha=0.5)
        fov4 = Wedge((self.width/2,-self.height/2), d, -90, 0, linewidth = 0, color="r", alpha=0.5)

        ax.add_artist(fov1)
        ax.add_artist(fov2)
        ax.add_artist(fov3)
        ax.add_artist(fov4)

            
        uoutrect = [
            [-self.width/2-d, -self.height/2, d, self.height],
            [-self.width/2, self.height/2, self.width, d],
            [self.width/2, -self.height/2, d, self.height],
            [-self.width/2, -self.height/2-d, self.width, d]
        ]

        for x, y, width, height in uoutrect:
            ax.add_patch(Rectangle((x, y), width, height, linewidth = 0, color="r", alpha=0.5))

        for openx, openy, openwidth, openheight in self.openings:
            for uoutx, uouty, uoutwidth, uoutheight in uoutrect:

                if (
                    uoutx + max(0, uoutwidth) < openx + min(0, openwidth) or 
                    uoutx + min(0, uoutwidth) > openx + max(0, openwidth) or 
                    uouty + max(0, uoutheight) < openy + min(0, openheight) or 
                    uouty + min(0, uoutheight) > openy + max(0, openheight)
                ):
                    #print('not in square')
                    continue

                #now check if the opening is left or right of column
                
                if not (abs(openx + openx+ openwidth) < self.width or
                    abs(openx) < self.width/2 or
                    abs(openx+ openwidth) < self.width/2
                ):
                    #not - abs(self.width/2) < min(openheight, uoutx + uoutwidth):
                    #TODO review formular belows to check if negative width and high make it invalid
                    y = max(min(uouty, uouty + uoutheight), min(openy, openy + openheight))
                    height =  min(max(uouty -y, uouty + uoutheight - y), max(openy - y, openy + openheight - y))
                    ax.add_patch(Rectangle((uoutx, y), uoutwidth, height, linewidth = 1, color="g"))
                
                #now check if the opening is above or below
                if not (abs(openy + openy+ openheight) < self.height or
                    abs(openy) < self.height/2 or
                    abs(openy+ openheight) < self.height/2
                ):

                    x = max(min(uoutx, uoutx + uoutwidth), min(openx, openx + openwidth))
                    width =  min(max(uoutx -x, uoutx + uoutwidth - x), max(openx - x, openx + openwidth - x))
                    ax.add_patch(Rectangle((x, uouty), width, uoutheight, linewidth = 1, color="g"))
        
        wedgeszone = [
            [[self.width/2, self.height/2 + d], [self.width/2 + d, self.height/2]],
            [[self.width/2 + d, -self.height/2], [self.width/2, -self.height/2 - d]],
            [[-self.width/2, -self.height/2 - d], [-self.width/2 - d, -self.height/2]],
            [[-self.width/2 - d, self.height/2], [-self.width/2, self.height/2 + d]]
        ]

        for wedge in wedgeszone:
            

            def findangle(x, y):
                angle = math.atan2(x,y)
                if angle < 0:
                    angle = angle + 2*math.pi
                return angle
            
            angle1 = findangle(wedge[0][0], wedge[0][1])
            angle2 = findangle(wedge[1][0], wedge[1][1])

            for openx, openy, openwidth, openheight in self.openings:
                openedges = [
                    [openx, openy],
                    [openx, openy + openheight],
                    [openx + openwidth, openy + openheight],
                    [openx + openwidth, openy]
                ]
                hits = []
               
                for edgex, edgey in openedges:
                    openangle = findangle(edgex, edgey)
                    if angle1 < openangle < angle2:
                        
                        print(angle1, openangle, angle2, sep=':\t')
                    
                    
            for spot in wedge:
                ax.plot([0, spot[0]], [0, spot[1]])
        





        self.drawopenings(ax)

    def uout(self):
        '''
        returns uout in mm
        '''
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
print(col1.show())

print('done')