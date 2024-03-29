# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 11:04:09 2021

@author: Karola
"""
import os
#os.chdir("C:\\Users\\bartakarola\\OneDrive - elte.hu\\birdsong_model_conf_imm_lm\\immigrants_with_non_random_repertoires\\half_deviation_from_the_pop\\8000cycles_migr0_002_004\\raw_simulation_data\\")
os.chdir("D:\\Karola\\birdsong_model_conf_imm_lm\\half_deviation_from_the_pop\\8000cycles_migr006_008_lm04_06\\raw_simulation_data\\")
#os.chdir("C:\\Users\\bartakarola\\OneDrive - elte.hu\\birdsong_model_conf_imm_lm\\immigrants_with_non_random_repertoires\\half_deviation_from_the_pop\\1000cycles_migr0_002_004\\raw_simulation_data\\")


from random import random
from random import sample, randint, choices
import pandas as pd
import multiprocessing
import itertools

import time
from datetime import timedelta

start = time.time()

"""ADJUSTABLE PARAMETERS"""

#Defining the birds class
prop_dev = 0.5
num_of_syll=2000

#general variables and parameters
age = [0,1,2,3,4,5,6,7]
prob_surviving=[0.5, 1 , 0.5, 0.5, 0.5, 0.5, 0.5, 0]
syllables = [syll for syll in range(num_of_syll)] #the x syllables used by the birds

#individual-based variables:

#creating a class called birds:
class Birds:
    #these things should be individualistic:
    def __init__(self, ID):
        self.id=ID
        self.age=0
        if self.age<1: #so if they are juveniles
            self.syll_rep=() #they won't have a repertoire
        self.song=[]
        self.neighbours=[]
        self.neighboursplaces=[]
        self.neigh_song=[]
        self.neigh_syll=[]
        self.prob_surviving=prob_surviving[self.age]



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
    # so everyone has a dataframe of ten of his neighbour's syll_rep 
    for i in set(tutorsrep):
        tutorsrep2 += round(tutorsrep.count(i)**intensity) * [i]
    
    indi=sample(tutorsrep2, 1)
    indi=indi[0]
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
    # normalize back to rel_freq:
    l[individual].syll_rep = l[individual].song[0].tolist()


def song_learning(a, migr, lm, ism):
    #print(a, migr, lm, ism)
    num_cycle = 8000
    countyears=1 # this variable is here in case we would want to record the changes
                 # only in several years
    num_birds=100
    indprodveclen = 150 #individual production vector length
    youngreplen = 30 #young individuals' functional repertoire length
    
    learningoccasions = 20

    birds0=list()
    for bi in range(num_birds):
        birds0.append(Birds(bi))
    #we also need to define syllable reppertoire for them, because 
    # the learning rule will not work otherwise
        birds0[bi].syll_rep=sample(syllables, youngreplen)*round(indprodveclen/youngreplen)
    # creating a dataframe for every bird's song, which we can use later 
        birds0[bi].song = pd.DataFrame(data=(birds0[bi].syll_rep))
    
    
    birds=birds0
    pop10=[]
    pop10=sample(birds,10)

    pop10_rep= pd.DataFrame()
    pop10_indrep = pd.DataFrame()
    #younginds_repchange = pd.DataFrame()

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


    learnmode='conf'+str(a)[0]+str(a)[2:]
    
    
    for c in range(num_cycle):
        for lo in range(learningoccasions):
            for i in range(len(birds)):
                if birds[i].age==0:
                    birds[i].tutors = sample(birds, 10)
                    birds[i].tutors = sample(birds[i].tutors, 1)
                    learning(i, birds, a, learning_mistake = lm)
        
        pop10=sample(birds,10)
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
        
            pop10_rep[str(c+1)] = sum_use/sum(sum_use) # here I put c+1 because otherwise there would be 
            # two columns with the name "0"
            new_pop_syllrep = []
            for i in range(len(birds)): # searching through the population
                for ii in range(len(birds[i].syll_rep)): # searching through their syll_rep
                    new_pop_syllrep.append(birds[i].syll_rep[ii])
                    
            # creating a dataframe that will be built based on the current repertoire of the population but it will contain different syllable types; We will use this later, to fill up the immigrants' repertoire.
        new_pop_syllrep_freq = pd.DataFrame(pd.Series(new_pop_syllrep).value_counts()).rename_axis("syll_types").reset_index()
        indices_to_replace = sample(range(new_pop_syllrep_freq.shape[0]), round(new_pop_syllrep_freq.shape[0]*prop_dev))
        sylls_to_replace_with = sample(syllables, round(new_pop_syllrep_freq.shape[0]*prop_dev)) # this is needed as otherwise there would be a chance that one syllable would be selected more than once which would influence the relative frequncies of syllables of immigrants
        for ind in indices_to_replace:
            new_pop_syllrep_freq["syll_types"][ind] = sylls_to_replace_with.pop()
            
            
        #next step: some of them gotta die
        #survivors=list(np.random.choice(birds, int(len(birds)*(1-lm)), replace=False))
        survivors = []
        for i in range(len(birds)):
            birds[i].prob_surviving=prob_surviving[birds[i].age]
            p=random() #generate a random number between 0 and 1
            if p<birds[i].prob_surviving:
                #if p is less than the prob of surviving of that bird, then
                # that bird is  a survivor, hurray!
                survivors.append(birds[i])
    
        for i in range(len(survivors)):
            survivors[i].age=survivors[i].age+1
    
        if c >= (num_cycle-10):
            for i in range(len(pop10)):
                pop10_indrep[str(c)+'_'+str(i)]=pop10[i].syll_rep
           # for i in range(len(new)):
            #    if new[i] in survivors and i < 10:
             #       colname = str(c)+'_'+str(i)
              #      younginds_repchange[colname+'_0'] = new[i].syll_rep0
               #     younginds_repchange[colname+'_1'] = new[i].syll_rep
    
    
        #creating new birds:
        new=list()
        num_birds = len(birds)
        for uuui in range(num_birds-len(survivors)):
            new.append(Birds(uuui))
        for ni in range(len(new)):
            pm2 = random()
            if pm2<=migr: #this individual among the new ones is an immigrant. As so, its repertoire will be filled up from a different set of syllables but those will have the same frequency distribution as in the population repertoire.
                new[ni].syll_rep=choices(new_pop_syllrep_freq["syll_types"], weights = new_pop_syllrep_freq[0], k=indprodveclen)
                print(new[ni].syll_rep)
                new[ni].song = pd.DataFrame(data=(new[ni].syll_rep))
            else: #this individual among the new ones is a local
                new[ni].syll_rep=sample(new_pop_syllrep, youngreplen*round(indprodveclen/youngreplen))
                new[ni].song = pd.DataFrame(data=(new[ni].syll_rep))
            if c >= (num_cycle-11):
                new[ni].syll_rep0 = new[ni].syll_rep
        
        birds=survivors+new
    
    #pop_rep.to_csv('poprep_'+learnmode+'_'+str(num_cycle)+'x'+str(learningoccasions)+'sys'+str(num_of_syll)+str(lm)[2:]+str(ism)+'.csv')
    pop10_rep.to_csv('pop10rep_'+learnmode+'_'+str(num_cycle)+'x'+str(learningoccasions)+'sys'+str(num_of_syll)+str(migr)[2:]+str(lm)[2:]+str(ism)[0]+'.csv')
    pop10_indrep.to_csv('pop10_indrep_'+learnmode+'_'+str(num_cycle)+'x'+str(learningoccasions)+'sys'+str(num_of_syll)+str(migr)[2:]+str(lm)[2:]+str(ism)[0]+'.csv')
    #younginds_repchange.to_csv('younginds_repchange'+learnmode+'_'+str(num_cycle)+'x'+str(learningoccasions)+'sys'+str(num_of_syll)+str(migr)[2:]+str(lm)[2:]+str(ism)[0]+'.csv')


"""ADJUSTABLE PARAMETERS"""
alpha1 = 1
alpha2 = 1.1
alpha3 = 1.2

migr1 = 0.0
migr2 = 0.02
migr3 = 0.04

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

num_comb = len(params['alpha']) * len(params['migr']) * len(params['lm']) * num_simrep

def main():
    keys = list(params)
    param_combs = pd.DataFrame(columns = ['alpha', 'migr', 'lm', 'ism'], index = [x for x in range(num_comb)])
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


end = time.time()

elapsed_time = end-start

print("elapsed time: " + str(timedelta(seconds=elapsed_time)))

