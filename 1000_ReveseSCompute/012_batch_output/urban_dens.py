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
from collections import OrderedDict



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
        ##water = ee.Image("JRC/GSW1_1/YearlyHistory/2018").gte(2)
        # Viz_water = {"min": 0, "max": 1, "palette": ["ffffff","0000ff"]}
        # Map.addLayer(water,Viz_water,"water")

        # center = ee.Geometry.Point([121.46851393726786, 31.224416065753665])

        buffer = ee.List([])
        ring = ee.List([])
        for i in range(maxdis):
            dis = 1000*(i+1)
            buffer = buffer.add( center.buffer(dis) )
            if i == 0:
                ring=ring.add( buffer.get(i))

            else:
                ring=ring.add( ee.Geometry(buffer.get(i)).symmetricDifference(buffer.get(i-1)) )

            #Map.addLayer(ring[i])
            ring_urban = GAIA_year.eq(1).clip(ring.get(i))
            urban_image = ring_urban.multiply(ee.Image.pixelArea())
            urban_area = ee.Number( urban_image.reduceRegion(**{"reducer": ee.Reducer.sum(),"scale": 30,"maxPixels": 1e9}).get("b1") )

            ring_water = water.eq(1).clip(ring.get(i))
            water_image = ring_water.multiply(ee.Image.pixelArea())
            water_area = ee.Number( water_image.reduceRegion(**{"reducer": ee.Reducer.sum(),"scale": 30,"maxPixels": 1e9}).get("waterClass") )

            ring_area = ee.Geometry(ring.get(i)).area()
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


if __name__=="__main__":

    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'
    ee.Initialize()

    yDic = [34,29,24,14,1]
    path = "./output/107/"
    file_x = "_reS"
    Country = ["United Kingdom"]
    index = 4 ## begin index
    status = 0
    df = pd.read_excel("centers.xls")
    df1 = df.loc[df["SOV0NAME"].isin(Country)][["NAMEASCII","wof_id"]]

    name_dic = OrderedDict({})
    for i in range(len(df1)):
        city = df1.iloc[i,]["NAMEASCII"]
        fid = int(df1.iloc[i,]["wof_id"])## int not numpy int64
        name_dic[city] = fid
    name_dic = OrderedDict(sorted(name_dic.items(), key=lambda t: t[0]))
    
    for i in range(len(name_dic)):
        if i<index:
            pass
        else:
            name = list(name_dic)[i]
            fid = name_dic[name]
            time = datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S') 
            print(name+" begin: "+ time)
            main(fid,name, yDic, path, file_x,status)
        
