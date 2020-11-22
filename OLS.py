#-------------------------------------------------------------------------------
# Name:        Linear regression combinations
# Purpose:      calculate R2 and p-value for each combination of population and
#               built-up area (and their derivatives)
#
# Author:      Ace
#
# Created:     03/04/2015
# Copyright:   (c) Ace 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from scipy import stats
import arcpy, numpy, csv
from numpy import array
import numpy as np

def getFieldList(Shp,field):
    # get all field names in a shapefile
    cur=arcpy.SearchCursor(Shp)
    reList=[]
    for row in cur:
        reList.append(row.getValue(field))
    del row
    del cur
    return reList

def countRsqr(list1,list2):
    # calculate R2 of two data (i.e. population and built-up area) based on linear regression
    arr1=np.log(array(list1))
    arr2=np.log(array(list2))
    slope, intercept, r_value, p_value, std_err = stats.linregress(arr1,arr2)
    p=p_value
    r=r_value**2
    return r

def countPValue(list1,list2):
    # calculate p-value of two data (i.e. population and built-up area) based on linear regression
    arr1=np.log(array(list1))
    arr2=np.log(array(list2))
    slope, intercept, r_value, p_value, std_err = stats.linregress(arr1,arr2)
    return p_value

def createRsqrTable(Shp,poplist,lclist,csvfile):
    # create a csv file to store the R2 and the p-value of all the combinations
    myfile = open(csvfile, 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    mylist=["popAtt"]
    mylist=mylist+lclist
    wr.writerow(mylist)
    for pop in poplist:
        mylist=[pop]
        list1=getFieldList(Shp,pop)
        for lc in lclist:
            list2=getFieldList(Shp,lc)
            r=countRsqr(list1,list2)
            p=countPValue(list1,list2)
            if p<0.05:
                text=str(r)[:6]+"*"

            else:
                text=str(r)[:6]
            mylist.append(text)
        wr.writerow(mylist)

#-------------------------------------------------------------------------------
Poplist=["Pop2000","Pop2010","PopChng","PctChnge","PopDens00","PopDens10","PopDnsChg","dvlpDens00",\
         "dvlpDens10","dvlpDnsChg"]

LClist=["Bu2000","Bu2000Pct","Bu2010","Bu2010Pct","newBu","PNewBu","NBuOBu00","NBuONnBu00"\
##        "PNBu250mInD","PNBu500mInD","PNBu1000mInD","PNBu2000mInD","PNBu5000mInD","PNBu5000mOutD",\
##        "PNBu250mInC","PNBu500mInC","PNBu1000mInC","PNBu2000mInC","PNBu5000mInC","PNBu5000mOutC",\
        ]
shpfile=r"D:\regional_anlys\anlys2.mdb\studyarea\studyarea_LCData_PosPopOnly"
csvloc=r"D:\regional_anlys\Rsqr_logPopLC.csv"

createRsqrTable(shpfile,Poplist,LClist,csvloc)