from trackhhl.event_model.event_model import Event, Segment
from trackhhl.hamiltonians.hamiltonian import Hamiltonian
from itertools import product, count
from scipy.sparse import coo_matrix, eye
from scipy.sparse.linalg import cg
import numpy as np
from collections import namedtuple

class SimpleHamiltonian(Hamiltonian):
    def __init__(self, epsilon, gamma, delta):
        self.epsilon                                    = epsilon
        self.gamma                                      = gamma
        self.delta                                      = delta
        self.A                                          = None
        self.b                                          = None
        self.segments                                   = None
        self.segments_grouped                           = None
        self.n_segments                                 = None
    
    
    def construct_segments(self, event: Event):
        segments_grouped = []
        segments = []
        n_segments = 0
        segment_id = count()
        for idx in range(len(event.modules)-1):
            from_hits = event.modules[idx].hits
            to_hits = event.modules[idx+1].hits
            
            segments_group = []
            for from_hit, to_hit in product(from_hits, to_hits):
                seg = Segment(next(segment_id),from_hit, to_hit)
                segments_group.append(seg)
                segments.append(seg)
                n_segments = n_segments + 1
        
            segments_grouped.append(segments_group)
            
        
        self.segments_grouped = segments_grouped
        self.segments = segments
        self.n_segments = n_segments
        
    
    def construct_hamiltonian(self, event: Event):
        
        if self.segments_grouped is None:
            self.construct_segments(event)
            
        A = eye(self.n_segments,format='lil')*(-(self.delta+self.gamma))
        b = np.ones(self.n_segments)*self.delta
        
        for group_idx in range(len(self.segments_grouped) - 1):
            for seg_i, seg_j in product(self.segments_grouped[group_idx], self.segments_grouped[group_idx+1]):
                if seg_i.hit_to == seg_j.hit_from:
                    cosine = seg_i * seg_j
                    
                    if abs(cosine - 1) < self.epsilon:
                        A[seg_i.segment_id, seg_j.segment_id] = A[seg_j.segment_id, seg_i.segment_id] =  1
                    
        
        A = A.tocsc()
        
        self.A, self.b = -A, b
        return -A, b
    
    
    
    def solve_classicaly(self):
        if self.A is None:
            raise Exception("Not initialised")
        
        solution, _ = cg(self.A, self.b, atol=0)
        return solution
    


    def evaluate(self, solution):
        raise NotImplemented
        