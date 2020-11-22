#-------------------------------------------------------------------------------
# Name:        Extract agriculture and natural vegetation to Ghana district shp
# Purpose:     This is the python script based on ArcGIS arcpy library for extracting
#               the areas of agriculture and natural vegetation land cover from
#               2000 and 2010 land cover maps.
#
# Author:      Ace
#
# Created:     12/07/2015
# Copyright:   (c) Ace 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, os, sys
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True

arcpy.env.workspace=r"D:\regional_anlys\anlys2.mdb\studyarea"

NV2000=r"D:\regional_anlys\anlys2.mdb\NV2000"   # path for 2000 natural vegetation raster file
NV2010=r"D:\regional_anlys\anlys2.mdb\NV2010"   # path for 2010 natural vegetation raster file
Ag2000=r"D:\regional_anlys\anlys2.mdb\Ag2000"   # path for 2000 agriculture raster file
Ag2010=r"D:\regional_anlys\anlys2.mdb\Ag2010"   # path for 2010 agriculture raster file

district=r"D:\regional_anlys\anlys2.mdb\studyarea\studyarea_LCData" #The input shapefile (features layer) name

def countLCPx(Img,district):
    # count agriculture and natural vegetation pixels in each district
    baseName=os.path.basename(Img)
    outZonalName=baseName+"_dst"
    outZonal=ZonalStatistics(district, "DISTRICT", Img, "SUM", "DATA")
    outZonal.save(outZonalName)
    print baseName +" done!"
    return baseName


def assignLCinfo(ImgList,District):
    # assign the areas of agriculture and natural vegetation to the district shapefile
    outPntName="LCdstPt"
    arcpy.FeatureToPoint_management(district, outPntName, "INSIDE")
    field_names = [f.name for f in arcpy.ListFields(outPntName)]

    for Img in ImgList:
        ExtractMultiValuesToPoints(outPntName, [[Img,Img[:2]+Img[4:6]]], "NONE")

    arcpy.AddMessage("finish extracting "+outZonalName)
    arcpy.AddMessage("  ")
    baseName=os.path.basename(ImgList)


