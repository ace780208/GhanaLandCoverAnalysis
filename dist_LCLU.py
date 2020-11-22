#-------------------------------------------------------------------------------
# Name:        district LC extraction
# Purpose:     This python-based script for arcGIS toolbox of extracting built-up
#              area for each district in 2000 and 2010.
#
# Author:      Ace
#
# Created:     09/03/2015
# Copyright:   (c) Ace 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, os, sys
from arcpy.sa import *

rawPath=sys.argv[1] #The work directory of the file
c2000workspace=sys.argv[2]  #2000 land cover map path
c2010workspace=sys.argv[3]  #2010 land cover map path
wantedClass=sys.argv[4]     #The land cover scheme number for built-up
studyarea=sys.argv[5]       #The dataset for storing the extracting info
outputClassClip=sys.argv[6] #The input shapefile (features layer) name

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True

env.workspace=rawPath

def extractClass(Img,wantclass):
    # extract the built-up from a raster land cover map based on the land cover scheme number
    fileName=os.path.basename(Img).rstrip(os.path.splitext(Img)[1])
    outName="Bu"+fileName[1:5]
    outCon= Con(Img==wantclass,1,0)
    outCon.save(rawPath+"\\"+outName)
    return outName

def countBuPx(Img,district):
    # count the number of pixel for built-up with a zonal statistic tool
    outZonalName=Img+"_dist"
    outZonal=ZonalStatistics(district, "OBJECTID_1", Img, "SUM", "DATA")
    outZonal.save(outZonalName)

    #convert roadBuf to points to extract zonalPx values
    outPntName=Img+"_distPnt"
    arcpy.FeatureToPoint_management(district, outPntName, "INSIDE")
    ExtractMultiValuesToPoints(outPntName, [[outZonalName]], "NONE")
    return outPntName

def assignBuCount(district,Pnt):
    # update the pixel counts of built-up in the output shapefile based on the zonal statistics layers

    # Use ListFields to get a list of field objects
    fieldObjList = arcpy.ListFields(Pnt)

    # Create an empty list that will be populated with field names
    fieldNameList = []

    # For each field in the object list, add the field name to the
    #  name list.  If the field is required, exclude it, to prevent errors
    for field in fieldObjList:
        if field.name=="distance" or field.name=="Bu2000" or field.name=="Bu2010" or field.name=="District":
            continue
        if not field.required:
            fieldNameList.append(field.name)

    # Execute DeleteField to delete all fields in the field list.
    arcpy.DeleteField_management(Pnt, fieldNameList)

    fieldObj= arcpy.ListFields(Pnt)
    fieldName=[]
    for field in fieldObj:
            fieldName.append(field.name)

    # Update Bu areas within the districts
    for field in fieldName:
        if field=="Bu2000":
            BuField="Bu2000"

        elif field=="Bu2010":
            BuField="Bu2010"

        else:
            continue

        arcpy.AddField_management(district, BuField, "FLOAT")
        rows1=arcpy.UpdateCursor(district,sort_fields="District A")
        for row1 in rows1:
            rows2 = arcpy.SearchCursor(Pnt,sort_fields="District A")
            for row2 in rows2:
                if row2.getValue("District")==row1.getValue("District"):
                    row1.setValue(BuField,float(row2.getValue(BuField))*12.5*12.5)
                    rows1.UpdateRow(row1)
                    break
            del row2
            del rows2
        del row1
        del rows1

#-------------------------------------------------------------------------------
copyStudyarea=studyarea+"_LCData"
arcpy.Copy_management(district, new_dist)
BuLayer1=extractClass(c2000workspace,wantedClass)
BuLayer2=extractClass(c2010workspace,wantedClass)

newStudyArea=processbuf(copyStudyarea,roadBuf)

zonalStat1=countBufPx(BuLayer1,copyStudyarea)
assignBufCount(copyStudyarea,zonalStat1)

zonalStat2=countBufPx(BuLayer2,copyStudyarea)
assignBufCount(copyStudyarea,zonalStat2)

