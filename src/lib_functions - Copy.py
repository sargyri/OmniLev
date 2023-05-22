# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 15:44:23 2020

@author: NicolasPaillet
"""

import numpy as np
import levitate
import base64
import sys
from importlib import import_module  
source=str('/content/scr/') 
sys.path.insert(0, source)

from matplotlib import pyplot as plt

from stl import mesh
import numpy as np
import plotly.graph_objects as go
coordinates = import_module("coordinates")
lib_scad = import_module("lib_scad")

from lib_scad import *
import streamlit as st

def modelisation(levitator, plot, phase_diff):
    p0 = 1
    if type(levitator) is str:
        coord = coordinates.lev(levitator) / 1000
    elif type(levitator) is dict:
        coord = calc_pos(levitator)
    
    normal = -1*coord / np.linalg.norm(coord, 2, axis=1, keepdims = 1)

    if plot == 'Pressure XY' or plot == 'Gorkov XY':
        meshsize = [50,50,2]
    elif plot == 'Pressure YZ' or plot == 'Gorkov YZ':
        meshsize = [2,50,50]
    elif plot == 'Pressure XZ' or plot == 'Gorkov XZ':
        meshsize = [50,2,50]
    elif plot == 'Pressure X':
        meshsize = [250,2,2]
    elif plot == 'Pressure Y':
        meshsize = [2,250,2]
    elif plot == 'Pressure Z':
        meshsize = [2,2,250]
    
    phases_down = 0.5*np.pi*np.ones((1,len(coord)//2))
    phases_up = (0.5+phase_diff)*np.pi*np.ones((1,len(coord)//2))

    coord = coord.T
    normal = normal.T
    
    # -----------------------------------------
    #### Mesh struture :

    max_x = max(abs(coord[0,:]))-0.002
    max_y = max(abs(coord[1,:]))-0.002
    max_z = min(abs(coord[2,:]))-0.002
    x = np.append(np.linspace(-max_x, 0, meshsize[0],endpoint = False),np.linspace(0,max_x,meshsize[0]+1))
    y = np.append(np.linspace(-max_y, 0, meshsize[1],endpoint = False),np.linspace(0,max_y,meshsize[1]+1))
    z = np.append(np.linspace(-max_z, 0, meshsize[2],endpoint = False),np.linspace(0,max_z,meshsize[2]+1))
    dx = x[1]-x[0]
    dy = y[1]-y[0]
    dz = z[1]-z[0]
    x0 = np.where(x==0)[0][0]
    y0 = np.where(y==0)[0][0]
    z0 = np.where(z==0)[0][0]
    points = np.reshape(np.meshgrid(x, y, z, indexing = 'ij'), (3, -1))

    # ----------------------------------------
    ##### Transducer array :    

    phases = np.append(phases_down,phases_up)
    complex_phase = levitate.utils.complex(phases)
    transducer = levitate.transducers.CircularRing(effective_radius=3e-3, p0=p0)    
    array = levitate.arrays.TransducerArray(coord, normal, transducer=transducer, transducer_size=0.01)

    # ----------------------------------------
    ##### Levitate calculation :

    pressure_calculation_instance = levitate.fields.Pressure(array) @ points
    pressure = abs(pressure_calculation_instance(complex_phase))

    gorkov_calc = levitate.fields.GorkovPotential(array,radius = 1e-3) @ points
    #gorkov_grad_calc = levitate.fields.GorkovGradient(array,radius = 1e-3) @ points
    gorkov = gorkov_calc(complex_phase)
    gorkov = gorkov.reshape(len(x),len(y),len(z))
    # gorkov_grad = gorkov_grad_calc(complex_phase)
    # F = -gorkov_grad.reshape(3,len(x),len(y),len(z))
    pressure = pressure.reshape(len(x),len(y),len(z))
    pressure_z = pressure[x0,y0,:]
    pressure_y = pressure[x0,:,z0]
    pressure_x = pressure[:,y0,z0]

    # ----------------------------------------
    ##### Plots :
    
    # --------------------------
    ##### 2d Pressure Map Y, Z :
    if plot == 'Pressure YZ':
        fig,ax = plt.subplots(figsize = (500*max_y,402*max_z))
        cs = ax.contourf(y*1000,z*1000,pressure[x0,:,:].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlim((-max_y*1000,max_y*1000))
        plt.ylim((-max_z*1000,max_z*1000))
        plt.xlabel('Y (mm)')
        plt.ylabel('Z (mm)')
        plt.axis('equal')
        bar = fig.colorbar(cs)
        plt.title("Theoretical Pressure Field Y, Z")

    # -------------------------------------
    ##### 2d Pressure Map X, Z :
    elif plot == 'Pressure XZ':
        fig,ax = plt.subplots(figsize = (500*max_y,402*max_z))
        cs = ax.contourf(x*1000,z*1000,pressure[:,y0,:].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlim((-max_x*1000,max_x*1000))
        plt.ylim((-max_z*1000,max_z*1000))
        plt.xlabel('X (mm)')
        plt.ylabel('Z (mm)')
        plt.axis('equal')
        bar = fig.colorbar(cs)
        plt.title("Theoretical Pressure Field X, Z")

    # --------------------------------------
    ##### 2d Pressure Map X, Y :
    elif plot == 'Pressure XY':
        fig,ax = plt.subplots(figsize = (500*max_x,402*max_y))
        cs = ax.contourf(x*1000,y*1000,pressure[:,:,z0].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlim((-max_x*1000,max_x*1000))
        plt.ylim((-max_y*1000,max_y*1000))
        plt.xlabel('X (mm)')
        plt.ylabel('Y (mm)')
        plt.axis('equal')
        bar = fig.colorbar(cs)
        plt.title("Theoretical Pressure Field X, Y")

    # ---------------------------------------
    ##### 2D Gorkov Potential y,z :
    elif plot == 'Gorkov YZ':
        fig,ax = plt.subplots(figsize = (500*max_y,402*max_z))
        cs = ax.contourf(y*1000,z*1000,gorkov[x0,:,:].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlabel('Y (mm)')
        plt.ylabel('Z (mm)')
        plt.axis('equal')
        plt.xlim((-max_y*1000,max_y*1000))
        plt.ylim((-max_z*1000,max_z*1000))
        cbar = fig.colorbar(cs)
        plt.title("Gor'kov Potential Y, Z")

    # ---------------------------------------
    ##### 2D Gorkov Potential x,z :
    elif plot == 'Gorkov XZ':
        fig,ax = plt.subplots(figsize = (500*max_x,402*max_z))
        cs = ax.contourf(x*1000,z*1000,gorkov[:,y0,:].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlabel('X (mm)')
        plt.ylabel('Z (mm)')
        plt.axis('equal')
        plt.xlim((-max_x*1000,max_x*1000))
        plt.ylim((-max_z*1000,max_z*1000))
        cbar = fig.colorbar(cs)
        plt.title("Gor'kov Potential X, Z")

    # ---------------------------------------
    ##### 2D Gorkov Potential x,y :
    elif plot == 'Gorkov XY':
        fig,ax = plt.subplots(figsize = (500*max_x,500*max_y))
        cs = ax.contourf(x*1000,y*1000,gorkov[:,:,z0].T,100, vmin = -2e-8, vmax = 2e-8)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlabel('X (mm)')
        plt.ylabel('Y (mm)')
        plt.axis('equal')
        plt.xlim((-max_x*1000,max_x*1000))
        plt.ylim((-max_y*1000,max_y*1000))
        cbar = fig.colorbar(cs)
        plt.title("Gor'kov Potential X, Y")

    # ------------------------------------------------
    #### Pressure z axis :
    elif plot == 'Pressure Z':
        fig = plt.figure()
        plt.plot(z*1000,pressure_z)
        plt.title('Calculated Pressure along z axis')
        plt.xlabel('z (mm)')
        plt.ylabel('P (Pa)')
        plt.xlim(-max_z*1000,max_z*1000)
        #plt.ylim(0,1700)


    # ------------------------------------------------
    #### Pressure y axis :
    elif plot == 'Pressure Y':
        fig = plt.figure()
        plt.plot(y*1000,pressure_y)
        plt.title('Calculated Pressure along y axis')
        plt.xlabel('y (mm)')
        plt.ylabel('P (Pa)')
        plt.xlim(-max_y*1000,max_y*1000)

    # ------------------------------------------------
    #### Pressure x axis :
    elif plot == 'Pressure X':
        fig = plt.figure()
        plt.plot(x*1000,pressure_x)
        plt.title('Calculated Pressure along x axis')
        plt.xlabel('x (mm)')
        plt.ylabel('P (Pa)')
        plt.xlim(-max_x*1000,max_x*1000)

    return (fig)

def stlmeshplot(mesh):   
    x = mesh.x.reshape(1,3*len(mesh.x)).tolist()
    y = mesh.y.reshape(1,3*len(mesh.y)).tolist()
    z = mesh.z.reshape(1,3*len(mesh.z)).tolist()
    i = np.linspace(0, 3*len(mesh.x),len(mesh.x), endpoint = False, dtype = int)
    j = i + 1
    k = j + 1
    i = i.tolist()
    j = j.tolist()
    k = k.tolist()    

    trace1 = {
        "i": i,
        "j": j,
        "k": k,
        "name": "", 
        "type": "mesh3d",
        "x" : x[0],
        "y" : y[0],
        "z" : z[0],
        "lighting": {
            "ambient": 0, 
            "diffuse": 0.6, 
            "fresnel": 0.1, 
            "specular": 0.7, 
            "roughness": 0.1, 
            "facenormalsepsilon": 1e-06, 
            "vertexnormalsepsilon": 1e-12
        },
        "showscale": False, 
        "colorscale": [
            [0, "rgb(5, 5, 5)"], [1, "rgb(250, 250, 250)"]],#, [0.5, "rgb(44, 127, 184)"], [0.75, "rgb(8, 104, 172)"], [1, "rgb(37, 52, 148)"]], 
        "flatshading": False,
        "intensity" : [0,1],
        "reversescale": True, 
        "lightposition": {
            "x": 0, 
            "y": 0, 
            "z": 10,
        }       
        }
    # data=pgo.Data([trace1])
    layout = {
    "font": {
        "size": 12, 
        "color": "black"
    }, 
    "scene": {
        "xaxis": {
            "visible" : False,
        }, 
        "yaxis": {
            "visible" : False,
        }, 
        "zaxis": {
            "visible" : False,
        }, 
        "camera": {"eye": {
            "x": 1, 
            "y": 1,
            "z": 1
        }},
        "aspectmode":'data'
    }, 
    "title": "Your Levitator :",
    "height":900,
    "width":900,
    "margin": {
        "r":0, 
        "l":0, 
        "b":0, 
        "t":0,
        },
    }
    fig = go.Figure(data=[go.Mesh3d(trace1)], layout = layout)
    return(fig)
