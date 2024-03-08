# -*- coding: utf-8 -*-
'''
@Author  :   adamzhou
@Contact :   zhouzz400@gmail.com
@Time    :   2020.02.02-23:40:00
@Desc    :   fit urban density function using google earth engine for any city in 1985-2018
'''

import ee
import os
# import geehydro
# import folium
import numpy as np
import pandas as pd
import datetime

from scipy.special import expit
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import AutoMinorLocator, MultipleLocator, FuncFormatter

def reverseSFit(x,y):
    def reverseS(x1, a, c, d):
        y1 = (1-c)/(1+expit( a*(2*x1/d-1) ))+c # overflow-error-in-pythons-numpy-exp-function
        return y1
    popt, pcov = curve_fit(reverseS, x, y, maxfev=5000)
    
    # popt
    a = popt[0] 
    c = popt[1]
    d = popt[2]
    yvals = reverseS(x,a,c,d) #拟合y值
    
    #print(pcov)
    
    return a,c,d,yvals

def gmpFit(x,y):
    def gmp(x1, alpha, n):
        y1 = 1-(1-x1**(-alpha))**n
        return y1
    popt, pcov = curve_fit(gmp, x, y, maxfev=5000)
    
    #popt
    alpha = popt[0]
    n = popt[1]
    yvals = gmp(x,alpha,n) #拟合y值
    
    #print(pcov)
    
    return alpha,n,yvals

def figParaRevers(dic,centerName):
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(3.5,2.625),dpi=200)

    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.tick_params("x",which = "major",direction = "in" ,
                                        length=3,width = 0.5,labelrotation=0,labelsize=6)
    ax.tick_params("x",which = "minor",direction = "in",
                            length=1.5,width = 0.5 ,labelsize=6)

    ax.set_xlim(0,31)
    ax.set_ylim(0,1)
    #ax.set_xticklabels(a,size=6)
    ax.yaxis.set_minor_locator(AutoMinorLocator(4))
    ax.tick_params("y",which = "major",direction = "in",
                            length=3,width = 0.5 ,labelsize=6)
    ax.tick_params("y",which = "minor",direction = "in",
                            length=1.5,width = 0.5 ,labelsize=6)
    labels = ax.get_xticklabels() + ax.get_yticklabels()
    label = [label.set_fontname('Times New Roman') for label in labels]

    font1 = {'family' : 'Times New Roman',
        'weight' : 'normal',
        'size'   : 6}

    ax.set_xlabel("Distance to the city center(km)",font1,size=7)
    ax.set_ylabel("Urban land density",font1,size=7)
    ax.set_title(centerName,font1,size=8)

    color = ["r","lawngreen","b","coral","g","lightskyblue","m","deeppink"]
    i=0
    acd = {}
    for year,data in dic.items():
        y1 = data.loc[:,"dens"]
        x1 = y1.index+1
        ax.plot(x1,y1,".",c=color[i],ms = 2)
        a,c,d,yvals = reverseSFit(x1,y1)
        ax.plot(x1,yvals,"--",lw=1,c=color[i],label = str(year))
        ax.legend(prop=font1,frameon=False,loc="lower left")
        i+=1

        acd[year]=np.round([a,c,d],4)

    return fig,acd

def figParaGMP(dic,centerName):
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(3.5,2.625),dpi=200)

    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.tick_params("x",which = "major",direction = "in" ,
                                        length=3,width = 0.5,labelrotation=0,labelsize=6)
    ax.tick_params("x",which = "minor",direction = "in",
                            length=1.5,width = 0.5 ,labelsize=6)

    ax.set_xlim(0,31)
    ax.set_ylim(0,1)
    #ax.set_xticklabels(a,size=6)
    ax.yaxis.set_minor_locator(AutoMinorLocator(4))
    ax.tick_params("y",which = "major",direction = "in",
                            length=3,width = 0.5 ,labelsize=6)
    ax.tick_params("y",which = "minor",direction = "in",
                            length=1.5,width = 0.5 ,labelsize=6)
    labels = ax.get_xticklabels() + ax.get_yticklabels()
    label = [label.set_fontname('Times New Roman') for label in labels]

    font1 = {'family' : 'Times New Roman',
        'weight' : 'normal',
        'size'   : 6}

    ax.set_xlabel("Distance to the city center(km)",font1,size=7)
    ax.set_ylabel("Urban land density",font1,size=7)
    ax.set_title(centerName,font1,size=8)

    color = ["r","lawngreen","b","coral","g","lightskyblue","m","deeppink"]
    i=0
    an = {}
    for year,data in dic.items():
        y = data.loc[:,"dens"]
        x = y.index+1
        ax.plot(x,y,".",c=color[i],ms = 2)
        a,n,yvals = gmpFit(x,y)
        ax.plot(x,yvals,"--",lw=1,c=color[i],label = str(year))
        ax.legend(prop=font1,frameon=False,loc="lower left")
        i+=1
        
        an[year]=np.round([a,n],4)

    return fig, an


def getBandName(center):
    coor = center.getInfo()["coordinates"]
    print("coordinate: ",coor)
    BandLat = np.ceil(coor[1])
    left = "users/zhouzz400/GAIA_2018_lat/GAIA_1985_2018_"
    if BandLat>0:
        Bandname = left+"%02d"% BandLat
        ceilBandname = left+"%02d"% (BandLat+1)
        floorBandname = left+"%02d"% (BandLat-1)
    elif BandLat<-1:
        Bandname = left+"%03d"% BandLat
        ceilBandname = left+"%03d"% (BandLat+1)
        floorBandname = left+"%03d"% (BandLat-1)
    elif BandLat==0:
        Bandname = left+"%02d"% BandLat
        ceilBandname = left+"%02d"% (BandLat+1)
        floorBandname = left+"%03d"% (BandLat-1)
    elif BandLat==-1:
        Bandname = left+"%03d"% BandLat
        ceilBandname = left+"%02d"% (BandLat+1)
        floorBandname = left+"%03d"% (BandLat-1)
    print( Bandname,ceilBandname,floorBandname)
    return Bandname,ceilBandname,floorBandname

def getDensity(center,years=[34,24,14,4],maxdis=30,kdens = 0.1,year_dic=[]):
    Bandname,ceilBandname,floorBandname = getBandName(center)
    
    GAIA = ee.ImageCollection([Bandname,ceilBandname,floorBandname]).mosaic()
    #Viz_GAIA = {"min": 1, "max": 34, "palette": ['FFFFFF', 'FF0000']}
    # Map.addLayer(GAIA,Viz_GAIA)
    
    df= pd.DataFrame(columns = ["year","dis","ring_area","water_area","urban_area","dens"])
    for year in years:
        print("year begin: "+str(year_dic[year]))
        
        GAIA_year = GAIA.gte(year)
        #Viz_year = {"min": 0, "max": 1, "palette": ['FFFFFF', 'FF0000']}
        #Map.addLayer(sh_year,Viz_year,"sh_year")

        water = ee.Image("JRC/GSW1_1/YearlyHistory/"+str(year_dic[year])).gte(2)
        # Viz_water = {"min": 0, "max": 1, "palette": ["ffffff","0000ff"]}
        # Map.addLayer(water,Viz_water,"water")

        # center = ee.Geometry.Point([121.46851393726786, 31.224416065753665])
        buffer = []
        ring = []
        for i in range(maxdis):
            dis = 1000*(i+1)
            buffer.append( center.buffer(dis) )
            if i == 0:
                ring.append(buffer[i])

            else:
                ring.append( buffer[i].symmetricDifference(buffer[i-1]) )

            #Map.addLayer(ring[i])
            ring_urban = GAIA_year.eq(1).clip(ring[i])
            urban_image = ring_urban.multiply(ee.Image.pixelArea())
            urban_area = ee.Number( urban_image.reduceRegion(**{"reducer": ee.Reducer.sum(),"scale": 30,"maxPixels": 1e9}).get("b1") )

            ring_water = water.eq(1).clip(ring[i])
            water_image = ring_water.multiply(ee.Image.pixelArea())
            water_area = ee.Number( water_image.reduceRegion(**{"reducer": ee.Reducer.sum(),"scale": 30,"maxPixels": 1e9}).get("waterClass") )

            ring_area = ring[i].area()
            #print(ring_area.getInfo(),water_area.getInfo(),urban_area.getInfo())
           
            Denominator = ring_area.subtract( water_area )
            dens = urban_area.divide(Denominator).getInfo()
            #print(i,dens)
            
            dic = {"year":str(year_dic[year]),"dis":dis,"ring_area":ring_area.getInfo(),"water_area":water_area.getInfo(),
                   "urban_area":urban_area.getInfo(),"dens":dens}
            df = df.append(dic,ignore_index=True)
            
            if dens<=kdens:
                print("less than "+str(kdens)+" in:"+str(i))
                break
    return  df

def main(fid,name,yDic,path,file_x,status = 1):
    year_dic = {34:1985,33:1986,32:1987,31:1988,
            30:1989,29:1990,28:1991,27:1992,26:1993,25:1994,24:1995,23:1996,22:1997,21:1998,
            20:1999,19:2000,18:2001,17:2002,16:2003,15:2004,14:2005,13:2006,12:2007,11:2008,
            10:2009, 9:2010, 8:2011, 7:2012, 6:2013, 5:2014, 4:2015, 3:2016, 2:2017, 1:2018,} 
    # greater than or equal  1 = urban 2018
    
    center = ee.FeatureCollection("users/zhouzz400/Boundries/city_center").filter(ee.Filter.eq("wof_id",fid)).geometry()
    ## center = ee.Geometry.Point([121.46851393726786, 31.224416065753665])
    df = getDensity(center, years=yDic, maxdis=30, kdens=0.1,year_dic=year_dic)

    fname = path + "dens_"+name+ file_x+".csv"
    df.to_csv(fname)

    dic = {}
    for year, group_data in df.groupby("year"):
        if len(group_data)>=5:
            dic[year] = group_data.reset_index(drop=True)
            
    if status >0:
        fig_rvs, acd = figParaRevers(dic,name)
        figSname = path + "FigS_"+name+ file_x +".png"
        fig_rvs.savefig(figSname,bbox_inches="tight",dpi=1200,pad_inches=0)
        
        df_acd = pd.DataFrame(acd)
        acdname = path+"ACD_"+name+ file_x +".csv"
        df_acd.to_csv(acdname)

    if status >1:
        fig_gmp, an = figParaGMP(dic,name)
        figGname = path + "FigG_"+name+ file_x +".png"
        fig_gmp.savefig(figGname,bbox_inches="tight",dpi=1200,pad_inches=0)
        
        df_an = pd.DataFrame(an)
        anname = path+"AN_"+name+ file_x +".csv"
        df_an.to_csv(anname)



if __name__=="__main__":

    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'
    ee.Initialize()


    yDic = [34,29,24,14,1]
    path = "./output/105/"
    file_x = "_reversS"
    Countrys = ["China","United Kingdom"]
    
    df = pd.read_excel("centers.xls")
    df1 = df.loc[df["SOV0NAME"].isin(Countrys)][["NAMEASCII","wof_id"]]
    name_dic = {}
    for i in range(len(df1)):
        city = df1.iloc[i,]["NAMEASCII"]
        fid = int(df1.iloc[i,]["wof_id"])## int not numpy int64
        name_dic[city] = fid

    status = 1 
    
    for name,fid in name_dic.items():
        time = datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S') 
        print(name+" begin: "+ time)
        main(fid,name, yDic, path, file_x,status)
        
