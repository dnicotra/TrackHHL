from trackhhl.event_model.event_model import Event, Segment
from trackhhl.hamiltonians.hamiltonian import Hamiltonian
from itertools import product, count
from scipy.sparse import coo_matrix, eye
from scipy.sparse.linalg import cg
import numpy as np
from collections import namedtuple
from qiskit.algorithms.linear_solvers import HHL
from qiskit.circuit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector
import qiskit_aer
def upscale_pow2(A,b):
    m = A.shape[0]
    d = int(2**np.ceil(np.log2(m)) - m)
    if d > 0:
        A_tilde = np.block([[A, np.zeros((m, d),dtype=np.float64)],[np.zeros((d, m),dtype=np.float64), np.eye(d,dtype=np.float64)]])
        b_tilde = np.block([b,b[:d]])
        return A_tilde, b_tilde
    else:
        return A, b

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
    
    def solve_hhl(self, epsilon=0.01, circuit_only=False):
        if self.A is None:
            raise Exception("Not initialised")
        # Construct the circuit
        A = self.A.todense()
        b = self.b
        
        A, b = upscale_pow2(A,b)
        
        b_circuit = QuantumCircuit(QuantumRegister(int(np.log2(len(b)))), name="init")
        for i in range(int(np.log2(len(b)))):
            b_circuit.h(i)
        
        hhl_solver = HHL(epsilon=epsilon)
        circuit = hhl_solver.construct_circuit(A, b_circuit, neg_vals=False)
        if circuit_only: return circuit
        
        # Get the final state vector
        state_vector = Statevector(circuit)
        solution_norm = hhl_solver._calculate_norm(circuit)
        
        # Pick the correct slice and renormalise it back
        post_select_qubit = int(np.log2(len(state_vector.data)))-1
        solution_len = len(b)
        base = 1 << post_select_qubit
        solution_vector = state_vector.data[base : base+solution_len].real
        solution_vector = solution_vector/np.linalg.norm(solution_vector)*solution_norm*np.linalg.norm(b)
        
        
        return solution_vector[:len(self.b)]


    def evaluate(self, solution):
        if self.A is None:
            raise Exception("Not initialised")
        
        if isinstance(solution, list):
            sol = np.array([solution, None])
        elif isinstance(solution, np.ndarray):
            if solution.ndim == 1:
                sol = solution[..., None]
            else: sol = solution
            
            
        return -0.5 * sol.T @ self.A @ sol + self.b.dot(sol)
        