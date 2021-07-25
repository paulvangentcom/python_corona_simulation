class VisualisationSettings:

    def __init__(self, x, y, *args, **kwargs):
        self.visualise = kwargs.get('visualise', True)  # whether to visualise the simulation
        self.plot_mode = kwargs.get('plot_mode', 'sir')  # default or sir
        # size of the simulated world in coordinates
        self.x_plot = kwargs.get('x_plot', [0, x])
        self.y_plot = kwargs.get('y_plot', [0, y])
        self.save_plot = kwargs.get('save_plot', False)
        self.plot_path = kwargs.get('plot_path', 'render/')  # folder where plots are saved to
        self.plot_style = kwargs.get('plot_style', 'default')  # can be default, dark, ...
        self.colorblind_mode = kwargs.get('colorblind_mode', False)
        # if colorblind is enabled, set type of colorblindness
        # available: deuteranopia, protanopia, tritanopia. defauld=deuteranopia
        self.colorblind_type = kwargs.get('colorblind_type', 'deuteranopia')

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value