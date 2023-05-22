$fn = 96;
$fudge = 0.01;

$inner_radius = (4.68541666667/2)*12;
$thickness = 2;
$end_angle = 53;
$row_number = 2;
angle = [21.9316, 43.0878];
in_row = [6,11];

$transducer_diameter = 10 +.2;
$transducer_height = 7;
$transducer_leg_diameter = 1.5;
$transducer_leg_separation_radius = 5.1/2;
$transducer_leg_height = 10;
$transducer_inset = 1;
$middle_radius = $inner_radius + $transducer_height - $transducer_inset;
$outer_radius = $middle_radius+$thickness;