class BoundsSettings:

    def __init__(self, x_plot, y_plot, *args, **kwargs):
        self.xbounds = kwargs.get('xbounds', [x_plot[0] + 0.02, x_plot[1] - 0.02])
        self.ybounds = kwargs.get('ybounds', [y_plot[0] + 0.02, y_plot[1] - 0.02])

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value