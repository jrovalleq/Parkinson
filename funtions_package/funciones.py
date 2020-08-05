# -*- coding: utf-8 -*-
"""funciones.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o4ZbrMC5xStjWK7NuwlqhyIufUD6NUIT

Packages
"""

#function ClickConnect(){
#console.log("Working"); 
#document.querySelector("colab-toolbar-button#connect").click() 
#}
#setInterval(ClickConnect,60000)
#Importacion de librerias
import pyfreesurfer as fs
from pyfreesurfer import __version__ as version
from pyfreesurfer.segmentation.cortical import recon_all
from pyfreesurfer.wrapper import FSWrapper
from pyfreesurfer import DEFAULT_FREESURFER_PATH
from pyfreesurfer.conversions.volconvs import mri_convert
from pyfreesurfer.conversions.volconvs import mri_convert
import os
from os import listdir
from os import remove
import itk
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
import shutil
import ipywidgets
from ipywidgets import interact, fixed

"""Function PreProcess with Freesurfer"""

#Esta funcion realiza el preproceso de una imagen por medio de la funcion autorecon1 freesurfer,recibe las variables:
#indirection = Dirección donde se encuentra la imagen
#imagename = Nombre y direccion de la imagen de la imagen 
#outdirection = Direccion de salida de la funcion, debe ser una carpeta existente 
def PreProcesFreesufer(indirection, imagename, outdirection):
    fs.configuration.environment(sh_file=None, env={})
    fs.segmentation.cortical.recon_all(indirection, imagename, outdirection, 
                                       reconstruction_stage = "autorecon1", 
                                       fsconfig = '/usr/local/freesurfer/SetUpFreeSurfer.sh')



"""Function Registratio Method"""

#Funcion de registro de imagenes siguiendo el funcionamiento de ANTS implementando funciones de ITK, recibe las variables:
#fixed_image: imagen objetivo
#moving_image: imagen la cual se busca alinear con la imagen objetivo
#La salida de esta funcion son:
#final_transform: Imagen Registrada
#registration_method.GetMetricValue(): Valor de la metrica del registro para este caso, mutual information
def RegistrationMethod(fixed_image, moving_image):
    initial_transform = sitk.CenteredTransformInitializer(fixed_image, moving_image, 
                                                      sitk.Euler3DTransform(), 
                                                      sitk.CenteredTransformInitializerFilter.GEOMETRY)
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, estimateLearningRate=registration_method.Once)
    registration_method.SetOptimizerScalesFromPhysicalShift() 
    registration_method.SetInitialTransform(initial_transform, inPlace=False)
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [4,2,1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas = [2,1,0])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    final_transform = registration_method.Execute(fixed_image, moving_image)
    print('Final metric value: {0}'.format(registration_method.GetMetricValue()))
    print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))
    return (final_transform, registration_method.GetMetricValue())



"""Function to convert file mgz to file nii"""

#Esta funcion Convierte los archivos .mgz a .nii
#por optimizar
fsdir2 = '/home/jarok/Documentos/Parkinson/DB/IBSR/img'
image  = '/home/jarok/Documentos/Parkinson/DB/IBSR/img/01_seg/mri/brainmask.mgz'
mgztoniic = '/home/jarok/Documentos/mgztonii'
def mgztonii(ImagesDirection, ImageToConvert, OutDirection):
    fs.conversions.volconvs.mri_convert(ImagesDirection, ImagesDirection, ImagesDirection, 
                                    fsconfig='/usr/local/freesurfer/SetUpFreeSurfer.sh', )

"""Function to Remove freesurfer trash"""

#Esta funcion elimina las carpetas creadas por fresurfer diferentes a la carpeta MRI donde quedan almacenada la informacion de interes
#La Variable que recibe es la direccion de la carpeta del sujeto 
def PosFreesurfer(FreesurferSujectDirection):
    if os.path.isdir(FreesurferSujectDirection):
        print('La carpeta existe.');
        Files = listdir(FreesurferSujectDirection)
        for i in range(len(Files)):
            File = FreesurferSujectDirection + "/" + Files[i]
            if Files[i] == 'mri':
                print('MRI sin Cambio')
            else:
                shutil.rmtree(File)
                print(File, 'Ha sido removido')
    else:
        print('La carpeta no existe.')


"""Function to remove folder MRI trash"""

#Esta Funcion elimina dentro de la carpeta MRI todas las imagnes que no se necesitan posteriormente
#dejando sin alteracion el brainmask, la imagen original y rawavg
#la variable que recibe es la direccion de la carpeta MRI de un sujeto  
def PosFreesurferMRI(FreesurferSujectDirectionMRI):
    if os.path.isdir(FreesurferSujectDirectionMRI):
        print('La carpeta existe.');
        Files = listdir(FreesurferSujectDirectionMRI)
        for i in range(len(Files)):
            File = FreesurferSujectDirectionMRI + "/" + Files[i]
            if Files[i] == 'orig':
                Fileorig = listdir(File)
                Fileorig = File + '/' + Fileorig[0]
                shutil.move(Fileorig, FreesurferSujectDirectionMRI )
                shutil.rmtree(File)
                print('Imagen original ha cambiado a la carpeta principal')
            elif Files[i] == 'brainmask.mgz':
                print('Brain Mask sin cambio')
            elif Files[i] == 'rawavg.mgz':
                print('rawavg.mgz sin cambio')
            else:
                if os.path.isdir(File):
                    shutil.rmtree(File)
                    print(File, 'Ha sido removido')
                else:
                    remove(File)
                    print(File, 'Ha sido removido')
    else:
        print('La carpeta no existe.')



"""Function Image and Brainmask convert to nii file"""

# Esta funcion realiza la conversion de la imagen y el Brainmask creado por freesurfer a .nii 
#la variable que recibe es: ImagesDirection: Direccon de las imagenes
def PosFreesurferConvert(ImagesDirection):
    ImagesDirectionSplit = ImagesDirection.split('/')
    ImagesDirectionSplit = ImagesDirectionSplit[-1]
    ImagesDestinyDirection = ImagesDirection.strip(ImagesDirectionSplit)
    ImagesDestinyDirection = ImagesDestinyDirection.rstrip('/')
    ImagesDestinyDirectionSplit = ImagesDestinyDirection.split('/')
    ImagesDestinyDirectionSplit = ImagesDestinyDirectionSplit[-1]
    ImagesConvertDestinyDirection = ImagesDestinyDirection.strip(ImagesDestinyDirectionSplit)
    ImagesConvertDestinyDirection = ImagesConvertDestinyDirection.rstrip('/')
    Images = listdir(ImagesDirection)
    for i in range(len(Images)):
        Image = ImagesDirection + "/" + Images[i]
        fs.conversions.volconvs.mri_convert(ImagesConvertDestinyDirection, Image, ImagesConvertDestinyDirection, 
                                    fsconfig='/usr/local/freesurfer/SetUpFreeSurfer.sh', ) 
    shutil.rmtree(ImagesDirection)


"""Function to correct nii Files name"""

#Esta funcion elimina las palabras agregadas por freesurfer al nombre de las imagenes
#LA variable que ingresa: ImagesDirection= la direccion de las imagenes 
def PosFreesurferNameCorrection(ImagesDirection):
    Images = listdir(ImagesDirection)
    for i in range(len(Images)):
        Image = ImagesDirection + "/" + Images[i]
        ImageName = Images[1]
        ImageName = ImageName.split('.')
        ImageName.remove('native')
        ImageSubject = ImageName[0]
        ImageName = ".".join(ImageName)
        
        if i == 0:
            ImageName = Images[0]
            ImageName = ImageName.split('.')
            ImageName.remove('native')
            ImageName.insert(0, ImageSubject)
            ImageName = ".".join(ImageName)
            os.rename(Image, ImagesDirection + "/" + ImageName)
        if i == 1:
            ImageName = Images[1]
            ImageName = ImageName.split('.')
            ImageName.remove('native')
            ImageName = ".".join(ImageName)
            os.rename(Image, ImagesDirection + "/" + ImageName)
        if i == 2:
            ImageName = Images[2]
            ImageName = ImageName.split('.')
            ImageName.remove('native')
            ImageName = ".".join(ImageName)
            os.rename(Image, ImagesDirection + "/" + ImageName)



"""Fucntion To Get a Roi without ITK iterators"""

#Esta funcion crea la rio de un grupo de imagenes con una estructura segmentada por medio de una operacion OR
#variables de ingreso: SegmentedImagesDirrection = direccion de las imagenes
#variables de salida: Roi = array de la Roi de todas las imagenes 
#                     RoiImage = imagen del mimsmo tamaño delas imagenes con la Roi  
def GetRoiFromArrays(SegmentedImagesDirection):
    Images = listdir(SegmentedImagesDirection)    
    for i in range(len(Images)):
        Image = SegmentedImagesDirection + Images[i]
        SegmentedImage = sitk.ReadImage(Image)
        ArrayOfSegmentedImage = sitk.GetArrayFromImage(SegmentedImage)
        ArrayOfSegmentedImage = ArrayOfSegmentedImages.astype(int)
        np.append(ArrayOfSegmentedImages, ArrayOfSegmentedImage)
    Roi = ArrayOfSegmentedImages[1]
    for i in range(len(ArrayOfSegmentedImages)-1):
        Roi = np.bitwise_or(Roi, ArrayOfSegmentedImages[i])
        RoiImage = sitk.GetImageFromArray(Roi)
    return(Roi, RoiImage)

"""Function to find the bounding box without ITK iterators"""

#Esta funacion Creauna imagen con  el cubo más pequeño posible que contiene la roi que recibe
#Recibe la variable: Roi direction: RoiDirection = Direccion de la imagen que contiene la roi
#Lavariable de salida es una imagen con el Bounding box
def GetRoiBoundingBox(RoiDirection):
    Roi = sitk.ReadImage(RoiDirection)
    RoiArray = sitk.GetArrayFromImage(Roi)
    RoiArray = RoiArray.astype(int)
    for i in range(len(RoiArray[1,:,:])):
        k = np.where(RoiArray[i,:,:] == 1)
        k = np.Array(k)
        x = k.size
        #print(i,x)
        if x >= 1:
            icordenadax = i
            break
    for i in reversed(range(len(RoiArray[1,:,:]))):
        k = np.where(RoiArray[i,:,:] == 1)
        k = np.Array(k)
        x = k.size
        #print(i,x)
        if x >= 1:
            ocordenadax = i
            break
    for i in range(len(RoiArray[:,1,:])):
        k = np.where(RoiArray[:,i,:] == 1)
        k = np.Array(k)
        y = k.size
        #print(i,y)
        if y >= 1:
            icordenaday = i
            break
    for i in reversed(range(len(RoiArray[:,1,:]))):
        k = np.where(RoiArray[:,i,:] == 1)
        k = np.Array(k)
        y = k.size
        #print(i,y)
        if y >= 1:
            ocordenaday = i
            break
    for i in range(len(RoiArray[:,:,1])):
        k = np.where(RoiArray[:,:,i] == 1)
        k = np.Array(k)
        z = k.size
        #print(i,z)
        if z >= 1:
            icordenadaz = i
            break
    for i in reversed(range(len(RoiArray[:,:,1]))):
        k = np.where(RoiArray[:,:,i] == 1)
        k = np.Array(k)
        z = k.size
        #print(i,z)
        if z >= 1:
            ocordenadaz = i
            break
    ini = np.Array([icordenadax,icordenaday,icordenadaz])
    out = np.Array([ocordenadax,ocordenaday,ocordenadaz])
    sizeBB = out-ini
    BB = np.ones((sizeBB))
    compx2x = (len(RoiArray[1,:,:]))-out[0]
    compX1 = np.zeros((ini[0], sizeBB[1], sizeBB[2]))
    compX2 = np.zeros((compx2x, sizeBB[1], sizeBB[2]))
    BB = np.concatenate((compX1, BB, compX2), axis=0 )
    sizeBBX = BB.shape[0]
    compy2y = (len(RoiArray[:,1,:]))-out[1]
    compY1 = np.zeros((sizeBBX, ini[1], sizeBB[2]))
    compY2 = np.zeros((sizeBBX, compy2y, sizeBB[2]))
    BB = np.concatenate((compY1, BB, compY2), axis=1 )
    sizeBBX = BB.shape[0]
    sizeBBY = BB.shape[1]
    compz2z = (len(RoiArray[:,:,1]))-out[2]
    compZ1 = np.zeros((sizeBBX, sizeBBY, ini[2]))
    compZ2 = np.zeros((sizeBBX, sizeBBY, compz2z))
    BB = np.concatenate((compZ1, BB, compZ2), axis=2 )
    BBox = sitk.GetImageFromArray(BB)
    return(sizeBB, BB, BBox)


def myshow(img, title=None, margin=0.05, dpi=80):
    nda = sitk.GetArrayFromImage(img)
    spacing = img.GetSpacing()

    if nda.ndim == 3:
        # fastest dim, either component or x
        c = nda.shape[-1]

        # the the number of components is 3 or 4 consider it an RGB image
        if c not in (3, 4):
            nda = nda[nda.shape[0] // 2, :, :]

    elif nda.ndim == 4:
        c = nda.shape[-1]

        if c not in (3, 4):
            raise RuntimeError("Unable to show 3D-vector Image")

        # take a z-slice
        nda = nda[nda.shape[0] // 2, :, :, :]

    xsize = nda.shape[1]
    ysize = nda.shape[0]

    # Make a figure big enough to accommodate an axis of xpixels by ypixels
    # as well as the ticklabels, etc...
    figsize = (1 + margin) * xsize / dpi, (1 + margin) * ysize / dpi

    plt.figure(figsize=figsize, dpi=dpi, tight_layout=True)
    ax = plt.gca()

    extent = (0, xsize * spacing[0], ysize * spacing[1], 0)

    t = ax.imshow(nda, extent=extent, interpolation=None)

    if nda.ndim == 2:
        t.set_cmap("gray")

    if(title):
        plt.title(title)

    plt.show()


def myshow3d(img, xslices=[], yslices=[], zslices=[], title=None, margin=0.05,
             dpi=80):
    img_xslices = [img[s, :, :] for s in xslices]
    img_yslices = [img[:, s, :] for s in yslices]
    img_zslices = [img[:, :, s] for s in zslices]

    maxlen = max(len(img_xslices), len(img_yslices), len(img_zslices))


    img_null = sitk.Image([0, 0], img.GetPixelID(),
                          img.GetNumberOfComponentsPerPixel())

    img_slices = []
    d = 0

    if len(img_xslices):
        img_slices += img_xslices + [img_null] * (maxlen - len(img_xslices))
        d += 1

    if len(img_yslices):
        img_slices += img_yslices + [img_null] * (maxlen - len(img_yslices))
        d += 1

    if len(img_zslices):
        img_slices += img_zslices + [img_null] * (maxlen - len(img_zslices))
        d += 1

    if maxlen != 0:
        if img.GetNumberOfComponentsPerPixel() == 1:
            img = sitk.Tile(img_slices, [maxlen, d])
        # TO DO check in code to get Tile Filter working with vector images
        else:
            img_comps = []
            for i in range(0, img.GetNumberOfComponentsPerPixel()):
                img_slices_c = [sitk.VectorIndexSelectionCast(s, i)
                                for s in img_slices]
                img_comps.append(sitk.Tile(img_slices_c, [maxlen, d]))
            img = sitk.Compose(img_comps)

    myshow(img, title, margin, dpi)

