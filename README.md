# modelling_complex_birdsong_culture_Flycatcher
In this repository You can find codes for the simulations described in our latest manuscript investigating the maintenance of diversity and stability in complex cultures. Demographic parameters are based on a population of collared flycatchers (Ficedula albicollis).

In this repository You can find several script written in Python 3.8.8 that helped us model characteristics of complex animal cultures. The different files served different purposes, You can find their description below.

"complex_culture_model.py" - Script for our initial model, where we tested the following parameter-combinations: the strength of conformism, α = {1, 1.1, 1.2}, the rate of learning mistakes, μl = {0, 0.1, 0.2} and the rate of immigration, μi = {0, 0.02, 0.04}. Each parameter-combination has been run 10 times independent of each other. 

"complex_culture_random_parameter_combinations.py" - Script for a model where the values for each of the three parameters are selected randomly from uniform distributions with the following limits: ⍺ = {1, 1.6}, 𝜇i = {0, 0.1} and 𝜇l = {0, 1}.

"

