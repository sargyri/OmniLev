import numpy as np
import levitate
import base64
from matplotlib import pyplot as plt
from stl import mesh
import numpy as np
import plotly.graph_objects as go
from src.coordinates import *
from src.lib_scad import *
import streamlit as st
import pandas as pd

p0=3

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


def get_array(separation, levitator, phase_diff):
    
    if type(levitator) is str:
        coordinates = lev(levitator).T / 1000
    elif type(levitator) is dict:
        coordinates = calc_pos(levitator).T
    
    original_distance = np.ptp(coordinates[2])
    normals = -1 * coordinates / np.linalg.norm(coordinates, 2, axis=1, keepdims=True)

    top_idx = np.where(coordinates[2] > 0)
    bottom_idx = np.where(coordinates[2] < 0)

    displacement = separation - original_distance
    coordinates[2, top_idx] += displacement
    coordinates[2, bottom_idx] -= displacement

    transducer = levitate.transducers.CircularRing(effective_radius=3e-3, p0=p0)
    array = levitate.arrays.TransducerArray(coordinates, normals, transducer=transducer)

    state = 0.5*np.pi*np.ones(array.num_transducers, complex)
    state[top_idx] = 1j
    state[bottom_idx] = 1j-(2*phase_diff/np.pi)*1j
    
    
    array.state = state
    return array


def modelisation(levitator, plot, phase_diff):

    if type(levitator) is str:
        coord = lev(levitator) / 1000
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
    else:
        meshsize = [0,0,0]
        
    
    
    Data_model = pd.DataFrame(columns=['cavity_length', 'pressure', 'net_force', 'hor_stiff', 'vert_stiff', 'curl'])
    separations = np.arange(30e-3, 130e-3, 1e-3)
    pressure_Lc = np.zeros((separations.size, 3, 3))
    forces_Lc = np.zeros((separations.size, 1, 3))
    force_gradients_Lc = np.zeros((separations.size, 3, 3))
    net_force_Lc = np.zeros((separations.size))
    
    for idx, separation in enumerate(separations):
        array = get_array(separation, levitator, phase_diff=phase_diff)
        node=-array.wavelength/4*abs(phase_diff)
        df0 = (levitate.fields.RadiationForce(array) @ [0, 0, node])(array.state) #array_inPhaseOpp.waveleng
        df = (levitate.fields.RadiationForceGradient(array) @ [0, 0, node])(array.state) #array_inPhaseOpp.waveleng
        p = (levitate.fields.Pressure(array) @ [0,0,node])(array.state)
        pressure_Lc[idx] = np.abs(p)
        forces_Lc[idx]=df0
        force_gradients_Lc[idx] = df
        net_force_Lc[idx] = np.sqrt(np.array(df0[0])**2+np.array(df0[1])**2+np.array(df0[2])**2)

    vertical_stiffness = np.zeros(separations.size)
    min_horizontal_stiffness = np.zeros(separations.size)
    max_horizontal_stiffness = np.zeros(separations.size)
    curl = np.zeros(separations.size)
    for idx, df in enumerate(force_gradients_Lc):
        e, v = np.linalg.eig(df)
        inverticallity = np.min(np.abs(e - df[2,2]))
        if inverticallity > 0.01 * abs(df[2, 2]):
            print(f'Separation {separations[idx]} has more than 1% inverticallity!')
        e, v = np.linalg.eig(df[:2, :2])
        vertical_stiffness[idx] = -df[2, 2]
        min_horizontal_stiffness[idx] = min(-e)
        max_horizontal_stiffness[idx] = max(-e)
    
        curl_x = df[2, 1] - df[1, 2]  # dFz/dy - dFy/dz
        curl_y = df[0, 2] - df[2, 0]  # dFx/dz - dFz/dx
        curl_z = df[1, 0] - df[0, 1]  # dFy/dx - dFx/dy
        curl[idx] = (curl_x**2 + curl_y**2 + curl_z**2)**0.5
        
        
        Data_model.loc[idx, 'cavity_length']=separations[idx]
        Data_model.loc[idx, 'pressure']=pressure_Lc[idx]
        Data_model.loc[idx, 'net_force']=net_force_Lc[idx]
        Data_model.loc[idx, 'hor_stiff']=max_horizontal_stiffness[idx]
        Data_model.loc[idx, 'vert_stiff']=vertical_stiffness[idx]
        Data_model.loc[idx, 'curl']=curl[idx]
    
    
    if ((plot != 'Curl vs cavity length') and (plot!= 'Trap stiffness vs cavity length') and (plot!= 'Acoustic radiation force vs cavity length')):
        coord = coord.T
        normal = normal.T
        
        # -----------------------------------------
        #### Mesh struture :
    
        max_x = 0.01
        max_y = 0.01
        max_z = 0.015
        x = np.append(np.linspace(-max_x, 0, meshsize[0],endpoint = False),np.linspace(0,max_x,meshsize[0]+1))
        y = np.append(np.linspace(-max_y, 0, meshsize[1],endpoint = False),np.linspace(0,max_y,meshsize[1]+1))
        z = np.append(np.linspace(-max_z, 0, meshsize[2],endpoint = False),np.linspace(0,max_z,meshsize[2]+1))
        # dx = x[1]-x[0]
        # dy = y[1]-y[0]
        # dz = z[1]-z[0]
        points = np.reshape(np.meshgrid(x, y, z, indexing = 'ij'), (3, -1))
    
        # ----------------------------------------
        ##### Levitate calculation :
    
        array = get_array(max(coord[2, :])*2, levitator, phase_diff=phase_diff)
        node=-array.wavelength/4*abs(phase_diff)
        # force_gradients = (levitate.fields.RadiationForceGradient(array) @ points)(array.state) #array_inPhaseOpp.waveleng
        p = (levitate.fields.Pressure(array) @ points)(array.state)
        pressure = np.abs(p)
    
        x0 = find_nearest(x, 0)[1]
        y0 = find_nearest(y, 0)[1]
        z0 = find_nearest(z, node)[1]
        gorkov_calc = levitate.fields.GorkovPotential(array, radius = 1e-3) @ points
        gorkov = gorkov_calc(array.state)
        gorkov = gorkov.reshape(len(x),len(y),len(z))
    
        pressure = pressure.reshape(len(x),len(y),len(z))
        pressure_z = pressure[x0,y0,:] 
        pressure_y = pressure[x0,:,z0]
        pressure_x = pressure[:,y0,z0]

    # ----------------------------------------
    ##### Plots :
    
    # --------------------------
    ##### 2d Pressure Map Y, Z :
    if plot == 'Pressure YZ':
        fig,ax = plt.subplots() #figsize = (500*max_y,402*max_z)
        cs = ax.contourf(y*1000,z*1000,pressure[x0,:,:].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlim((-max_y*1000,max_y*1000))
        plt.ylim((-max_z*1000,max_z*1000))
        plt.xlabel('y (mm)')
        plt.ylabel('z (mm)')
        # plt.axis('equal')
        cbar = fig.colorbar(cs)
        cbar.ax.set_ylabel("Acoustic pressure (Pa)")
        plt.title("Theoretical pressure Field y, z")

    # -------------------------------------
    ##### 2d Pressure Map X, Z :
    elif plot == 'Pressure XZ':
        fig,ax = plt.subplots()
        cs = ax.contourf(x*1000,z*1000,pressure[:,y0,:].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlim((-max_x*1000,max_x*1000))
        plt.ylim((-max_z*1000,max_z*1000))
        plt.xlabel('x (mm)')
        plt.ylabel('z (mm)')
        # plt.axis('equal')
        cbar = fig.colorbar(cs)
        cbar.ax.set_ylabel("Acoustic pressure (Pa)")
        plt.title("Theoretical pressure Field x, z")

    # --------------------------------------
    ##### 2d Pressure Map X, Y :
    elif plot == 'Pressure XY':
        fig,ax = plt.subplots()
        cs = ax.contourf(x*1000,y*1000,pressure[:,:,z0].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlim((-max_x*1000,max_x*1000))
        plt.ylim((-max_y*1000,max_y*1000))
        plt.xlabel('x (mm)')
        plt.ylabel('y (mm)')
        # plt.axis('equal')
        cbar = fig.colorbar(cs)
        cbar.ax.set_ylabel("Acoustic pressure (Pa)")
        plt.title("Theoretical pressure Field x, y")

    # ---------------------------------------
    ##### 2D Gorkov Potential Y, Z :
    elif plot == 'Gorkov YZ':
        fig,ax = plt.subplots()
        cs = ax.contourf(y*1000, z*1000, gorkov[x0,:,:].T, 100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlabel('y (mm)')
        plt.ylabel('z (mm)')
        # plt.axis('equal')
        plt.xlim((-max_y*1000,max_y*1000))
        plt.ylim((-max_z*1000,max_z*1000))
        cbar = fig.colorbar(cs)
        cbar.ax.set_ylabel("Acoustic radiation force (N)")
        plt.title("Gor'kov potential y, z")

    # ---------------------------------------
    ##### 2D Gorkov Potential x, z :
    elif plot == 'Gorkov XZ':
        fig,ax = plt.subplots()
        cs = ax.contourf(x*1000,z*1000,gorkov[:,y0,:].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlabel('x (mm)')
        plt.ylabel('z (mm)')
        # plt.axis('equal')
        plt.xlim(-max_x*1000,max_x*1000)
        plt.ylim(-max_z*1000,max_z*1000)
        cbar = fig.colorbar(cs)
        cbar.ax.set_ylabel("Acoustic radiation force (N)")
        plt.title("Gor'kov potential x, z")

    # ---------------------------------------
    ##### 2D Gorkov Potential x, y :
    elif plot == 'Gorkov XY':
        fig,ax = plt.subplots()
        cs = ax.contourf(x*1000,y*1000,gorkov[:,:,z0].T,100)
        for a in cs.collections:
            a.set_edgecolor('face')
        plt.xlabel('x (mm)')
        plt.ylabel('y (mm)')
        # plt.axis('equal')
        plt.xlim(-max_x*1000,max_x*1000)
        plt.ylim(-max_y*1000,max_y*1000)
        cbar = fig.colorbar(cs)
        cbar.ax.set_ylabel("Acoustic radiation force (N)")
        plt.title("Gor'kov potential x, y")

    # ------------------------------------------------
    #### Pressure z axis :
    elif plot == 'Pressure Z':
        fig = plt.figure()
        plt.plot(z*1000,pressure_z)
        plt.title('Theoretical pressure along the z axis')
        plt.xlabel('z (mm)')
        plt.ylabel('Pressure (Pa)')
        plt.xlim(-max_z*1000,max_z*1000)
        plt.title("Pressure along the Z-axis at acoustic node")


    # ------------------------------------------------
    #### Pressure y axis :
    elif plot == 'Pressure Y':
        fig = plt.figure()
        plt.plot(y*1000,pressure_y)
        plt.title('Theoretical pressure along the y axis')
        plt.xlabel('y (mm)')
        plt.ylabel('Pressure (Pa)')
        plt.xlim(-max_y*1000,max_y*1000)
        plt.title("Pressure along the Y-axis at acoustic node")

    # ------------------------------------------------
    #### Pressure x axis :
    elif plot == 'Pressure X':
        fig = plt.figure()
        plt.plot(x*1000,pressure_x)
        plt.title('Theoretical pressure along the x axis')
        plt.xlabel('x (mm)')
        plt.ylabel('Pressure (Pa)')
        plt.xlim(-max_x*1000,max_x*1000)
        plt.title("Pressure along the X-axis at acoustic node")

    # ------------------------------------------------
    #### Vertical trap stiffness :
    elif plot == 'Trap stiffness vs cavity length':
        fig = plt.figure(figsize=(8,6))
        plt.plot(Data_model.cavity_length*1e3, abs(Data_model.vert_stiff)*1e3, label='Vertically')
        plt.plot(Data_model.cavity_length*1e3, abs(Data_model.hor_stiff)*1e3, label='Horizonrally')
        plt.xlabel('Cavity length (mm)')
        plt.ylabel('Trap stiffness (μN/mm)')
        plt.xlim(min(separations)*1000, max(separations)*1000)
        # plt.ylim(0,)
        plt.legend(frameon=False)
        plt.title("Trap stiffness vs cavity length")

    elif plot == 'Acoustic radiation force vs cavity length':
        fig = plt.figure()
        plt.plot(separations*1e3, Data_model.net_force*10**6)
        plt.xlim(min(separations)*1000, max(separations)*1000)
        plt.ylim(0,)
        plt.legend(frameon=False)
        plt.xlabel('Cavity length (mm)')
        plt.ylabel('Acoustic radiation force (μN)')
        plt.title("Acoustic radiation force vs cavity length")

    elif plot == 'Curl vs cavity length':
        fig = plt.figure()
        plt.plot(separations*1e3, Data_model.curl)
        plt.xlim(min(separations)*1000, max(separations)*1000)
        # plt.ylim(0,)
        plt.legend(frameon=False)
        plt.xlabel('Cavity length (mm)')
        plt.ylabel('Curl (a.u.)')
        plt.title("Curl vs cavity length")

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
