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
from src.models import *
import json
import time
import re

if 'levtype' not in st.session_state:
    st.session_state.levtype = 'none'

if 'isbuilt' not in st.session_state:
    st.session_state.isbuilt = False

def lev_type(levname):
    st.session_state.levtype = levname

def electronics():
    with st.container():
        st.header("Electronics :")
        st.subheader("Polarity determination :")
        st.write("To create a resonant sound cavity, and thus building a stable levitator, one of the most important things is to know the relative polarity of each transducer you will use.")
        st.write("As transducers are usually not marked regarding the polarity of the pins, you will need to determine this manually.")
        st.write("This 3D print part can help you to do so. It consists of two areas for 2 transducers separated by exactly an integer number of sound wavelength at 40kHz.")
        with open('biblio/stl/phase.stl', 'rb') as f:
                st.download_button(label = "Download phase tool", data = f,file_name = "phase.stl")
        st.write("Insert a transducer in the circled emplacement, which will be your reference. Supply it with 40kHz signal, monitored with an oscilloscope.")
        st.write("On the other side, place a transducer and monitor its electrical output on the oscilloscope.")
        st.write("You should see two signals, either in phase (i.e. matching maxima and mimima) or in phase opposition (maxima facing minima).")
        st.write("Choose a convention (Beware that you will have to keep the same for all the transducers) for example : if signals are in phase, mark the pin connected to X wire, and if not mark the other pin.")
        st.write("Then, all the marked pins will have the same polarity.")

def right_column_simulation(levitator):
    with st.form("plots to display"):
        st.header("Designing customized acoustic levitators")
        phase_diff = st.slider('Phase difference', min_value = -1., max_value = 1., value = 0.)
        plot = st.multiselect("Select plots to display", ["Pressure XZ", "Pressure YZ", "Pressure XY",'Gorkov XZ','Gorkov YZ','Gorkov XY', 'Pressure X', 'Pressure Y', 'Pressure Z'])
        submitted = st.form_submit_button("Calculate")
    if submitted:
        for i in plot:
            st.pyplot(modelisation(levitator, i, phase_diff))

def left_column_print(lev_name):
    with st.container():
        st.header("3D scaffold")
        with open('biblio/scad/'+lev_name+'.scad', 'rb') as f:
            st.download_button(label = "Download SCAD file", data = f,file_name = lev_name+'.scad')    
    
        st.write("Here you will find the STL file of the levitator and the preview : ")
        with open('biblio/stl/'+lev_name+'.zip', 'rb') as f:
            st.download_button(label = "Download STL file(s)", data = f,file_name = lev_name+'.zip')
            
        meshstl = mesh.Mesh.from_file('biblio/stl/'+lev_name+'.stl')
        st.plotly_chart(stlmeshplot(meshstl),use_column_width = True)
                  

#------------------------------------------------------------
########## Begin App
#-------------------

st.set_page_config(page_title="OmniLev", page_icon="🧊", layout="wide",initial_sidebar_state="auto")
path = os.getcwd()

st.sidebar.title("OmniLev")
st.sidebar.button('🏠', on_click = lev_type, args=('none',))
st.sidebar.image(Image.open('misc/logo2.jpg'), use_column_width=True)

#--------------------------------------
######## HomePage 
#-------------

if st.session_state.levtype == 'none':
    col1, col2, col3 = st.columns(3)
    with col2:
        st.title('Design and 3D print your own levitator !')

    st.write("This platform provides blueprints and tutorials on fabricating acoustic levitators, using a 3D printer and cost effective electronics. Several models with their own specifications are provided, and a tool to design your own.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header('Mk1')
        st.image([Image.open('misc/Mk1.jpg')],width=400)
        st.subheader('Specifications :')
        st.write("Total diameter : 63mm")
        st.write('Radius of curvature: 28 mm')
        st.write("Total height : 76mm")
        st.write('Cavity length: 52 mm')
        st.write("Number of transducers : 34 (17 + 17)")
        st.write("Size of transducers : 10mm")
        st.write("Operating frequency : 40kHz ")
        st.subheader("Mk1 Models :")
        st.button('3D print levitator Mk1', on_click = lev_type, args=('Levitator_Mk1',))
    
    with col2:
        st.header('Mk2')
        st.image([Image.open('misc/Mk2.jpg')],width=400)
        st.subheader('Specifications :')
        st.write("Total diameter : 42mm")
        st.write('Radius of curvature: 20 mm')
        st.write("Total height : 46mm")
        st.write('Cavity length: 38 mm')
        st.write("Number of transducers : 24 (12 + 12), uncapped")
        st.write("Size of transducers : 10mm")
        st.write("Operating frequency : 40kHz ")
        st.subheader("Mk2 Models :")
        st.button('3D print levitator Mk2', on_click = lev_type, args=('Levitator_Mk2',))

    with col3:
        st.header('Mk3')
        st.image([Image.open('misc/Mk3.jpg')],width=400)
        st.subheader('Specifications :')
        st.write("Total diameter : 50mm")
        st.write('Radius of curvature: 21 mm')
        st.write("Total height : 60mm")
        st.write('Cavity length: 42 mm')
        st.write("Number of transducers : 36 (18 + 18), uncapped, beehive configuration")
        st.write("Size of transducers : 10mm")
        st.write("Operating frequency : 40kHz ")
        st.subheader("Mk3 Models :")
        st.button('3D print levitator Mk3', on_click = lev_type, args=('Levitator_Mk3',))
    
    st.sidebar.header('CustomLev')
    st.sidebar.write("CustomLev is a built-in app that is used for the design of customized levitators.")
    st.sidebar.button('3D print a customlev', on_click = lev_type, args=('Custom',))

#--------------------------------------
######### Models
#------------------

elif st.session_state.levtype == 'Levitator_Mk1':
    st.title('Mk1')
    print3d, simul = st.columns(2)
    with print3d:
        left_column_print(st.session_state.levtype)
        electronics()
    with simul:
        right_column_simulation('mk1')


elif st.session_state.levtype == 'Levitator_Mk2':
    st.title('Mk2')
    print3d, simul = st.columns(2)
    with print3d:
        left_column_print(st.session_state.levtype)
        electronics()
    with simul:
        right_column_simulation('mk2')


elif st.session_state.levtype == 'Levitator_Mk3':
    st.title('Mk3')

    print3d, simul = st.columns(2)
    with print3d:
        left_column_print(st.session_state.levtype)
        electronics()
    with simul:
        right_column_simulation('mk3')


#----------------------------------------------
####### Custom Lev
#-----------------

elif st.session_state.levtype == 'Custom':
    isbuilt = False
    st.title("Custom Levitator")

    expl = st.expander("How to set the parameters ?")
    with expl:
        models = pd.DataFrame(columns = ['Model', 'Frequency (kHz)', 'Diameter (mm)', 'Height (mm)', 'Directivity', 'SPL (dB)', 'Leg Space (mm)','Leg Diameter (mm)', 'Leg Height (mm)'])  
        models.loc[0] = ['Murata MA40S4S', 40, 10, 7,'','',5.1,1.3,10]
        models.loc[1] = ['Manorshi A1640H10T', 40, 16, 10,'','',9.1,2,8.6]
        models.set_index('Model', inplace=True)
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
        "This value is set to ensure the transducers are not in contact with each other when their positions are calculated."
        
        st.subheader('Thickness (mm)')
        "It is the thickness of the printed part of the sphere."

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

    name = st.sidebar.text_input('Name your levitator !', value='default_lev', max_chars=None, key=None, type='default')
    name = re.sub(r"\s+", '_', name)
        
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

    st.sidebar.header('Transducer Parameter')     
        
    transducer_number = st.sidebar.slider('Transducer Number : ',min_value = 2, max_value = 30, value = settings.transducer_number) 

    transducer = st.sidebar.selectbox("Transducer Model", ['Murata MA40S4S', 'Manorshi A1640H10T', 'Custom'], index = 2)
    if transducer != 'Custom':
        transducer_diameter = models.loc[transducer]['Diameter (mm)']
        transducer_height = models.loc[transducer]['Height (mm)']
        leg_space = models.loc[transducer]['Leg Space (mm)']    
        leg_diameter = models.loc[transducer]['Leg Diameter (mm)'] 
        leg_height = models.loc[transducer]['Leg Height (mm)']
        frequency = models.loc[transducer]['Frequency (kHz)']

    if transducer == 'Custom':
        with st.sidebar.expander('Custom Parameters'):
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

        
    transducer_gap = st.sidebar.slider('Minimal space wanted between each transducer', min_value = 0., max_value = 3., value = settings.transducer_gap)

    st.sidebar.subheader('Case and Shape Parameters')
    thickness = st.sidebar.slider('Thickness', min_value = 0.5, max_value = 10., value = settings.thickness, step = 0.1)      #Tickness of the case
    well = st.sidebar.slider('Well depth', min_value = 0., max_value = thickness, value = settings.well) 

    if st.sidebar.checkbox('Diameter = n*λ/2 ?', value = True):
        l = 340/frequency
        diameter = st.sidebar.slider('Diameter', min_value = 2*(thickness - well + transducer_height), max_value = 300., value = thickness - well + transducer_height + 9*l, step = l/2)
    else:
        diameter = st.sidebar.slider('Diameter', min_value = 0, max_value = 300, value = settings.diameter)

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

    if st.button('Create stl file'):
        isbuilt = True
        scad_path = build(settings)
        with st.spinner(text = "Building the levitator"):        
            os.system("openscad -o biblio/stl/"+settings['name']+".stl "+scad_path)
        st.success('Done!')
        time.sleep(1)
        lev_name = settings['name']    
        
        print3d, simul = st.columns(2)
        with print3d:
            with st.container():
                st.header("3D case")
                with open('biblio/scad/'+lev_name+'.scad', 'rb') as f:
                    st.download_button(label = "Download SCAD file", data = f,file_name = lev_name+'.scad')    
            
                st.write("Here you will find the STL file of the levitator and the preview: ")
                with open('biblio/stl/'+lev_name+'.stl', 'rb') as f:
                    st.download_button(label = "Download STL file(s)", data = f,file_name = lev_name+'.stl')
                    
                meshstl = mesh.Mesh.from_file('biblio/stl/'+lev_name+'.stl')
                st.plotly_chart(stlmeshplot(meshstl),use_column_width = True)
            electronics()
        with simul:
            right_column_simulation(settings)

    if isbuilt == False:
        col1, col2 = st.columns(2)
        with col1:
            #scad_file = build(settings)
            scad_file = test_easy(settings)
            # os.system("DISPLAY=:5 openscad -o biblio/preview.png "+scad_file)
            os.system("openscad -o biblio/preview.png "+scad_file)  
            st.subheader('Scad Preview')
            with open(scad_file,'rb') as f:
                st.download_button(label = "Download SCAD file", data = f,file_name = settings['name']+'.scad')
            time.sleep(1)
            st.image(Image.open('biblio/preview.png'), width = 600)
        
        with col2:
            right_column_simulation(settings)

else:
    st.session_state.levtype = 'none'
    st.experimental_rerun()
            


            
