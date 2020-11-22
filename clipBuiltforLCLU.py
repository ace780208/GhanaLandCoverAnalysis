#-------------------------------------------------------------------------------
# Name:        extract Built-up area in the road buffer
# Purpose:      This is a python script for arcGIS toolbox to extract built-up
#               area for each district in Southeastern Ghana within 0.25, 0.5,
#               1, 2, and 5 km buffer of major road (i.e. highway) for 2000 and
#               and 2010.
#
# Author:      Ace
#
# Created:     09/03/2015
# Copyright:   (c) Ace 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, os, sys
from arcpy.sa import *

rawPath=sys.argv[1] # the path for work directory
c2000workspace=sys.argv[2] # the path for 2000 land cover map
c2010workspace=sys.argv[3] # the path for 2010 land cover map
wantedClass=sys.argv[4] # the scheme number for built-up class in the land cover maps
roadBufforC=sys.argv[5] # the road buffer polygon shapefile from the 2000 built-up shapefile
roadBufforD=sys.argv[6] # the road buffer polygon shapefile based on major road
studyarea=sys.argv[7]   # The input shapefile

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True

arcpy.env.workspace=rawPath

def extractClass(workspace,Img,wantclass):
    # extract the built-up from a raster land cover map based on the land cover scheme number
    inRaster=Raster(Img)
    fileName=os.path.basename(Img)
    outName="Bu"+fileName[1:5]
    outCon= Con(inRaster==int(wantclass),1,0)
    outCon.save(workspace+"\\"+outName)
    arcpy.AddMessage("Finish Con class "+str(wantclass) +" for "+outName)
    return outName

def extractNewBu(workspace,Img1, Img2):
    # extract the new built-up from 2000 and 2010 land cover map
    inRas1=Raster(Img1)
    inRas2=Raster(Img2)
    Img1Name=os.path.basename(Img1)
    Img2Name=os.path.basename(Img2)
    outputCom="Combined"
    com=Combine([inRas1, inRas2])
    com.save(outputCom)
    arcpy.AddMessage("Finish Combined")

    cur=arcpy.SearchCursor(outputCom)
    newBu=0
    for row in cur:
        if row.getValue(Img1Name)!=1 and row.getValue(Img2Name)==1:
            newBu=row.getValue("Value")

    outputRe=workspace+"\\newBu"
    reclass=Reclassify(outputCom,"Value",RemapValue([[newBu,1]]),"NODATA")
    reclass.save(outputRe)
    arcpy.AddMessage("Finish reclassify Combined")
    return outputRe

def processbuf(studyArea,roadBuffer):
    #get road buffer within the study area
    outputBuf=roadBuffer+"_Clip"
    arcpy.Clip_analysis(roadBuffer, studyArea, outputBuf)

    #label road buffer with district names
    outputstudyareaBuf=roadBuffer+"_dist"
    arcpy.Identity_analysis(studyArea,outputBuf,outputstudyareaBuf)

    return outputstudyareaBuf

def countBuPx(Img,district):
    # count the number of pixel for built-up with zonal statistic tool
    baseName=os.path.basename(Img)
    outZonalName=baseName+"_dst"
    outZonal=ZonalStatistics(district, "DISTRICT", Img, "SUM", "DATA")
    outZonal.save(outZonalName)

    #convert roadBuf to points to extract zonalPx values
    outPntName=Img+"_dstPt"
    arcpy.FeatureToPoint_management(district, outPntName, "INSIDE")
    ExtractMultiValuesToPoints(outPntName, [[outZonalName,outZonalName]], "NONE")
    arcpy.AddMessage("finish extracting "+outZonalName)
    arcpy.AddMessage("  ")
    return outPntName

def countNewBuPx(Img, district):
    # derive the pixel count of new built-up with zonal statistic tool
    baseName=os.path.basename(Img)
    outZonalName=baseName+"_dst"
    outZonal=ZonalStatistics(district, "DISTRICT", Img, "SUM", "DATA")
    outZonal.save(outZonalName)

    #convert roadBuf to points to extract zonalPx values
    outPntName=Img+"_dstPt"
    arcpy.FeatureToPoint_management(district, outPntName, "INSIDE")
    ExtractMultiValuesToPoints(outPntName, [[outZonalName,outZonalName]], "NONE")
    arcpy.AddMessage("finish extracting "+outZonalName)
    arcpy.AddMessage("  ")
    return outPntName

def countNewBuBufPx(Img,roadBuffer):
    # derive the pixel count of new built-up with zonal statistic tool with the road buffer file
    baseName=os.path.basename(Img)
    desc=arcpy.Describe(roadBuffer)
    RdName=desc.name
    partRdName=RdName[5:9]
    outZonalName=baseName+partRdName
    outZonal=ZonalStatistics (roadBuffer, "OBJECTID", Img, "SUM", "DATA")
    outZonal.save(outZonalName)

    #convert roadBuf to points to extract zonalPx values
    outPntName=Img+"_Pnt"+partRdName
    arcpy.FeatureToPoint_management(roadBuffer, outPntName, "INSIDE")
    ExtractMultiValuesToPoints(outPntName, [[outZonalName]], "NONE")
    arcpy.AddMessage("finish extracting "+outZonalName)
    arcpy.AddMessage("  ")
    return outPntName

def assignBuCount(district,Pnt):
    # assign the built-up pixel number to each district for the selected year
    # Use ListFields to get a list of field objects
    fieldObjList = arcpy.ListFields(Pnt)

    # Create an empty list that will be populated with field names
    fieldNameList = []

    # For each field in the object list, add the field name to the
    #  name list.  If the field is required, exclude it, to prevent errors
    for field in fieldObjList:
        if field.name=="distance" or field.name=="Bu2000_dst" or field.name=="Bu2010_dst" or field.name=="DISTRICT" or field.name=="newBu_dst":
            continue
        if not field.required:
            fieldNameList.append(field.name)

    # Execute DeleteField to delete all fields in the field list.
    arcpy.DeleteField_management(Pnt, fieldNameList)

    fieldObj= arcpy.ListFields(Pnt)
    fieldName=[]
    for field in fieldObj:
            fieldName.append(field.name)
            arcpy.AddMessage(field.name)

    # Update Bu areas within the districts
    for field in fieldName:
        arcpy.AddMessage("now field: "+field)
        if field=="Bu2000_dst":
            BuField="Bu2000"
            nonBuField="nonBu2000"

        elif field=="Bu2010_dst":
            BuField="Bu2010"
            nonBuField="nonBu2010"

        elif field=="newBu_dst":
            BuField="newBu"
            arcpy.AddField_management(district, BuField, "DOUBLE")
            rows1=arcpy.UpdateCursor(district)
            for row1 in rows1:
                rows2 = arcpy.SearchCursor(Pnt)
                for row2 in rows2:
                    if row2.getValue("DISTRICT")==row1.getValue("DISTRICT"):
                        row1.setValue(BuField,row2.getValue(field)*12.5*12.5) #Change for cell size if necessary # Area unit=m2
                        rows1.updateRow(row1)
                        break
                del row2
                del rows2
            del row1
            del rows1
            arcpy.AddField_management(district, "PNewBu", "DOUBLE")
            arcpy.AddField_management(district, "NBuOBu00", "DOUBLE")
            arcpy.AddField_management(district, "NBuONnBu00", "DOUBLE")
            cur=arcpy.UpdateCursor(district)
            for row in cur:
                row.setValue("PNewBu",row.getValue(BuField)/row.getValue("Shape_Area")*100)
                row.setValue("NBuOBu00",row.getValue(BuField)/row.getValue("Bu2000")*100)
                row.setValue("NBuONnBu00",row.getValue(BuField)/row.getValue("nonBu2000")*100)


            del row
            del cur
            continue

        else:
            arcpy.AddMessage("Field: "+ field+" ignored")
            continue

        arcpy.AddMessage("Field: "+ field+" passed, continue...")
        arcpy.AddMessage(BuField+" "+nonBuField)

        arcpy.AddField_management(district, BuField, "DOUBLE")
        arcpy.AddField_management(district,BuField+"Pct","DOUBLE")
        arcpy.AddField_management(district,nonBuField,"DOUBLE")
        arcpy.AddField_management(district,nonBuField+"Pct","DOUBLE")
        rows1=arcpy.UpdateCursor(district)
        for row1 in rows1:
            rows2 = arcpy.SearchCursor(Pnt)
            for row2 in rows2:
                if row2.getValue("DISTRICT")==row1.getValue("DISTRICT"):
                    row1.setValue(BuField,row2.getValue(field)*12.5*12.5) #Change for cell size if necessary # Area unit=m2
                    row1.setValue(BuField+"Pct",row2.getValue(field)*12.5*12.5/row1.getValue("Shape_Area")*100)# Pct Area unit=%
                    row1.setValue(nonBuField,row1.getValue("Shape_Area")-row2.getValue(field)*12.5*12.5)# Area unit=m2
                    row1.setValue(nonBuField+"Pct",(1-(float(row2.getValue(field))*12.5*12.5/row1.getValue("Shape_Area")))*100)# Pct Area unit=%
                    rows1.updateRow(row1)
                    break
            del row2
            del rows2
        del row1
        del rows1

def assignNewBuBufConut(district,Pnt):
    # assign the new built-up pixel number to each district
    values = [row[0] for row in arcpy.da.SearchCursor(Pnt, "distance")]
    BufList = set(values)
    # Use ListFields to get a list of field objects
    fieldObjList = arcpy.ListFields(Pnt)

    # Create an empty list that will be populated with field names
    fieldNameList = []

    # For each field in the object list, add the field name to the
    #  name list.  If the field is required, exclude it, to prevent errors
    for field in fieldObjList:
        if field.name=="distance" or field.name=="newBuOutC" or field.name=="DISTRICT"or field.name=="newBuOutD":
            continue
        if not field.required:
            fieldNameList.append(field.name)

    # Execute DeleteField to delete all fields in the field list.
    arcpy.DeleteField_management(Pnt, fieldNameList)


    # Update new Bu areas within the districts
    for field in fieldNameList:
        if Pnt[-1]=="C":
            end="C"
            BuField="newBuOutC"

        elif Pnt[-1]=="D":
            end="D"
            BuField="newBuOutD"

        else:
            continue

        for dist in BufList:
            if dist==0:
                outside=int(max(BufList)*1000)
                newfield="NBu"+str(outside)+"mOut"+end

            else:
                inside=int(dist*1000)
                newfield="NBu"+str(inside)+"mIn"+end

            arcpy.AddField_management(district, newfield, "DOUBLE")
            arcpy.AddField_management(district,"P"+newfield,"DOUBLE")
            rows1=arcpy.UpdateCursor(district)
            for row1 in rows1:
                rows2 = arcpy.SearchCursor(Pnt)
                for row2 in rows2:
                    if row2.getValue("distance")==dist and row2.getValue("DISTRICT")==row1.getValue("DISTRICT"):
                        row1.setValue(newfield,float(row2.getValue(BuField))*12.5*12.5) #Change for cell size if necessary
                        row1.setValue("P"+newfield,(float(row2.getValue(BuField))*12.5*12.5/row1.getValue("newBu"))*100)
                        #new Bu proportion in each buffer ring, so the total of buffer rings will be 100%
                        rows1.updateRow(row1)
                        break
                del row2
                del rows2
            del row1
            del rows1

def NewBuPct (district):
    # calculate the % of built up within each district
    arcpy.AddField_management(district,"NBuOPBu00","DOUBLE")
    arcpy.AddField_management(district,"NBuOPNnBu00","DOUBLE")
    cur=arcpy.UpdateCursor(district)
    for row in cur:
        row.setValue("NBuOPBu00",(row.getValue("newBu")/row.getValue("Shape_Area"))*100/row.getValue("Bu2000Pct"))
        row.setValue("NBuOPNnBu00",(row.getValue("newBu")/row.getValue("Shape_Area"))*100/row.getValue("nonBu2000Pct"))
        cur.updateRow(row)

    del cur
    del row

def PopCount(district):
    # calculate population density based on the population column and district area in 2000 and 2010
    arcpy.AddField_management(district,"PopDens00","DOUBLE")
    arcpy.AddField_management(district,"PopDens10","DOUBLE")
    cur=arcpy.UpdateCursor(district)
    for row in cur:
        row.setValue("PopDens00",row.getValue("Pop2000")/row.getValue("Shape_Area")*1000000)
        row.setValue("PopDens10",row.getValue("Pop2010")/row.getValue("Shape_Area")*1000000)
        cur.updateRow(row)

    del row
    del cur

def Derivatives(district):
    # calculate population density based on the population and built-up area in 2000 and 2010
    arcpy.AddField_management(district,"dvlpDens00","DOUBLE")
    arcpy.AddField_management(district,"dvlpDens10","DOUBLE")
    arcpy.AddField_management(district,"RePpChOAvD","DOUBLE")

    cur=arcpy.UpdateCursor(district)
    for row in cur:

        row.setValue("dvlpDens00",row.getValue("Pop2000")/row.getValue("Bu2000")*1000000)
        row.setValue("dvlpDens10",row.getValue("Pop2010")/row.getValue("Bu2010")*1000000)

        cur.updateRow(row)

    del cur
    del row

    arcpy.AddField_management(district,"dvlpDnsChg","DOUBLE")

    cur=arcpy.UpdateCursor(district)
    for row in cur:
        row.setValue("dvlpDnsChg",row.getValue("dvlpDens10")-row.getValue("dvlpDens00"))
        cur.updateRow(row)

    del cur
    del row

    cur=arcpy.UpdateCursor(district)
    for row in cur:
        row.setValue("RePpChOAvD",((row.getValue("Pop2010")-row.getValue("Pop2000"))/row.getValue("Pop2000"))/(row.getValue("NBuOPNnBu00")))
        cur.updateRow(row)

    del cur
    del row


#-------------------------------------------------------------------------------
copyStudyarea=studyarea+"_LCData"
arcpy.Copy_management(studyarea, copyStudyarea)

BuLayer1=extractClass(rawPath,c2000workspace,wantedClass)
BuLayer2=extractClass(rawPath,c2010workspace,wantedClass)

zonalStat1=countBuPx(BuLayer1,copyStudyarea)
assignBuCount(copyStudyarea,zonalStat1)

zonalStat2=countBuPx(BuLayer2,copyStudyarea)
assignBuCount(copyStudyarea,zonalStat2)

newBu=extractNewBu(rawPath,BuLayer1,BuLayer2)
zonalStat3=countNewBuPx(newBu,copyStudyarea)
assignBuCount(copyStudyarea,zonalStat3)
#new Bu % from the distance Buffers from the major roads
newStudyArea1=processbuf(copyStudyarea,roadBufforD)
zonalStat4=countNewBuBufPx(newBu,newStudyArea1)
assignNewBuBufConut(copyStudyarea,zonalStat4)

#new Bu % from the distance Buffers from nearest 2000Bu
newStudyArea2=processbuf(copyStudyarea,roadBufforC)
zonalStat5=countNewBuBufPx(newBu,newStudyArea2)
assignNewBuBufConut(copyStudyarea,zonalStat5)

PopCount(copyStudyarea)
NewBuPct(copyStudyarea)
Derivatives(copyStudyarea)
