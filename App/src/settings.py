scad_filename = "lev_to_stl"

# scad_path = "C:\Users\paillet\Desktop\openscad-2019.05"
resolution = 32   #The higher, the more precise the printing is
fudge = 0.2         #Safety parameter to take into account the reliability of the printer

### Casing Type ##############
end_angle = 67      #Limit angle (also determine the number of rows of transducer you can fit in the case)
shape = 'spherical'
### Casing shape ##########################################################
diameter = 80   #External Size of the levitator
width = 65
thickness = 2.      #Tickness of the case
pillar_size = 15    # Desired width of the two pillars
well = 1.       # Depth of the holes for the transducers, must be < thickness

support = False
support_height = 4   #Height of a small support cylinder below the case, set to 0 if unwanted
support_thickness = 1.   #Thickness of this support


### Transducer ##############################################################

transducer_diameter = 10    # Diameter of a transducer
transducer_height = 7       # Height of a transducer
leg_space = 5.1             # Width of the space between the legs
leg_diameter = 1.3          # Diameter of the legs of the transducers
leg_height = 10             #Length of the transducers pins
transducer_number = 6       # The nuber of desired transducer in the inner circle
transducer_gap = 0.5       # Minimal distance between the cap of two transducer of the same row (and for the calculation of any other row)
