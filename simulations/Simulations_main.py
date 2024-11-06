import numpy as np
import levitate
from matplotlib import pyplot as plt
# import src.coordinates
from math import pi
import pandas as pd
import matplotlib
import random
import os
import sys
from importlib import import_module 

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


# c0=343 #m/s  speed of sound in the air
freq=40 #kHz or ms^-1  operational frequency of ultrasonic transducers
# wavelength=c0/freq #mm  
medium = 'air'

if medium == 'CO2':
    gas = levitate.materials.Air()
    gas.c = 269
    gas.dynamic_viscosity = 1.496e-5
    gas.rho = 1.784
elif medium == 'air':
    gas = levitate.materials.Air()
    gas.c = 343.2367605312694
    gas.dynamic_viscosity = 1.85e-05
    gas.rho = 1.2040847588826422

path_to_library=str('C:/Users/argyri/Desktop/Python_codes/') #!!! To adjust to the path that leads to the file: coordinates.py ###  
sys.path.insert(0, path_to_library)
source_coordinates = import_module("coordinates")

# ----------------------------------------
#### Simulation Parameters :
lev_list = ['mk3'] #"mk1", "mk2",  "mk3"
phase = "opposition"    #opposition or quadrature  or in phase => To have a central antinode or a central node

# material='water'
# R_obj=0.001 #m


#Colour bar range
# vmin=0      #Defines the minimum acoustic pressure in Pascals on the 2D map plots
# vmax=1700  #Defines the maximum acoustic pressure in pascals on the 2D map plots
# space=250

# levitate.materials.Gas(c=269, dynamic_viscosity=1.496e-5, rho=1.784)  #https://www.engineeringtoolbox.com/


#### Saving parameters:
path_save=str('change_this_to_the_directory_you_want_to_save_the_images_in')  #!!!
savefigure = False
fig_type='.svg'  
plt.rcParams['font.size'] = '12'


# zoom = 0.003                     # Shift (in mm) from the max transducer coordinates (to avoid singularities)                       
linear_nbpoints = 1001
map_nbpoints = 201
max_x = 0.012  #Define the +/- distance around the (0,0,0) along the x-axis
max_y = 0.012  #Define the +/- distance around the (0,0,0) along the y-axis
max_z = 0.012  #Define the +/- distance around the (0,0,0) along the z-axis  

j=0
plots = ['xy']     # 'x', 'y','z', 'xz', 'yz', 'xy']  
for levitator in lev_list:
    for i in plots:
        #Define mesh for the 2D plots
        meshsize = [5,5,5]          # Init number of points in x, y and z directions for the 3D mesh used in calculation
        if i == "x":
            isx = True
            meshsize[0] = linear_nbpoints
        if i == "y":
            isy = True
            meshsize[1] = linear_nbpoints 
        if i == "z":
            isz = True
            meshsize[2] = linear_nbpoints
        if i =="yz":
            isy = True
            isz = True
            meshsize[1] = map_nbpoints
            meshsize[2] = map_nbpoints
        if i =="xz":
            isx = True
            isz = True
            meshsize[0] = map_nbpoints
            meshsize[2] = map_nbpoints
        if i =="xy":
            isx = True
            isy = True
            meshsize[0] = map_nbpoints
            meshsize[1] = map_nbpoints
    
        # #Import coordinates
        if levitator=='LangLev':
            p0=10     # Reference pressure (Pa) used in levitate
            coord= source_coordinates.lev('LangLev')/ 1000
        else:
            p0=1      # Reference pressure (Pa) used in levitate
            coord = source_coordinates.lev(levitator) / 1000
    
    
        # -----------------------------------------
        #### Mesh struture :
    
        x = np.linspace(-max_x,max_x, meshsize[0])
        y = np.linspace(-max_y,max_y, meshsize[1])
        z = np.linspace(-max_z, max_z, meshsize[2])
    
        dx = x[1]-x[0]
        dy = y[1]-y[0]
        dz = z[1]-z[0]
        x0 = np.where(x==0)[0][0]
        y0 = np.where(y==0)[0][0]
        z0 = find_nearest(z, 0)[1]
        points = np.reshape(np.meshgrid(x, y, z, indexing = 'ij'), (3, -1))
    
        # ----------------------------------------
        ##### Transducer array :
        # Define phases of transducer arrays
        phases_down = 0.5*np.pi*np.ones((1,len(coord)//2)) 
        if phase == 'quadrature':
            phases_up = 0*np.pi*np.ones((1,len(coord)//2))
        elif phase == 'in phase':
            phases_up = 0.5*np.pi*np.ones((1,len(coord)//2)) 
        elif phase == 'opposition':
            phases_up = -0.5*np.pi*np.ones((1,len(coord)//2)) 
        
        # Calculate the normals of the coordinates
        normal = -1*coord / np.linalg.norm(coord, 2, axis=1, keepdims = 1)
        
        # Transform the matrixes
        coord = coord.T
        normal = normal.T
        
        # Append the phases of the lower and upper transducers.
        phases = np.append(phases_down,phases_up)
        
        # Calcluate the complex phase
        complex_phase = levitate.complex(phases)

        # Define the directivity of the transducers
        transducer = levitate.transducers.CircularRing(effective_radius=3e-3, p0=p0)    
        # Define the transducer arrays
        array = levitate.arrays.TransducerArray(coord, normal, transducer=transducer, transducer_size=0.01)
        array.freq=freq*1000
        
        # ----------------------------------------
        # Calculate the acoustic pressure
        pressure_calculation_instance = levitate.fields.Pressure(array) @ points
        pressure = abs(pressure_calculation_instance(complex_phase))
    
        # Calculate the Gor'Kov potential and gradient
        gorkov_calc = levitate.fields.GorkovPotential(array,radius = 1e-3) @ points
        gorkov_grad_calc = levitate.fields.GorkovGradient(array,radius = 1e-3) @ points
        
        gorkov = gorkov_calc(complex_phase)
        gorkov = gorkov.reshape(len(x),len(y),len(z))
        gorkov_grad = gorkov_grad_calc(complex_phase)
        # Calculate the acoustic radiation force applied on a small spherical rigid object based on Gor'kov's theory 
        F = -gorkov_grad.reshape(3,len(x),len(y),len(z))
        
        # Reshape the acoustic pressure matrix
        pressure = pressure.reshape(len(x),len(y),len(z))
    
        # Define the pressure arrays along the z, y, and x axes 
        pressure_z = pressure[x0,y0,:] #for x=y=0
        pressure_y = pressure[x0,:,z0] #for x=z=0
        pressure_x = pressure[:,y0,z0] #for y=z=0
      
        
        # ---------------------------------------------------------------
        ##### Plots :
        # --------------------------
        ##### 2d Pressure Map Y, Z :
        if i == "yz":
            fig,ax = plt.subplots(figsize = (502*max_x,406*max_z))
    
            cs = ax.contourf(y*1000,z*1000,pressure[x0,:,:].T,100, vmin = 0, vmax = 3300)  #, vmin = 0, vmax = vmax
            for a in cs.collections:
                a.set_edgecolor('face')
            plt.xlim((-max_y*1000,max_y*1000))
            plt.ylim((-max_z*1000,max_z*1000))
            plt.xlabel('Y (mm)', fontweight='bold', fontsize=15)
            plt.ylabel('Z (mm)', fontweight='bold', fontsize=15)
            plt.axis('equal')
            bar = fig.colorbar(cs)
            bar.set_label('Acoustic pressure (Pa)', rotation=90, fontsize=15)
    
            # plt.title("Theoretical pressure field Y, Z")
            if savefigure & isy & isz :
                plt.savefig(path_save+levitator+"_PressureField_yz_"+phase+fig_type, dpi = 300)
    
    
        # -------------------------------------
        ##### 2d Pressure Map X, Z :
        if i == "xz":
            fig,ax = plt.subplots(figsize = (502*max_x,406*max_z))
            cs = ax.contourf(x*1000,z*1000,pressure[:,y0,:].T,100, vmin = 0, vmax = 1000) # vmin = 0, vmax = 1100
            for a in cs.collections:
                a.set_edgecolor('face')
            plt.xlim((-max_y*1000,max_y*1000))
            plt.ylim((-max_z*1000,max_z*1000))
            plt.xlabel('X (mm)', fontweight='bold', fontsize=15)
            plt.ylabel('Z (mm)', fontweight='bold', fontsize=15)
            plt.axis('equal')
            bar = fig.colorbar(cs)  #, ticks=range(vmin, vmax, space)
            bar.set_label('Acoustic pressure (Pa)', rotation=90, fontweight='bold', fontsize=15)
                # plt.title("Theoretical pressure field X, Z")
            if savefigure & isx & isz :
              plt.savefig(path_save+levitator+"_PressureField_xz_"+phase+fig_type, dpi = 300)
                
        # --------------------------------------
        ##### 2d Pressure Map X, Y :
        if i == "xy":
            fig,ax = plt.subplots(figsize = (502*max_x,406*max_y))
            cs = ax.contourf(x*1000,y*1000,pressure[:,:,z0].T,100,  vmin=0, vmax=10e-14) #vmin=0, vmax=12
            for a in cs.collections:
                a.set_edgecolor('face')
            plt.xlim((-max_y*1000, max_y*1000))
            plt.ylim((-max_z*1000, max_z*1000))
            plt.xlabel('X (mm)', fontweight='bold', fontsize=15)
            plt.ylabel('Y (mm)', fontweight='bold', fontsize=15)
            plt.axis('equal')
            bar = fig.colorbar(cs)  #ticks=range(0, 220, 20)
            bar.set_label('Acoustic pressure (Pa)', rotation=90, fontweight='bold', fontsize=15)
            # plt.title("Theoretical pressure field X, Y")
            if savefigure & isx & isy:
              plt.savefig(path_save+levitator+"_PressureField_xy_"+phase+fig_type, dpi = 300)
    
        # ---------------------------------------
        #### 2D Gorkov Potential y,z :
        # if i == "yz":
        #     fig,ax = plt.subplots(figsize = (500*max_y,402*max_z))
        #     cs = ax.contourf(y*1000,z*1000,gorkov[x0,:,:].T,100, vmin = -2e-8, vmax = 2e-8)
        #     for a in cs.collections:
        #         a.set_edgecolor('face')
        #     plt.xlabel('Y (mm)')
        #     plt.ylabel('Z (mm)')
        #     plt.axis('equal')
        #     plt.xlim((-max_y*1000,max_y*1000))
        #     plt.ylim((-max_z*1000,max_z*1000))
        #     cbar = fig.colorbar(cs)
        #     plt.title("Gor'kov potential Y, Z")
        #     if savefigure & isy & isz:
        #         plt.savefig(path_save+levitator+"_GorkovField_yz_"+phase+fig_type, dpi = 300)
    
        # # ---------------------------------------
        # ##### 2D Gorkov Potential x,z :
        # if i == "xz":
            # fig,ax = plt.subplots(figsize = (500*max_x,402*max_z))
            # cs = ax.contourf(x*1000,z*1000,gorkov[:,y0,:].T,100, vmin = -2e-8, vmax = 2e-8)
            # for a in cs.collections:
            #     a.set_edgecolor('face')
            # plt.xlabel('X (mm)')
            # plt.ylabel('Z (mm)')
            # plt.axis('equal')
            # plt.xlim((-max_x*1000,max_x*1000))
            # plt.ylim((-max_z*1000,max_z*1000))
            # cbar = fig.colorbar(cs)
            # plt.title("Gor'kov potential X, Z")
            # if savefigure & isx & isz:
            #     plt.savefig(path_save+levitator+"_GorkovField_xz_"+phase+fig_type, dpi = 300)
    
        # # ---------------------------------------
        # ##### 2D Gorkov Potential x,y :
        # if i == "xy":
        #     fig,ax = plt.subplots(figsize = (500*max_x,402*max_y))
        #     cs = ax.contourf(x*1000,y*1000,gorkov[:,:,z0].T,100, vmin = -2e-8, vmax = 2e-8)
        #     for a in cs.collections:
        #         a.set_edgecolor('face')
        #     plt.xlabel('X (mm)')
        #     plt.ylabel('Y (mm)')
        #     plt.axis('equal')
        #     plt.xlim((-max_x*1000,max_x*1000))
        #     plt.ylim((-max_y*1000,max_y*1000))
        #     cbar = fig.colorbar(cs)
        #     plt.title("Gor'kov potential X, Y")
        #     if savefigure & isx & isy:
        #         plt.savefig(path_save+levitator+"_GorkovField_xy_"+phase+fig_type, dpi = 300)
    
        # ------------------------------------------------
        #### Pressure z axis :
        if i == "z":
            # mod_mk3_Pz=pressure_z
            plt.figure()
            plt.plot(z*1000,pressure_z) #, label='Original'
            # plt.plot(z*1000,mod_mk3_Pz, label='Modified')
            plt.title('Calculated pressure along z axis')
            plt.xlabel('z (mm)')
            plt.ylabel('P (Pa)')
            # plt.ylim(0, 1650)
            plt.xlim(-max_z*1000,max_z*1000)
            # plt.legend(frameon=False)
            plt.ylim(0,1650)
            if savefigure & isz:
                plt.savefig(path_save+levitator+"_Pressure_z_"+phase+fig_type, dpi = 300)
    
        # ------------------------------------------------
        #### Force z axis :
        if i == "z":
            plt.figure()
            plt.plot(z[1:]*1000,-np.diff(pressure_z)/dz)
            plt.title('Force density along z axis')
            plt.xlabel('z (mm)')
            plt.ylabel('Fz (N/mm3)')
            plt.xlim(-max_z*1000,max_z*1000)
            #plt.ylim(-1e6,1e6)
            if savefigure & isz:
                plt.savefig(path_save+levitator+"_Force_z_"+phase+fig_type, dpi = 300)
    
        # ------------------------------------------------
        #### Pressure y axis :
        if i == "y":
            # mod_mk3_Py=pressure_y
            plt.figure()
            plt.plot(y*1000,pressure_y)  #, label='Original'
            # plt.plot(y*1000,mod_mk3_Py, label='Modified')
            plt.title('Calculated Pressure along y axis')
            plt.xlabel('y (mm)')
            plt.ylabel('P (Pa)')
            # plt.legend(frameon=False)
            plt.ylim(0, 4e-13)
            plt.xlim(-max_y*1000,max_y*1000)
            if savefigure & isy:
                plt.savefig(path_save+levitator+"_Pressure_y_"+phase+fig_type, dpi = 300)
    
        # ------------------------------------------------
        #### Force y axis :
        if i == "y":
            plt.figure()
            plt.plot(y[1:]*1000,-np.diff(pressure_y)/dy)
            plt.title('Force density along y axis')
            plt.xlabel('y (mm)')
            plt.ylabel('Fy (N/mm3)')
            plt.xlim(-max_y*1000,max_y*1000)
            if savefigure & isy:
                plt.savefig(path_save+levitator+"_Force_y_"+phase+fig_type, dpi = 300)
    
        # ------------------------------------------------
        #### Pressure x axis :
        if i == "x":
            # mod_mk3_Px=pressure_x
            plt.figure()
            plt.plot(x*1000,pressure_x)  #, label='Original'
            # plt.plot(x*1000,mod_mk3_Px, label='Modified')
            plt.title('Calculated pressure along x axis')
            plt.xlabel('x (mm)')
            plt.ylabel('P (Pa)')
            plt.ylim(0, 235)
            plt.xlim(-max_x*1000,max_x*1000)

            # plt.legend(frameon=False)
            if savefigure & isx:
                plt.savefig(path_save+levitator+"_Pressure_x_"+phase+fig_type, dpi = 300)
    
        # ------------------------------------------------
        ### Force x axis :
            if i == "x":
                plt.figure()
                plt.plot(x[1:]*1000,-np.diff(pressure_x)/dx)
                plt.title('Force density along x axis')
                plt.xlabel('x (mm)')
                plt.ylabel('Fx (N/mm3)')
                plt.xlim(-max_x*1000,max_x*1000)
                if savefigure & isx:
                    plt.savefig(path_save+levitator+"_Force_x_"+phase+fig_type, dpi = 300)



# ------------------------------------------------
### MultiPlot Pressure Force along axis :

fig, axs = plt.subplots(3, 2,  dpi = 300)
# fig.suptitle('Calculated Pressure and Force field along z, y and x axis')
axs[0,0].plot(z*1000, pressure[x0,y0,:])
# axs[0,0].set_title('Vertical Pressure (z) for x,y = 0')
axs[0,0].set_xlabel('z (mm)')
axs[0,0].set_ylabel('Pressure (Pa)')
#axs[0].legend(fontsize = 'x-small')
axs[0,0].set_xlim(-max_z*1000,max_z*1000)

axs[0,1].plot(z*1000,-np.gradient(pressure_z))
# axs[0,1].set_title('Vertical Force (z) for x,y = 0')
axs[0,1].set_xlabel('z (mm)')
axs[0,1].set_ylabel('Force density (N/mm3)')
#axs[1].legend(fontsize = 'x-small')
axs[0,1].set_xlim(-max_z*1000,max_z*1000)

axs[1,0].plot(y*1000,pressure[x0,:,z0])
#axs[1,0].set_title('Lateral Pressure (y) for z = node')
axs[1,0].set_xlabel('y (mm)')
axs[1,0].set_ylabel('Pressure (Pa)')
#axs[2].legend(fontsize = 'x-small')
axs[1,0].set_xlim(-max_y*1000,max_y*1000)

axs[1,1].plot(y*1000,-np.gradient(pressure_y))
#axs[1,1].set_title('Lateral Force (y) for z = node')
axs[1,1].set_xlabel('y (mm)')
axs[1,1].set_ylabel('Force density (N/mm3)')
#axs[3].legend(fontsize = 'x-small')
axs[1,1].set_xlim(-max_y*1000, max_y*1000)

axs[2,0].plot(x*1000,pressure[:,y0,z0])
#axs[2,0].set_title('Lateral Pressure (x) for z = node')
axs[2,0].set_xlabel('x (mm)')
axs[2,0].set_ylabel('Pressure (Pa)')
#axs[4].legend(fontsize = 'x-small')
axs[2,0].set_xlim(-max_x*1000, max_x*1000)

axs[2,1].plot(x*1000,-np.gradient(pressure_x))
#axs[2,1].set_title('Lateral Force (x) for z = node')
axs[2,1].set_xlabel('x (mm)')
axs[2,1].set_ylabel('Force density (N/mm3)')
#axs[5].legend(fontsize = 'x-small')
axs[2,1].set_xlim(-max_x*1000, max_x*1000)
plt.tight_layout()
if savefigure == True:
    plt.savefig(levitator+"_Multiplot_"+phase+fig_type, dpi = 300)
