import streamlit as st
from src.lib_functions import *
from stl import mesh
import plotly.graph_objects as go

def MicroLev_Cap():
    st.title('Two Halves MicroLev')
    st.header("3D printed case :")
    st.warning("This model only provides the 2 caps, top and bottom, without any other part to link them, it is recommended to use the scad file and edit it according to your own needs !")
    with open('biblio/scad/MagLevCap.scad', 'rb') as f:
        st.download_button(label = "Download MagLevCap SCAD", data = f,file_name = "MagLevCap.scad")    

    st.write("You will find here the STL File of the MicroLev and the preview : ")
    with open('biblio/stl/MicroLev/MagLevCap.zip', 'rb') as f:
        st.download_button(label = "Download MagLevCap STL", data = f,file_name = "MagLevCap.zip")
    
    mesh = mesh.Mesh.from_file('biblio/stl/MicroLev/MagLevCap.stl')
    st.plotly_chart(stlmeshplot(mesh),width=400)

