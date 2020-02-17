import matplotlib.pyplot as plt


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

'''
for b in range(300,1200,150):
    beamPlotDesign(200,1600,b,300000000,35)

plt.show()
'''
resolution = 20
for p1 in [0.0016+((0.02-0.0016)/resolution)*i for i in range(resolution+1)]:
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
            ved = Ved2/(0.9*bw*depth)
            vrc = ConcreteShearCapacity(35,depth,bw,p1*depth*bw)
            #print(ved,vrc)
            if vrc > ved:
                #print('Pilecapacity: ',pileCapacity,'  Depth: ',depth)
                depthlist.append(depth)
                pileCapacityList.append(pileCapacity*10**-3)
                break
    #print(p1)
    #print(pileCapacityList,depthlist)
    plt.plot(pileCapacityList,depthlist)
plt.show()



