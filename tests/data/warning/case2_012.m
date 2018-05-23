function mpc = case2_000
mpc.version = '2';
mpc.baseMVA = 100.0;

mpc.bus = [
	1	 3	 0.0	 0.0	 0.0	 0.0	 1	    1.10000	   -0.00000	 240.0	 -1	    1.10000	    0.90000;
	2	 0	 110.0	 40.0	 0.0	 0.0	 1	    0.92617	    7.25886	 240.0	 1	    1.10000	    0.90000;
];

mpc.gen = [
	1	 148	 54	 1000.0	 -1000.0	 1.1	 100.0	 1	 2000.0	 0.0	 0.0	 0.0	 0.0	 0.0	 0.0	 0.0	 0.0	 0.0	 0.0	 0.0	 0.0;
];

mpc.gencost = [
	2	 0.0	 0.0	 3	   0.110000	   5.000000	   0.000000;
];

mpc.branch = [
	1	 2	 0.042	 0.9	 0.3	 900.0	 0.0	 0.0	 0.0	 0.0	 1	 -30.0	 30.0;
];
