$fn=128;

height_transducer=5.3;
height_transducer_base = 1.2;


freq=40000;
speed_sound=343;
wavelength=speed_sound/freq*1000;

inner_sphere_radius=(wavelength/2)*5;
thickness_under_transducer = 1.5;
spacing = 26;

thickness = thickness_under_transducer + height_transducer_base;
outer_sphere_radius = inner_sphere_radius + height_transducer + thickness_under_transducer;

module transducer_10(){
    rotate([0,0,90])union(){
        
        color("grey"){cylinder(d=10.5,h=5.3);
            translate([0,0,3.6])cylinder(d=8,h=0.7);
            cylinder(d=5,h=3.6);
            translate([0,0,4.3])cylinder(d1=2,d2=6.9,h=1);
        }  
    translate([-2.21,0,-8.3])color("grey")cylinder(d=1.2,h=10);
    translate([2.21,0,-8.3])color("grey")cylinder(d=1.2,h=10);
}
}

module bottom_half(){
difference(){
    sphere(r=outer_sphere_radius);
    translate([0,0,-spacing/2])difference(){cylinder(d=outer_sphere_radius*2, h=outer_sphere_radius*4);
    translate([0,0,0])cylinder(d1=outer_sphere_radius*2,d2=0,h=spacing/2);}
    
    sphere(r=outer_sphere_radius-thickness);
    translate([0,0,-outer_sphere_radius])cylinder(d=4,h=4*thickness);    
    
    for (angle=[0:120:240]){rotate([0,0,angle])rotate([14,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("blue")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle+60])rotate([28,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("green")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle-19])rotate([36.5,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("red")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle+19])rotate([36.5,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("red")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle+60-14])rotate([50,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("grey")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle+60+14])rotate([50,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("grey")transducer_10();}
    }
}

module top_half(){
mirror([0,0,1])rotate([0,0,180])
difference(){
    sphere(r=outer_sphere_radius);
    translate([0,0,-spacing/2])difference(){cylinder(d=outer_sphere_radius*2, h=outer_sphere_radius*4);
    translate([0,0,0])cylinder(d1=outer_sphere_radius*2,d2=0,h=spacing/2);}
    sphere(r=outer_sphere_radius-thickness);
    translate([0,0,-outer_sphere_radius])cylinder(d=4,h=4*thickness);    
    
    for (angle=[0:120:240]){rotate([0,0,angle])rotate([14,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("blue")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle+60])rotate([28,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("green")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle-19])rotate([36.5,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("red")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle+19])rotate([36.5,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("red")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle+60-14])rotate([50,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("grey")transducer_10();}
    
    for (angle=[0:120:240]){rotate([0,0,angle+60+14])rotate([50,0,0])translate([0,0,-(inner_sphere_radius + height_transducer)])color("grey")transducer_10();}
}
}

module top(){
difference(){
    union(){
    top_half();
     intersection(){   
translate([-10,-26,0.25])cube([20,8,spacing/2-0.5]);
         difference(){
            sphere(r=outer_sphere_radius);
           cylinder(r=(outer_sphere_radius-2.9)*0.91,h=60,center=true);}}}
translate([0,-20,6])rotate([90,0,0])cylinder(h=20,d=3.5);
}
}

module bot(){
difference(){
    union(){
        bottom_half();
     intersection(){   
translate([-10,-26,-spacing/2-0.25])cube([20,8,spacing/2-0.5]);
         difference(){
            sphere(r=outer_sphere_radius);
           cylinder(r=(outer_sphere_radius-2.9)*0.91,h=50,center=true);}}}
translate([0,-20,-6])rotate([90,0,0])cylinder(h=20,d=3.75);
}
}


module holder(){
difference(){
    translate([-10,-32,-20])cube([20,4,40]);
    translate([0,-20,6])rotate([90,0,0])cylinder(h=20,d=4.5);
    translate([0,-20,-6])rotate([90,0,0])cylinder(h=20,d=4.5);
//    translate([-2.25,-35,-6])cube([4.5,10,12]);
    }
}

bot();
top();
holder();