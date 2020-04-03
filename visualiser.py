'''
contains all methods for visualisation tasks
'''

import matplotlib.pyplot as plt
import numpy as np

from environment import build_hospital


def build_fig(Config, figsize=(5,7)):
    fig = plt.figure(figsize=(5,7))
    spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])

    ax1 = fig.add_subplot(spec[0,0])
    plt.title('infection simulation')
    plt.xlim(Config.xbounds[0], Config.xbounds[1])
    plt.ylim(Config.ybounds[0], Config.ybounds[1])

    ax2 = fig.add_subplot(spec[1,0])
    ax2.set_title('number of infected')
    #ax2.set_xlim(0, simulation_steps)
    ax2.set_ylim(0, Config.pop_size + 100)

    return fig, spec, ax1, ax2


def draw_tstep(Config, population, pop_tracker, frame,
               fig, spec, ax1, ax2):
    #construct plot and visualise
    spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])
    ax1.clear()
    ax2.clear()

    ax1.set_xlim(Config.x_plot[0], Config.x_plot[1])
    ax1.set_ylim(Config.y_plot[0], Config.y_plot[1])

    if Config.self_isolate and Config.isolation_bounds != None:
        build_hospital(Config.isolation_bounds[0], Config.isolation_bounds[2],
                       Config.isolation_bounds[1], Config.isolation_bounds[3], ax1,
                       addcross = False)
        
    #plot population segments
    healthy = population[population[:,6] == 0][:,1:3]
    ax1.scatter(healthy[:,0], healthy[:,1], color='gray', s = 2, label='healthy')
    
    infected = population[population[:,6] == 1][:,1:3]
    ax1.scatter(infected[:,0], infected[:,1], color='red', s = 2, label='infected')

    immune = population[population[:,6] == 2][:,1:3]
    ax1.scatter(immune[:,0], immune[:,1], color='green', s = 2, label='immune')
    
    fatalities = population[population[:,6] == 3][:,1:3]
    ax1.scatter(fatalities[:,0], fatalities[:,1], color='black', s = 2, label='dead')
        
    
    #add text descriptors
    ax1.text(Config.x_plot[0], 
             Config.y_plot[1] + ((Config.y_plot[1] - Config.y_plot[0]) / 100), 
             'timestep: %i, total: %i, healthy: %i infected: %i immune: %i fatalities: %i' %(frame,
                                                                                             len(population),
                                                                                             len(healthy), 
                                                                                             len(infected), 
                                                                                             len(immune), 
                                                                                             len(fatalities)),
                fontsize=6)
    
    ax2.set_title('number of infected')
    ax2.text(0, Config.pop_size * 0.05, 
                'https://github.com/paulvangentcom/python-corona-simulation',
                fontsize=6, alpha=0.5)
    #ax2.set_xlim(0, simulation_steps)
    ax2.set_ylim(0, Config.pop_size + 200)

    if Config.treatment_dependent_risk:
        infected_arr = np.asarray(pop_tracker.infectious)
        indices = np.argwhere(infected_arr >= Config.healthcare_capacity)

        ax2.plot([Config.healthcare_capacity for x in range(len(pop_tracker.infectious))], 
                 color='red', label='healthcare capacity')

    if Config.plot_style.lower() == 'default':
        ax2.plot(pop_tracker.infectious, color='gray')
        ax2.plot(pop_tracker.fatalities, color='black', label='fatalities')
    elif Config.plot_style.lower() == 'sir':
        ax2.plot(pop_tracker.infectious, color='gray')
        ax2.plot(pop_tracker.fatalities, color='black', label='fatalities')
        ax2.plot(pop_tracker.susceptible, color='blue', label='susceptible')
        ax2.plot(pop_tracker.recovered, color='green', label='recovered')
    else:
        raise ValueError('incorrect plot_style specified, use \'sir\' or \'default\'')

    if Config.treatment_dependent_risk:
        ax2.plot(indices, infected_arr[infected_arr >= Config.healthcare_capacity], 
                    color='red')

    ax2.legend(loc = 'best', fontsize = 6)
    
    plt.draw()
    plt.pause(0.0001)

    if Config.save_plot:
        plt.savefig('render/%i.png' %frame)