
import numpy as np


def find_nearby(population, infection_zone, traveling_infects=False,
                kind='healthy', infected_previous_step=[]):
    '''finds nearby IDs

    Keyword Arguments
    -----------------

    kind : str (can be 'healthy' or 'infected')
        determines whether infected or healthy individuals are returned
        within the infection_zone


    Returns
    -------
    if kind='healthy', indices of healthy agents within the infection
    zone is returned. This is because for each healthy agent, the chance to
    become infected needs to be tested

    if kind='infected', only the number of infected within the infection zone is
    returned. This is because in this situation, the odds of the healthy agent at
    the center of the infection zone depend on how many infectious agents are around
    it.
    '''

    if kind.lower() == 'healthy':
        indices = np.int32(population[:,0][(infection_zone[0] < population[:,1]) &
                                            (population[:,1] < infection_zone[2]) &
                                            (infection_zone[1] < population [:,2]) &
                                            (population[:,2] < infection_zone[3]) &
                                            (population[:,6] == 0)])
        return indices

    elif kind.lower() == 'infected':
        if traveling_infects:
            infected_number = len(infected_previous_step[:,6][(infection_zone[0] < infected_previous_step[:,1]) &
                                                            (infected_previous_step[:,1] < infection_zone[2]) &
                                                            (infection_zone[1] < infected_previous_step [:,2]) &
                                                            (infected_previous_step[:,2] < infection_zone[3]) &
                                                            (infected_previous_step[:,6] == 1)])
        else:
            infected_number = len(infected_previous_step[:,6][(infection_zone[0] < infected_previous_step[:,1]) &
                                                            (infected_previous_step[:,1] < infection_zone[2]) &
                                                            (infection_zone[1] < infected_previous_step [:,2]) &
                                                            (infected_previous_step[:,2] < infection_zone[3]) &
                                                            (infected_previous_step[:,6] == 1) &
                                                            (infected_previous_step[:,11] == 0)])
        return infected_number

    else:
        raise ValueError('type to find %s not understood! Must be either \'healthy\' or \'ill\'')
