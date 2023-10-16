# WAGE_cube_attack
The implementation of paper "An Improved Method for Evaluating Secret Variables and Its Application to WAGE".

The inequalities for component SB and WGP are provided in "inequality" folder.

The functions in "main.py" include secret variables evaluation function and degree estimation function.
SuperPoly_var_x() is used to evaluate secret variables for certain cube. Moreover, SuperPoly_var() corresponds to Todo's method, SuperPoly_varv2() corresponds to individual method and SuperPoly_varv3() is for our improved method.
Superpoly_degree_estimation() and Upbound() are functions for degree estimations, which would help find useful cube.
