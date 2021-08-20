from abc import abstractmethod
import simulation
import utils
import visualiser
class command():
    @abstractmethod
    def __init__(self,name):
        self.name=name

    @abstractmethod
    def excute(self):
        pass


class simulateCommand(command):
    def excute(self):
        simulation.run()

class savefileCutCommand(command):
    def excute(self,folder):
        utils.check_folder(folder)



class pltCommand(command):
    def excute(self):
        visualiser.plot_sir()

