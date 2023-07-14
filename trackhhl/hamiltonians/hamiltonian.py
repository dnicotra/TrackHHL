from abc import ABC, abstractmethod
from trackhhl.event_model.event_model import Event

class Hamiltonian(ABC):
    
    @abstractmethod
    def construct_hamiltonian(self, event: Event):
        pass
    
    @abstractmethod
    def evaluate(self, solution):
        pass
    