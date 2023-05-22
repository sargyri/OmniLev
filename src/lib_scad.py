# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 15:43:06 2020

@author: NicolasPaillet
"""

from solid import *
from solid.utils import *
import numpy as np
from math import cos, atan, sin, pi, asin, acos

def transducer (settings, radius,angle1,angle2) -> OpenSCADObject: # Fonction to create the transducer object
    fudge = settings['fudge']    
    transducer_radius = settings['transducer_diameter'] / 2
    transducer_height = settings['transducer_height']
    leg_radius = settings['leg_diameter'] / 2
    leg_space = settings['leg_space']
    leg_height = settings['leg_height']
    contour_height = 1
    
    obj = color([0.5,0.5,0.5, 0.7])(cylinder(transducer_radius, transducer_height,center = True))
    # obj = color([0.5,0.5,0.5, 0.7])(cylinder(transducer_radius + fudge, transducer_height,center = True) - down(0.5*(transducer_height - contour_height))(cylinder(transducer_radius - 0.4, contour_height, center = True)))

    leg1 = color([0,0,1, 0.5])(cylinder(leg_radius, leg_height, center = True))
    leg2 = color([1,0,0, 0.5])(cylinder(leg_radius, leg_height, center = True))
    legs = right(leg_space/2)(up(- transducer_height/2 - leg_height/2)(leg1))+right(- leg_space/2)(up(- transducer_height/2 - leg_height/2)(leg2))# + color([0,0,0, 0.5])(cylinder(0.1,radius))
    
    obj = obj + legs
    
    obj = rotate([0,angle1,angle2])(up(-radius)(obj))
    return obj

def transducer_hole (settings, radius,angle1,angle2) -> OpenSCADObject: # Fonction to create and place a transducer at spherical (r, theta, phi) coordinates
    fudge = settings['fudge']   
    transducer_radius = settings['transducer_diameter'] / 2
    transducer_height = settings['transducer_height']
    leg_radius = settings['leg_diameter'] / 2
    leg_space = settings['leg_space']
    leg_height = settings['leg_height']
    contour_height = 1
    
    obj = cylinder(transducer_radius, transducer_height,center = True)
    # obj = cylinder(transducer_radius + fudge, transducer_height,center = True) - down(0.5*(transducer_height - contour_height))(cylinder(transducer_radius - 2, contour_height, center = True))
    # color([0.5,0.5,0.5, 0.7])
    leg1 = cylinder(leg_radius, leg_height, center = True)
    leg2 = cylinder(leg_radius, leg_height, center = True)
    legs = right(leg_space/2)(up(- transducer_height/2 - leg_height/2)(leg1))+right(- leg_space/2)(up(- transducer_height/2 - leg_height/2)(leg2))
    
    obj = obj + legs
    
    obj = rotate([0,angle1,angle2])(up(-radius)(obj))
    obj = hole()(obj)
    return obj

def transducer_raw1(settings): # Fonction to determine the position of the transducers on the first row, given the number of desire transducers
    radius = settings['diameter'] / 2
    diameter = settings['transducer_diameter']
    inner_radius = radius - settings['thickness']      # Internal casing size
    well_radius = inner_radius + settings['well']      # Radius from center to the well where transducers will be
    transducer_radius = well_radius - settings['transducer_height']        # Length between the top of the transducers to the center of the device
    minimal_chord = settings['transducer_number']*(diameter + settings['transducer_gap'])
    angle = asin(minimal_chord/(2*pi*transducer_radius))*180/pi
    return [angle, well_radius-settings['transducer_height']/2, transducer_radius]

def transducer_raws(settings, previous_angle, previous_radius): # Fonction to determine the position of the other raws of trandsucer determine from end_angle and the previous angle
    diameter = settings['transducer_diameter']
    minimal_angle = 2*atan(((diameter+settings['transducer_gap'])/2)/previous_radius)*180/pi
    new_angle = previous_angle + minimal_angle
    chord = 2*pi*sin(new_angle*pi/180)*previous_radius
    number = round(chord / (diameter + settings['transducer_gap']))
    return [number, new_angle]

def limit_angle(settings, transducer_radius, end_angle):
    radius = settings['diameter'] / 2
    diameter = settings['transducer_diameter']
    thickness = settings['thickness']
    angle_edge = acos(radius*cos(end_angle)/(radius-thickness))
    minimal_angle = 2*atan(((diameter+settings['transducer_gap'])/2)/transducer_radius)
    transducer_angle = asin(0.5*diameter / (radius - thickness))
    angle = (angle_edge - transducer_angle - minimal_angle)*180/pi
    return angle

def calc_pos(settings):             
    diameter = settings['diameter']
    radius = settings['diameter'] / 2
    end_angle = settings['end_angle']*pi/180
    width = settings['width']
    thickness = settings['thickness']
    support_height = settings['support_height']
    fudge = settings['fudge']
    number = settings['transducer_number']
    
    alpha = acos(radius*cos(end_angle)/(radius-thickness))
    pos = np.empty(shape =[3,0]) 
       
    [angle, pos_radius, transducer_radius] = transducer_raw1(settings)
        
    for i in range(0, number):
        pos = np.append(pos, sph_to_cart(transducer_radius, angle, 360 * i / number), axis = 1)
    
    total_number = number

    while angle < limit_angle(settings, transducer_radius, end_angle):
        [number, angle] = transducer_raws(settings, angle, transducer_radius)
        for i in range(0, number):
            pos = np.append(pos, sph_to_cart(transducer_radius, angle, 360 * i / number), axis = 1)
        total_number = total_number + number
    coord = np.append(pos,-pos, axis = 1)
    return coord.T

def build(settings):    #Fonction to build a scad file
    diameter = settings['diameter']
    radius = settings['diameter'] / 2
    end_angle = settings['end_angle']*pi/180
    width = settings['width']
    thickness = settings['thickness']   
    fudge = settings['fudge']
    number = settings['transducer_number']
    alpha = acos(radius*cos(end_angle)/(radius-thickness))
    pos = np.empty(shape =[3,0])
        
    if settings['support'] == False:
        case = sphere(radius) - sphere(radius - thickness) - up(radius*(1-cos(end_angle)))(cube(radius*2, center= True))
        case = case + down(0.5*radius*cos(end_angle))(cylinder(0.5*width,radius*cos(end_angle),center = True)) - down(0.5*radius*cos(end_angle))(cylinder((radius-thickness)*sin(alpha),radius*cos(end_angle)+fudge,center = True))
        case = case - right(0.5*settings['pillar_size'] + diameter)(cube([2*diameter, 2*diameter, 2*radius*cos(end_angle)], center = True)) - left(0.5*settings['pillar_size'] + diameter)(cube([2*diameter, 2*diameter, 2*radius*cos(end_angle)], center = True))
    
    elif settings['support'] == True:
        support_height = settings['support_height']
        support_thickness = settings['support_thickness']
        if settings['support_height'] < radius*(1-cos(end_angle)):
            case = down(radius-0.5*radius*(1-cos(end_angle)))(cylinder(0.5*width, radius*(1-cos(end_angle)),center = True)) - down(radius-0.5*radius*(1-cos(end_angle)))(cylinder(0.5*width - support_thickness, radius*(1-cos(end_angle)),center = True))
            print('support too small', radius*(1-cos(end_angle)))
        elif settings['support_height'] > radius*(1-cos(end_angle)):
            case = down(radius*cos(end_angle)+0.5*support_height)(cylinder(0.5*width, support_height, center = True)) - down(radius*cos(end_angle)+0.5*support_height)(cylinder(0.5*width - support_thickness, support_height,center = True))
        
        case = case + sphere(radius) - sphere(radius - thickness) - up(radius*(1-cos(end_angle)))(cube(radius*2, center= True))
        case = case + down(0.5*radius*cos(end_angle))(cylinder(0.5*width,radius*cos(end_angle),center = True)) - down(0.5*radius*cos(end_angle))(cylinder((radius-thickness)*sin(alpha),radius*cos(end_angle)+fudge,center = True))
        case = case - right(0.5*settings['pillar_size'] + diameter)(cube([2*diameter, 2*diameter, 2*radius*cos(end_angle)], center = True)) - left(0.5*settings['pillar_size'] + diameter)(cube([2*diameter, 2*diameter, 2*radius*cos(end_angle)], center = True))
            
    [angle, pos_radius, transducer_radius] = transducer_raw1(settings)
    
    if settings['hole'] == True:
        z = (radius - thickness)*cos(angle*pi/180 - atan(settings['transducer_diameter']/(2 * transducer_radius)))
        middle_hole = down(radius - (radius - z )/ 2)(cylinder(z*atan(angle*pi/180 - atan(settings['transducer_diameter']/(2*transducer_radius))), radius - z, center = True))
        case = case - middle_hole
       
    show_tr = case
        
    for i in range(0, number):
        show_tr = show_tr - transducer(settings, pos_radius, angle, 360 * i / number)
        show_tr = show_tr + transducer(settings, pos_radius, angle, 360 * i / number)
        case = case + transducer_hole(settings, pos_radius, angle, 360 * i / number)     
        pos = np.append(pos, sph_to_cart(transducer_radius, angle, 360 * i / number), axis = 1)
    
    total_number = number

    while angle < limit_angle(settings, transducer_radius, end_angle):
        [number, angle] = transducer_raws(settings, angle, transducer_radius)
        for i in range(0, number):
            case = case + transducer_hole(settings, pos_radius, angle, 360 * i / number)
            show_tr = show_tr - transducer(settings, pos_radius, angle, 360 * i / number)
            show_tr = show_tr + transducer(settings, pos_radius, angle, 360 * i / number)
            pos = np.append(pos, sph_to_cart(transducer_radius, angle, 360 * i / number), axis = 1)
        total_number = total_number + number
    header = "$fn="+str(settings['fn'])+";"
    final_scad = scad_render(case, file_header=header)#'$fn = '+str(settings['fn'])+';')
    #final_scad_show = scad_render(show_tr, file_header='$fn = '+str(settings['fn'])+';')
    scad_render_to_file(case, "biblio/scad/"+settings['name']+".scad",  file_header=header)#file_header='$fn = '+str(settings['fn'])+';')
    #scad_render_to_file(show_tr, settings['name']+"_tr.scad", file_header='$fn = '+str(settings['fn'])+';')
    
    return "biblio/scad/"+settings['name']+".scad"

def test_easy(settings):
    radius = settings['diameter'] / 2
    t_diam = settings['transducer_diameter']
    thickness = settings['thickness']
    middle_radius = radius - settings['thickness']      # Internal casing size
    well_radius = middle_radius + settings['well']      # Radius from center to the well where transducers will be
    inner_radius = well_radius - settings['transducer_height']        # Length between the top of the transducers to the center of the device
    minimal_chord = settings['transducer_number']*(settings['transducer_diameter'] + settings['transducer_gap'])
    end_angle = 51 #settings['end_angle']

    angle_edge = acos(radius*cos(end_angle)/(radius-thickness))
    minimal_angle = 2*atan(((t_diam+settings['transducer_gap'])/2)/inner_radius)
    transducer_angle = asin(0.5*t_diam / (radius - thickness))
    limit_angle = (angle_edge - transducer_angle - minimal_angle)*180/pi
    print(limit_angle)


    angle = asin(minimal_chord/(2*pi*inner_radius))*180/pi
    angles = [angle]
    number_transducer = [settings['transducer_number']]
    number_rows = 0
    minimal_angle = 2*atan(((t_diam+settings['transducer_gap'])/2)/inner_radius)*180/pi
    while angle < end_angle:#limit_angle:
        angle = angle + minimal_angle
        angles.append(angle)
        chord = 2*pi*sin(angle*pi/180)*inner_radius
        number = round(chord / (t_diam + settings['transducer_gap']))
        number_transducer.append(number)
        number_rows = number_rows+1
        

    to_write=[
        ["$fn = "+str(settings['fn'])+";\n"],
        ["$fudge = "+str(settings['fudge'])+";\n"],
        ["$inner_radius = "+str(inner_radius)+";\n"],
        ["$thickness = "+str(thickness)+";\n"],
        ["angles = "+str(angles)+";\n"],
        ["$end_angle = "+str(end_angle)+";\n"],
        ["number = "+str(number_transducer)+";\n"],
        ["$row_number = "+str(number_rows)+";\n"],
        ["$transducer_diameter = "+str(10)+";\n"],
        ["$transducer_height = "+str(7)+";\n"],
        ["$transducer_leg_diameter = "+str(1.3)+";\n"],
        ["$transducer_leg_separation_radius = "+str(5.1/2)+";\n"],
        ["$transducer_leg_height = "+str(10)+";\n"],
        ["$transducer_inset = "+str(1)+";\n"],
        ["$middle_radius = "+str(middle_radius)+";\n"],
        ["$outer_radius = "+str(radius)+";\n"],
        ]
    print(to_write)
    header = "//Parameters\n$fn=96;\n//Un autre trucs ici"
    f_settings = open('biblio/scad/settings.scad','r')
    settings = f_settings.readlines()
    scad_file = open('biblio/scad/temp.scad','r')
    lines = scad_file.readlines()
    with open('biblio/scad/custom.scad','w') as out:
        for i in to_write:
            out.write(i[0])
        for j in lines:
            out.write(j)
    scad_file.close()
    f_settings.close()
    return "biblio/scad/custom.scad"


def sph_to_cart(r, angle, theta):
    theta = pi * theta / 180
    phi = pi * angle / 180
    x = r*cos(theta)*sin(phi)*1e-3
    y = - r*sin(theta)*sin(phi)*1e-3
    z = - r*cos(phi)*1e-3   
    return [[x],[y],[z]]
