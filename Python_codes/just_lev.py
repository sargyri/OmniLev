import streamlit as st
import pandas as pd
import numpy as np
import src.settings as settings
from math import sin, asin, pi, cos
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from PIL import Image
import os
from stl import mesh
import base64
from src.lib_scad import *
from src.lib_functions import *
import json


# def get_binary_file_downloader_html(bin_file,name, file_label='File'):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     bin_str = base64.b64encode(data).decode()
#     href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{name}">Download {file_label}</a>'
#     return href

st.beta_set_page_config(page_title="Just Lev", page_icon="🧊", layout="wide",initial_sidebar_state="auto")
path = os.getcwd()

st.sidebar.image(Image.open('misc/logo2.jpg'), use_column_width=True)

col1, col2, col3 = st.beta_columns(3)
with col2:
    st.title('Build your own levitator !')

name = st.sidebar.text_input('Name your levitator !', value='default_lev', max_chars=None, key=None, type='default')
resolution = st.sidebar.selectbox("Resolution", ['Very Fast', 'Fast', 'Medium', 'High', 'To Print'], index = 3)
if resolution == 'Very Fast':
    fn = 16
elif resolution == 'Fast':
    fn = 32
elif resolution == 'Medium':
    fn = 64
elif resolution == 'High':
    fn = 96
elif resolution == 'To Print':
    fn = 128
    
fudge = st.sidebar.slider('Fudge', min_value = 0., max_value = 1., value = settings.fudge)

models = pd.DataFrame(columns = ['Model', 'Frequency (kHz)', 'Diameter (mm)', 'Height (mm)', 'Directivity', 'SPL (dB)', 'Leg Space (mm)','Leg Diameter (mm)', 'Leg Height (mm)'])  
models.loc[0] = ['Murata MA40S4S', 40, 10, 7,'','',5.1,1.3,10]
models.loc[1] = ['Manorshi A1640H10T', 40, 16, 10,'','',9.1,2,8.6]
models.set_index('Model', inplace=True)

st.sidebar.header('Transducer Parameter')

expl = st.beta_expander("How to set the parameters ?")
with expl:
    "Work in progress / Schematics to be added to explain each parameter"
    
    st.subheader('Resolution')
    "The resolution is the paramater used to define the number of triangles fitting fot the 3D model built. The lowest resolutions allows a shorter time for stl generation, but can't really be used to print"
    
    st.subheader('Fudge (mm)')
    "The Fudge is a parameter that can be used to smooth the potential defects or errors of the 3D printer. This distance in millimeters is added to most of the shapes used in the 3D file to better adjust to the desired shaped once printed."
    
    st.subheader('Transducer Number')
    "Transducer Number is the number of transducer on the inner circle. The position of this inner circle and all other raws of transducers are determined through this number."
    "Here are some examples :"
    st.image([Image.open('misc/Example4.png'), Image.open('misc/Example6.png'),Image.open('misc/Example10.png')],caption = ['Using 4 as Transducer Number', 'Using 6 as Transducer Number','Using 10 as Transducer Number'], width = 450)
    
    st.subheader('Transducer Model')
    "Transducer Model is the model of transducer you want to use in your levitator. Some standard transducers are already implemented (see list below) but you can use customs ones by entering their specifications."
    "Standard Transducer Models : "
    st.image([Image.open('misc/muratama40s4s.png'), Image.open('misc/MSO-A1640H10T.png')],caption = ["Murata MA40S4S","Manorshi A1640H10T"], width = 450)  
    st.write('Constructor Specifications :')
    st.dataframe(models)
    
    st.subheader('Minimal Space between transducer (mm)')
    "This value is set to ensure the transducers do not touch each other when their positions are calculated."
    
    st.subheader('Thickness (mm)')
    "It is the thickness of the printed part of sphere."

    st.subheader('Well Depth (mm)')
    "Well depth is the depth of the holes where the transducer will be placed"
    
    st.subheader('Diameter (mm)')
    st.image(Image.open('misc/diameter.png'), width = 600)
    "Diameter is the diameter of the outer sphere of the levitator. It can also be seen as the height of the levitator. It defines the curvature of the levitator. It is to be set along with "
    "Note : For better trapping forces, the diameter should be set so that the distance between two opposite transducer is a mupliple of half the sound wavelength. The checking box 'Diameter = n*λ/2*' constrain the diameter parameter to specific values which satisfy this condition"
    
    st.subheader('Width (mm) and end angle (degrees)')
    "Width is the width of the levitator (or the diameter of a cylinder that can contains the levitator). The maximum width is the diameter previously defined, since the overall shape is meant to be spherical."
    "The end angle is the angle formed between the vertical axis and the intersection of the outer sphere with a cylinder of diameter width"
    st.image(Image.open('misc/end_angle.png'), width = 700)
    
    st.subheader('Pillar Size')
    "The width of the support pillar (which should connect the two sides of the levitator)"
    
    st.subheader('Hole')
    "Check this box if you want a hole at the bottom (and/or top of the levitator). The size of the hole is calculated with the parameters and not set manually"
    
    st.subheader('Support')
    "Check this box if you want a support. The support is a cylinder added below the spherical cap to hold the levitator."    
    
transducer_number = st.sidebar.slider('Transducer Number : ',min_value = 2, max_value = 30, value = settings.transducer_number) 

transducer = st.sidebar.selectbox("Transducer Model", ['Murata MA40S4S', 'Manorshi A1640H10T', 'Custom'], index = 2)
if transducer != 'Custom':
    transducer_diameter = models.loc[transducer]['Diameter (mm)']
    transducer_height = models.loc[transducer]['Height (mm)']
    leg_space = models.loc[transducer]['Leg Space (mm)']    
    leg_diameter = models.loc[transducer]['Leg Diameter (mm)'] 
    leg_height = models.loc[transducer]['Leg Height (mm)']
    frequency = 1000*models.loc[transducer]['Frequency (kHz)']

if transducer == 'Custom':
    with st.sidebar.beta_expander('Custom Parameters'):
        "Diameter is the diameter of the head of the transducer"
        "Height is the height of the cap of the transducer"
        "Space betwee two legs is the distance between the two pins (from center to center)"
        "Diameter of a leg is the diametr of the pins"
        "Length of a leg is the length of the pins"
    
    transducer_diameter = st.sidebar.slider('Diameter of transducer (mm)', min_value = 0, max_value = 30, value = settings.transducer_diameter)
    transducer_height = st.sidebar.slider('Height of transducer (mm)', min_value = 0, max_value = 15, value = settings.transducer_height)      
    leg_space = st.sidebar.slider('Space between the two legs (mm)', min_value = 0., max_value = 10., value = settings.leg_space)      
    leg_diameter = st.sidebar.slider('Diameter of a leg (mm)', min_value = 0., max_value = 4., value = settings.leg_diameter)      
    leg_height = st.sidebar.slider('Length of a leg (mm)', min_value = 0, max_value = 20, value = settings.leg_height)
    frequency = st.sidebar.slider('Frequency (kHz)', min_value = 20, max_value = 100, value = 40)

    
transducer_gap = st.sidebar.slider('Minimal wanted space between each transducer', min_value = 0., max_value = 3., value = settings.transducer_gap)

st.sidebar.subheader('Case and Shape Parameters')
thickness = st.sidebar.slider('Thickness', min_value = 0.5, max_value = 10., value = settings.thickness, step = 0.1)      #Tickness of the case
well = st.sidebar.slider('Well depth', min_value = 0., max_value = thickness, value = settings.well) 

if st.sidebar.checkbox('Diameter = n*λ/2 ?', value = True):
    l = 340/frequency
    diameter = st.sidebar.slider('Diameter', min_value = 2*(thickness - well + transducer_height), max_value = 300., value = thickness - well + transducer_height + 9*l, step = l/2)
else:
    diameter = st.sidebar.slider('Diameter', min_value = 0, max_value = 300, value = settings.diameter, key = 'diam')
    
option = st.sidebar.selectbox("What do you want to set ?", ['Set Width', 'Set Angle'])
if option == 'Set Angle':
    end_angle = st.sidebar.slider('Angle', min_value = 0, max_value = 90, value = settings.end_angle)
    width = diameter*sin(end_angle*pi/180)
    st.sidebar.text('max width is '+str(round(width,1))+' mm.')
elif option =='Set Width':
    width = st.sidebar.slider('Width', min_value = round(diameter/2), max_value = round(diameter), value = round(0.75*diameter))
    end_angle = asin(width / diameter)*180/pi
    st.sidebar.write('Max angle is '+str(round(end_angle,1))+' degrees.')

pillar_size = st.sidebar.slider('Pillar Size', min_value = 0, max_value = round(diameter), value = settings.pillar_size)    # Desired width of the two pillars

if st.sidebar.checkbox('Support ?', value = False):
    support = True
    st.sidebar.text('Minimum support height is '+str(round(0.5*diameter*(1-cos(end_angle*pi/180)),1))+' mm.')
    support_height = st.sidebar.slider('Support Height', min_value = 0, max_value = round(diameter), value = settings.support_height)
    support_thickness = st.sidebar.slider('Support Thickness', min_value = 0., max_value = 4., value = settings.support_thickness)
else:
    support = False
    support_height=0
    support_thickness=0

if st.sidebar.checkbox('Hole ?', value = True):
    hole = True
else:
    hole = False

settings = {
    "name" : name,
    "fn" : fn,
    "fudge" : fudge,
    "diameter": diameter,
    "width": width,
    "end_angle" : end_angle,
    "thickness" : thickness,
    "pillar_size" : pillar_size,
    "well" : well,
    "support" : support,
    "support_height" :support_height,
    "support_thickness" : support_thickness,
    "hole" : hole,
    "transducer_number" :transducer_number,
    "transducer_diameter" : transducer_diameter,
    "transducer_height": transducer_height,
    "leg_space" : leg_space,
    "leg_diameter": leg_diameter,
    "leg_height": leg_height,
    "transducer_gap": transducer_gap,
}

library_settings = {
    "fn" : fn,
    "fudge" : fudge,
    "diameter": diameter,
    "width": width,
    "end_angle" : end_angle,
    "thickness" : thickness,
    "pillar_size" : pillar_size,
    "well" : well,
    "support" : support,
    "support_height" :support_height,
    "support_thickness" : support_thickness,
    "hole" : hole,
    "transducer_number" :transducer_number,
    "transducer_diameter" : transducer_diameter,
    "transducer_height": transducer_height,
    "leg_space" : leg_space,
    "leg_diameter": leg_diameter,
    "leg_height": leg_height,
    "transducer_gap": transducer_gap,
}


calc = st.beta_expander('Preview and simulation')

# buildscad = st.beta_expander('Build')

with calc:
    col1, col2 = st.beta_columns(2)
    with col1:
        scad_file = build(settings)
        os.system("openscad -o preview.png "+scad_file)
        st.subheader('Scad Preview')
        st.markdown(get_binary_file_downloader_html(scad_file, settings['name']+'.scad', 'Your Scad File'), unsafe_allow_html=True)
        st.image([Image.open('preview.png')], width = 600)
    
    with col2:
        st.subheader("Simulation")
        phase_diff = st.slider('Phase difference', min_value = -1., max_value = 1., value = 0.)
        st.pyplot(simulation(settings, phase_diff), dpi = 300) 

    # df = pd.DataFrame(np.array([z, pressure]).T, columns=('z', 'Pressure'))
    # fig = px.scatter(df, x='z',y='Pressure')
    # array.visualize.append(('pressure', {'resolution': 60}))
    # array.visualize.append('Velocity')
    # fig2 = array.visualize(amps)
    # # st.plotly_chart(fig)
    # st.plotly_chart(fig2)

    # diagram = ForceDiagram(array)
    # radii = [1e-3, 2e-3, 4e-3, 8e-3, 16e-3]
    # for radius in radii:
    #     diagram.append([pos, {'radius': radius, 'name': '{} mm'.format(radius * 1e3)}])
    # st.plotly_chart(diagram(amps))

# with buildscad:
#     scad_file = build(settings)
#     os.system("openscad -o preview.png "+scad_file)
#     'Preview :'
    
#     st.image([Image.open('preview.png')], width = 600)
    
#     st.markdown(get_binary_file_downloader_html(scad_file, settings['name']+'.scad', 'Your Scad File'), unsafe_allow_html=True)

# with st.beta_expander('Build a Scad File'):
#     scad_file = build(settings)
#     os.system("openscad -o preview.png "+scad_file)
#     'Preview :'
    
#     st.image([Image.open('preview.png')],width = 600)
    
if st.button('Build a stl File'):
        
    with open('build/library.json') as file:
        library = json.load(file)
        
        if library_settings in library["levitators"]:
            index = library["levitators"].index(library_settings)
            'Retrieving stl from database ...'
            lev_index = "levitator_"+str(index)
        
        else:
            'Building a brand new levitator. . .'
            scad_path = build(settings)
            temp = library["levitators"]
            index = len(temp)
            lev_index = "levitator_"+str(index)
            temp.append(library_settings) 
            os.system("openscad -o build/stl/"+lev_index+".stl "+scad_path)
            with open('build/library.json', 'w') as file:
                json.dump(library, file, indent = 4)
            with open('build/settings'+lev_index+'.txt', 'w') as f:
               print(library_settings, file=f)
               'Done !'
            
    st.markdown(get_binary_file_downloader_html("build/stl/"+lev_index+'.stl', settings['name']+'.stl', 'Picture'), unsafe_allow_html=True)
    
    mesh = mesh.Mesh.from_file("build/stl/"+lev_index+'.stl')    
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
            "ambient": 0.1, 
            "diffuse": 1, 
            "fresnel": 0.1, 
            "specular": 0.7, 
            "roughness": 0.1, 
            "facenormalsepsilon": 1e-06, 
            "vertexnormalsepsilon": 1e-12
          },
        "showscale": False, 
        "colorscale": [
            [0.0, "rgb(161, 218, 180)"], [0.25, "rgb(65, 182, 196)"], [0.5, "rgb(44, 127, 184)"], [0.75, "rgb(8, 104, 172)"], [1, "rgb(37, 52, 148)"]], 
        "flatshading": False,
        "intensity" : z[0],
        "reversescale": True, 
        "lightposition": {
            "x": 0, 
            "y": 0, 
            "z": 100,
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
            "x": 1.15, 
            "y": 1.15, 
            "z": 1.15
          }}, 
        "aspectratio": {
          "x": 1, 
          "y": 1, 
          "z": 0.5,
        }
      }, 
      "title": "Your Levitator :", 
      "width": 900, 
      "height": 800
    }
    fig = go.Figure(data=[go.Mesh3d(trace1)], layout = layout)
    st.plotly_chart(fig)

        
