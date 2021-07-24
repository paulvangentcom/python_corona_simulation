from glob import glob
import os
import numpy as np
import matplotlib.pyplot as plt


class Save:
    save_data = False
    save_pop = False
    save_pop_freq = 10
    save_pop_folder = "data_tstep"
    save_plot = False

    @staticmethod
    def save_data(cls, population, pop_tracker):
        '''dumps simulation data to disk

        Function that dumps the simulation data to specific files on the disk.
        Saves final state of the population matrix, the array of infected over time,
        and the array of fatalities over time

        Keyword arguments
        -----------------
        population : ndarray
            the array containing all the population information

        infected : list or ndarray
            the array containing data of infections over time

        fatalities : list or ndarray
            the array containing data of fatalities over time
        '''
        num_files = len(glob('data/*'))
        cls.check_folder('data/%i' % num_files)
        np.save('data/%i/population.npy' % num_files, population)
        np.save('data/%i/infected.npy' % num_files, pop_tracker.infectious)
        np.save('data/%i/recovered.npy' % num_files, pop_tracker.recovered)
        np.save('data/%i/fatalities.npy' % num_files, pop_tracker.fatalities)

    @staticmethod
    def save_population(cls, population, tstep=0):
        '''dumps population data at given timestep to disk

        Function that dumps the simulation data to specific files on the disk.
        Saves final state of the population matrix, the array of infected over time,
        and the array of fatalities over time

        Keyword arguments
        -----------------
        population : ndarray
            the array containing all the population information

        tstep : int
            the timestep that will be saved
        '''
        cls.check_folder('%s/' % (cls.save_pop_folder))
        np.save('%s/population_%i.npy' % (cls.save_pop_folder, tstep), population)

    @staticmethod
    def savefig(plot_path, frame):
        plt.savefig('%s/%i.png' % (plot_path, frame))

    @staticmethod
    def check_folder(folder='render/'):
        '''check if folder exists, make if not present'''
        if not os.path.exists(folder):
            os.makedirs(folder)
