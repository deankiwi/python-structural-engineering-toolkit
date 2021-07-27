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

def findangle(x, y):
    angle = math.atan2(x,y)
    if angle < 0:
        angle = angle + 2*math.pi
    return angle



class punchingshear():

    def __init__(self):
        self.width = 400
        self.height = 200
        self.slapdepth = 250
        self.concretegrade = 32
        self.topcover = 30
        self.bottomcover = 30
        self.topreinforcement = [[16,200,0],[16,200,1],[20,200,1]] #[[diameter, spacing, layer]] = layer starts at 0
        self.openings = [
            [0, -500, 300, 200],
            [-400,-200, 150, 500],
            [-230,300,1000,200]] #[[x, y, width, height]] 
        self.wedges = [
            [self.width/2, self.height/2, 0, 90],
            [-self.width/2, self.height/2, 90, 180],
            [-self.width/2, -self.height/2, 180, 270],
            [self.width/2, -self.height/2, -90, 0]] #[x,y,angle0, angle1]
        self.d1 = self.effectivedepthcalulator()*2
        self.uoutrect = [
            [-self.width/2-self.d1, -self.height/2, self.d1, self.height],
            [-self.width/2, self.height/2, self.width, self.d1],
            [self.width/2, -self.height/2, self.d1, self.height],
            [-self.width/2, -self.height/2-self.d1, self.width, self.d1]
        ]

    
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
    
    def drawwedge(self, ax):
        d = self.effectivedepthcalulator()*2
        #TODO add function that cuts wedges relative to openings

        for x, y, angle0, angle1 in self.wedges:
            objwedge = Wedge((x,y), d, angle0, angle1, linewidth = 0, color="r", alpha=0.5)
            ax.add_artist(objwedge)
    
    def drawuoutrect(self, ax):
        #call function that reduces reletive to location of opens
        for x, y, width, height in self.uoutrect:
            ax.add_patch(Rectangle((x, y), width, height, linewidth = 0, color="r", alpha=0.5))



    
    def drawuout(self, ax):
        d = self.effectivedepthcalulator()*2

        self.drawwedge(ax)
        self.drawuoutrect(ax)
        self.wedgesopenings()

        #TODO but for loop below into it's own function
        for openx, openy, openwidth, openheight in self.openings:
            for uoutx, uouty, uoutwidth, uoutheight in self.uoutrect:

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
                        #TODO if also opening is within wedge add to hit
                        pass
                        #print(angle1, openangle, angle2, sep=':\t')
            #TODO use hits list to find max a min

                    
            for spot in wedge:
                ax.plot([0, spot[0]], [0, spot[1]])
        





        self.drawopenings(ax)
    
    def isinwedgh(self, wedgex0, wedgey0, wedgex1, wedgey1, wedgex2, wedgey2, x, y):
        
        if min( wedgex0, wedgex1, wedgex2) < x < max(wedgex0, wedgex1, wedgex2) and min( wedgey0, wedgey1, wedgey2) < y < max(wedgey0, wedgey1, wedgey2):
            return True
    #TODO function that returns True and angle that the zone infringest on

    def wedgesopenings(self):
        
        def angleWedgetoMaths(angle):
            #convert matplotlib wedge angle (0 start East anticlockwises)
            #to Math angle (0 starts North clock wise)
            return (90-angle)%360
        
        #cutes the wedges relative to the openings
        newwedge = [] #New list the will replace self.wedge
        orginalwedge = []
        for wedgex, wedgey, angle0, angle1 in self.wedges:
            angle0_, angle1_ = angleWedgetoMaths(angle0), angleWedgetoMaths(angle1)
            startangle = min(angle0_, angle1_)
            endangle = max(angle0_, angle1_)
            if endangle-startangle > 90:
                #TODO add in function the stops 0 =360 from causing erros
                startangle, endangle = endangle, startangle + 360
            orginalwedge.append([startangle, endangle])
            openangle = [] #create list of all opening max and min angle relative to wedge
            for openx, openy, openwidth, openheight in self.openings:
                '''
                find out the angle of all the points on the opening
                check to see if the points are within or overlap the wedge
                the opening can't be > 180° 
                there for max(angle) - min(angle) we must normalise angle but suptracting 360 of max(angle) 
                wedge angle is 90 degree of from find angle degree
                wedge is horizontal
                findangle in vertical
                '''
                openxnorm = openx - wedgex
                openynorm = openy - wedgey
                angles = [
                    findangle(openxnorm, openynorm),
                    findangle(openxnorm + openwidth, openynorm),
                    findangle(openxnorm, openynorm + openheight),
                    findangle(openxnorm + openwidth, openynorm + openheight)
                ]
                angles = [math.degrees(ang) for ang in angles]

                    
                
                if [x for x in angles if startangle < x < endangle]:
                    #print(angles, startangle, endangle)
                    if max(angles) - min(angles) > 180:
                        #if the opening runs over 0 degree axiels we add 360 to lower angles
                        angles = [x + 360*(1-x//180) for x in angles if x < 360]
                    if sum((startangle, endangle)) <= 90:
                            startangle, endangle = startangle + 360, endangle + 360
                    print(angles, startangle, endangle)
                    if max(angles) > endangle:
                        startangle = max(startangle,min(angles))
                        print(startangle, endangle)
                        newwedge.append([startangle%360,endangle%360])
                        

                        
                    else:
                        startangle = min(startangle,max(angles))
                        endangle = max(angles)
                        print(startangle, endangle)
                        newwedge.append([startangle%360,endangle%360])
            # newwedge.append([startangle%360,endangle%360])
        print(newwedge, orginalwedge)
        for openzone in newwedge:
            for wedges in orginalwedge:
                if min(wedges):
                    pass
        #TODO split the wedges relative to the max and min angles but also check if it is already within angle
        #TODO ^ this to be done using the newwedge compaired to the orginalwedge list
        
        
            


                    




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