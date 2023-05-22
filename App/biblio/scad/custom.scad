$fn = 16;
$fudge = 0.2;
$inner_radius = 34.25;
$thickness = 2.0;
angles = [17.022795765545347, 34.452261515267665, 51.881727264989976];
$end_angle = 51;
number = [6, 12, 16];
$row_number = 2;
$transducer_diameter = 10;
$transducer_height = 7;
$transducer_leg_diameter = 1.3;
$transducer_leg_separation_radius = 2.55;
$transducer_leg_height = 10;
$transducer_inset = 1;
$middle_radius = 40.25;
$outer_radius = 42.25;
module transducer() rotate([0,0,90]){
  cylinder(d=$transducer_diameter,h=$transducer_height);
  translate([0, $transducer_leg_separation_radius, -$transducer_leg_height]) {
    cylinder(h=$transducer_leg_height + $fudge, d=$transducer_leg_diameter);
  }
  translate([0, -$transducer_leg_separation_radius, -$transducer_leg_height]) {
    cylinder(h=$transducer_leg_height + $fudge, d=$transducer_leg_diameter);
  }
}

module bottom_cap() {
  intersection() {
    difference() {
      sphere($outer_radius);
      sphere($middle_radius);
        for (i = [0:$row_number-1]){
      for (j = [0:number[i]]){
        rotate([0, angles[i], 360 / number[i] * j])translate([0,0,-$middle_radius- $transducer_inset])transducer();
            }
        }
    
      //translate([0,0, - $outer_radius - 1])cylinder(h = $outer_radius + 1, r2 = 1, r1= ($outer_radius + 1)/tan(90-$end_angle));
    translate([-2*$outer_radius,-2*$outer_radius,-$outer_radius*cos($end_angle+2)])cube([4*$outer_radius,4*$outer_radius,2*$outer_radius]);
  }
  }
}


module two_pillars_bot(){
    z=$outer_radius*cos($end_angle+2);
    difference(){
        translate([0,0,-z])cylinder(r=$outer_radius*sin($end_angle+2),h=z);
        
        translate([0,0,-z-1])cylinder(r=$middle_radius*sin($end_angle),h=2*z+2);
        translate([-$outer_radius*sin($end_angle+2),-$middle_radius*sin($end_angle),-z])cube([2*$outer_radius*sin($end_angle+2),2*$middle_radius*sin($end_angle),2*z]);
    }
}


module screw(){
    z=$outer_radius*cos($end_angle+2);
    pos = $outer_radius*sin($end_angle)*0.707+2;
    screw_diameter = 4;
    difference(){
        translate([0,0,-z-2])cylinder(r=6+$outer_radius*sin($end_angle+2),h=2);
        translate([0,0,-z-3])cylinder(r=$middle_radius*sin($end_angle+2),h=4);
        translate([pos,pos,-z-3])cylinder(d= screw_diameter,h=4);
        translate([pos,-pos,-z-3])cylinder(d= screw_diameter,h=4);
        translate([-pos,pos,-z-3])cylinder(d= screw_diameter,h=4);
        translate([-pos,-pos,-z-3])cylinder(d= screw_diameter,h=4);
        
    }
}

module rod_holes(){
    z=$outer_radius*cos($end_angle+2);
    pos = $outer_radius*sin($end_angle)*0.707+2;
    bar_diameter = 4;
    difference(){
        translate([0,0,-z-2])cylinder(r=6+$outer_radius*sin($end_angle+2),h=2);
        translate([0,0,-z-3])cylinder(r=$middle_radius*sin($end_angle+2),h=4);
        translate([pos,pos,-z-1])cylinder(d= bar_diameter+.2,h=4);
        translate([pos,-pos,-z-1])cylinder(d= bar_diameter+.2,h=4);
        translate([-pos,pos,-z-1])cylinder(d= bar_diameter+.2,h=4);
        translate([-pos,-pos,-z-1])cylinder(d= bar_diameter+.2,h=4);
        
    }
}

module rods(){
    z=$outer_radius*cos($end_angle+2);
    pos = $outer_radius*sin($end_angle)*0.707+2;
    bar_diameter = 4;
    translate([pos,pos,-z-1])cylinder(d= bar_diameter,h=z+1);
    translate([pos,-pos,-z-1])cylinder(d= bar_diameter,h=z+1);
    translate([-pos,pos,-z-1])cylinder(d= bar_diameter,h=z+1);
    translate([-pos,-pos,-z-1])cylinder(d= bar_diameter,h=z+1);
}
    

module final_bot_part(){
    bottom_cap();
    //two_pillars_bot();
    rod_holes();
    //rods();
    //screw();
}

final_bot_part();

mirror([0,0,1])rotate([0,0,180]){
    final_bot_part();
    }
