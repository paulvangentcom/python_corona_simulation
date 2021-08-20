from abc import abstractmethod


class iterator():
    @abstractmethod
    def getNext(self):
        pass

    @abstractmethod
    def hasMore(self):
        pass

class populationIterator(iterator):
    def __init__(self,tracker):
        self.tracker=tracker
        self.currentposition=0
    def getNext(self):
        if(self.hasMore()):
            self.currentposition+=1
            return self.tracker[self.currentposition]
    def hasMore(self):
        return self.currentposition < len(self.tracker)