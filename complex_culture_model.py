# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 11:04:09 2021

@author: Karola Anna Barta
"""
# setting up the working directory:
import os
os.chdir("path to the working directory")

# importing neccessary packages and functions:
from random import random
from random import sample, randint
import pandas as pd
import multiprocessing
import itertools

"""ADJUSTABLE PARAMETERS"""

#general variables and parameters:
num_of_syll=2000 # number of different syllable types in the pool of syllables
age = [0,1,2,3,4,5,6,7] # age categories birds could have
prob_surviving=[0.5, 1 , 0.5, 0.5, 0.5, 0.5, 0.5, 0] # probabilities of surviving in a given age cathegory
syllables = [syll for syll in range(num_of_syll)] # pool of syllables (a vector)


#Defining the birds class
class Birds:
    #the following things should be defined on the individual level:
    def __init__(self, ID):
        self.id=ID
        self.age=0 # their default age is 0
        if self.age<1: #so if they are juveniles
            self.syll_rep=() #they won't have a repertoire
        self.song=[]
        self.neighbours=[]
        self.neighboursplaces=[]
        self.neigh_song=[]
        self.neigh_syll=[]
        self.prob_surviving=prob_surviving[self.age]


# Function for social learning:
    # During learning young individuals get a randomly chosen tutor. The repertoire of this tutor gets copied into a vector in which each element will be found according to the strength of the conformist bias (intensity). The young individual will acquire a randomly chosen syllable from this vector (tutorsrep2). With a given probability, a learning mistake will be made. After this, the final syllable gets implemented in the young individual's production vector by substituting another, randomly chosen syllable. The function takes four parameters: the learning indiidual's identity (individual), a list containing all the birds in the population (l), the strength of conformism (intensity) and the allowed rate of learning mistakes (learning_mistake).
def learning(individual, l, intensity, learning_mistake):
    indi = num_of_syll
    tutorsrep = [] # the production vector of tutors
    tutorsrep2 = [] # the production vector raied to alpha/intensity
    #collecting the syllables used by  the juveniles' tutors
    
    for ii in l[individual].tutors:
        for si in ii.syll_rep:
            tutorsrep.append(si)
    
    l[individual].tutors_song = pd.DataFrame(data=(tutorsrep))
    
    #learning: randomly from tutors
    for i in set(tutorsrep):
        tutorsrep2 += round(tutorsrep.count(i)**intensity) * [i]
    
    indi=sample(tutorsrep2, 1)
    indi=indi[0]
    # Does a mistake in learning happen? 'pm' will decide this.
    pm = random()
    if pm <= learning_mistake: # a mistake in learning happens
        #print("A mistake is being made, turning", indi, "into:")
        plusminusone = sample([-1, 1], 1)[0]
        if indi == 0 and plusminusone == -1:
            indi = num_of_syll-1
        elif indi == num_of_syll-1 and plusminusone == 1:
            indi = 0
        else:
            indi = indi + plusminusone
        #print(indi)
    # changing a RANDOM syllable in the ind's rep to the new, learned syllable
    l[individual].song.loc[randint(0, len(l[individual].song)-1)] = indi
    # recalculate the relative frequency of syllable types:
    l[individual].syll_rep = l[individual].song[0].tolist()

# The function containing the main simulation cycle:the definition of additional parameters and that of the initial population, the learning of young individuals and the life-cycle main cycle of the simulations
def song_learning(a, migr, lm, ism):
    num_cycle=8000 #  For how many cycles (years) the simulation should run for?
    countyears=1 # this variable is here in case we would want to record the changes only in several years
    num_birds=100 # number of birds in the population
    learningoccasions = 20 # number of learning occasions/individual/year
    
    #individual-based variables:
    indprodveclen = 150 #individual production vector length
    youngreplen = 30 #young individuals' functional repertoire length

    # Defining the initial population:
    birds0=list()
    for bi in range(num_birds):
        birds0.append(Birds(bi))
    #we also need to define syllable reppertoire for them, because 
    # the learning rule will not work otherwise
        birds0[bi].syll_rep=sample(syllables, youngreplen)*round(indprodveclen/youngreplen)
    # creating a dataframe for every bird's song, which we can use later 
        birds0[bi].song = pd.DataFrame(data=(birds0[bi].syll_rep))
    
    
    birds=birds0
    
    # Defining vectors and data frames needed for data collection:
    pop10=[]
    pop10=sample(birds,10)

    pop10_rep= pd.DataFrame()
    pop10_indrep = pd.DataFrame()
    younginds_repchange = pd.DataFrame()

    new_pop10_rep=pd.DataFrame()
    new_pop10_syllrep = []

    for i in range(len(pop10)): # searching through the population
        for ii in range(len(pop10[i].syll_rep)): # searching through their syll_rep
            new_pop10_syllrep.append(pop10[i].syll_rep[ii])

    new_pop10_rep[0]=new_pop10_syllrep
    new_pop10_rep=new_pop10_rep.sort_values([0])
    sum_use = []
    
    for i in range(len(syllables)):
        sum_use.append(new_pop10_rep.loc[new_pop10_rep[0] == i, 0].count())

    pop10_rep[str(0)] = sum_use/sum(sum_use) 

    
    learnmode='conf'+str(a)[0]+str(a)[2:] # a variable used when writing out files
    
    # The main cycle designating the years:
    for c in range(num_cycle):
        # Within a year, individuals learn for a given number of times:
        for lo in range(learningoccasions):
            for i in range(len(birds)):
                #Only young individuals learn:
                if birds[i].age==0:
                    birds[i].tutors = sample(birds, 10)
                    birds[i].tutors = sample(birds[i].tutors, 1)
                    learning(i, birds, a, learning_mistake = lm)
        
        # For the purpose of this study, we collected data on the repertoire of only 10 individuals from the population:
        pop10=sample(birds,10)
        # Then in each year we collected data on them:
        if (c+1)% countyears == 0:
            new_pop10_rep=pd.DataFrame()
            new_pop10_syllrep = []
            for i in range(len(pop10)): # searching through the population
                for ii in range(len(pop10[i].syll_rep)): # searching through their syll_rep
                    new_pop10_syllrep.append(pop10[i].syll_rep[ii])
        
            new_pop10_rep[0]=new_pop10_syllrep
            new_pop10_rep=new_pop10_rep.sort_values([0])
            sum_use = []
            #
            for i in range(len(syllables)):
                sum_use.append(new_pop10_rep.loc[new_pop10_rep[0] == i, 0].count())
        
            pop10_rep[str(c+1)] = sum_use/sum(sum_use) # here I put c+1 because otherwise there would be two columns with the name "0"
            new_pop_syllrep = []
            for i in range(len(birds)): # searching through the population
                for ii in range(len(birds[i].syll_rep)): # searching through their syll_rep
                    new_pop_syllrep.append(birds[i].syll_rep[ii])
        
        # Each year a proportion of the population passed away according to their individual surviving probability:
        survivors = []
        for i in range(len(birds)):
            birds[i].prob_surviving=prob_surviving[birds[i].age]
            p=random() #generate a random number between 0 and 1
            if p<birds[i].prob_surviving:
                #if p is less than the prob of surviving of that bird, then
                # that bird is  a survivor, hurray!
                survivors.append(birds[i])
    
        # Collecting the survivors into a separate vector:
        for i in range(len(survivors)):
            survivors[i].age=survivors[i].age+1
        
        # collecting data from the last 10 years of the simulations:
        if c >= (num_cycle-10):
            for i in range(len(pop10)):
                pop10_indrep[str(c)+'_'+str(i)]=pop10[i].syll_rep
            for i in range(len(new)):
                if new[i] in survivors and i < 10:
                    colname = str(c)+'_'+str(i)
                    younginds_repchange[colname+'_0'] = new[i].syll_rep0
                    younginds_repchange[colname+'_1'] = new[i].syll_rep
    
    
        # Filling up the population with new birds:
        new=list()
        num_birds = len(birds)
        for uuui in range(num_birds-len(survivors)):
            new.append(Birds(uuui))
        for ni in range(len(new)):
            pm2 = random()
            if pm2<=migr: #this individual among the new ones is a migrant
                new[ni].syll_rep=sample(syllables, youngreplen)*round(indprodveclen/youngreplen)
                new[ni].song = pd.DataFrame(data=(new[ni].syll_rep))
            else: #this individual among the new ones is a local
                new[ni].syll_rep=sample(new_pop_syllrep, youngreplen*round(indprodveclen/youngreplen))
                new[ni].song = pd.DataFrame(data=(new[ni].syll_rep))
            if c >= (num_cycle-11):
                new[ni].syll_rep0 = new[ni].syll_rep
        
        birds=survivors+new
    
    # Writing out the necessary files: 
    pop10_rep.to_csv('pop10rep_'+learnmode+'_'+str(num_cycle)+'x'+str(learningoccasions)+'sys'+str(num_of_syll)+str(migr)[2:]+str(lm)[2:]+str(ism)[0]+'.csv')
    pop10_indrep.to_csv('pop10_indrep_'+learnmode+'_'+str(num_cycle)+'x'+str(learningoccasions)+'sys'+str(num_of_syll)+str(migr)[2:]+str(lm)[2:]+str(ism)[0]+'.csv')
    younginds_repchange.to_csv('younginds_repchange'+learnmode+'_'+str(num_cycle)+'x'+str(learningoccasions)+'sys'+str(num_of_syll)+str(migr)[2:]+str(lm)[2:]+str(ism)[0]+'.csv')
    
    dmp10 = pd.DataFrame()
    column_nr = len(pop10_rep.loc[0,])
    
    for i in range(column_nr): # getting through columns/years/num_cycle
        dij10=[]
        for j in range(column_nr): # getting through columns/years/num_cycle again
            sumdiff = sum(abs(pop10_rep.iloc[:,i]-pop10_rep.iloc[:,j]))
            dij10.append(0.5*sumdiff)
        dmp10[str(i)]=dij10
    
    dmp10.to_csv('distmatpop10_'+learnmode+'_'+str(num_cycle)+'x'+str(learningoccasions)+'sys'+str(num_of_syll)+str(migr)[2:]+str(lm)[2:]+str(ism)[0]+'.csv')

    lydmp10 = pd.DataFrame()
    diff=[]
    values=[]
    for c in range(num_cycle-10,num_cycle):
        for r in range(num_cycle-10,num_cycle):
            if c>r:
                diff.append(c-r)
                values.append(dmp10.iloc[r,c])
    lydmp10[1]=diff
    lydmp10[2]=values
    lydmp10 = lydmp10.sort_values([1,2])
    lydmp10.to_csv('lydmp10_'+learnmode+'_'+str(num_cycle)+'x'+str(learningoccasions)+'sys'+str(num_of_syll)+str(migr)[2:]+str(lm)[2:]+str(ism)[0]+'.csv')
    

# As the simulations take a long time to run, we used multiprocessing to run those with different parameter-combinations simultaneously.
# Description of the multiprocessing method can be found at https://docs.python.org/3/library/multiprocessing.html

"""ADJUSTABLE PARAMETERS"""
alpha1 = 1
alpha2 = 1.1
alpha3 = 1.2

migr1 = 0.0
migr2 = 0.01
migr3 = 0.02

lm1 = 0.0
lm2 = 0.1
lm3 = 0.2

num_simrep = 10


params = {
        'alpha' : [alpha1, alpha2, alpha3],
        'migr' : [migr1, migr2, migr3],
        'lm' : [lm1, lm2, lm3],
        'ism' : [x for x in range(num_simrep)]
        }

    
def main():
    keys = list(params)
    param_combs = pd.DataFrame(columns = ['alpha', 'migr', 'lm', 'ism'], index = [x for x in range(270)])
    rownum = 0
    
    
    for values in itertools.product(*map(params.get, keys)):
        param_combs.loc[rownum] = list(values)
        rownum = rownum+1

    with multiprocessing.Pool(10) as pool:
        pool.starmap(song_learning, zip(param_combs.iloc[:,0], 
                                        param_combs.iloc[:,1], 
                                        param_combs.iloc[:,2], 
                                        param_combs.iloc[:,3]))
                
        
if __name__ == '__main__':
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    main()

