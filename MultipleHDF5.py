#contoh script processing data IMERG format HDF5 sederhana
#modifikasi dari script di https://www.hatarilabs.com/ih-en/massive-operations-on-rasters-with-qgis3-and-python-tutorial

#import modul yang dibutuhkan
from osgeo import gdal, osr
import os
import numpy as np
from qgis.core import *
import qgis.utils


#direktori data
wkdir='/D/Semester_4/SIMet/Praktikum/Modul_5_SIMET/Data/IMERG_HDF5'
os.chdir(wkdir) #ubah current direktory ke direktori data

#nama-nama file
totallinks = os.listdir(os.getcwd())
#print(totallinks)
#semua file dengan ekstensi .HDF5 di append ke sebuah list
hdflinks = []
for link in totallinks:
    if link[-4:] == 'HDF5':
        hdflinks.append(link)

#hitung akumulasi dari semua data yg ada di list 
sum_array = np.zeros([1800,3600]) #array/matriks untuk mengisi hasil perhitungan 
#loop setiap file
for link in hdflinks:
    hdf_ds = gdal.Open(link, gdal.GA_ReadOnly) #open file
    print(link)
    band_ds = gdal.Open(hdf_ds.GetSubDatasets()[7][0], gdal.GA_ReadOnly) #ambil variabel precipitationCal (di layer ke-7)
     
    band_array = band_ds.ReadAsArray() #baca array nya sebagai numpy array
    band_array[band_array<0] = 0 #filter data NaN --> ch<0
        
    #tranpose array data: (nlon,nlat) menjadi (nlat,nlon)
    #hitung akumulasi: karena data adalah rainrate (mm/hr) per 30 menit, maka diubah dulu ke akumulasi 30 menit
    sum_array = band_array.T[::-1]*0.5 + sum_array 
    
#Geo-transformasi numpy array
geotransform = ([-180,0.1,0,90,0,-0.1]) #[longitude_paling_kiri,dlon,0,latitude_paling_atas,0,dlat]
outfile="../PrecipAccum_20210408_1900_2200_UTC.tif" #nama file output dalam format GeoTiff
#buat rasternya
raster = gdal.GetDriverByName('GTiff').Create(outfile,3600,1800,1,gdal.GDT_Float32)
raster.SetGeoTransform(geotransform)
#set proyeksi rasternya
srs=osr.SpatialReference()
srs.ImportFromEPSG(4326)
raster.SetProjection(srs.ExportToWkt())
#tulis ke file output
raster.GetRasterBand(1).WriteArray(sum_array)    
	 
raster=None
     
#load ke QGIS
rlayer=iface.addRasterLayer(outfile,"precip","gdal")
