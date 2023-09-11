from trackhhl.hamiltonians.simple_hamiltonian import SimpleHamiltonian
from trackhhl.toy.simple_generator import SimpleDetectorGeometry, SimpleGenerator
import numpy as np


def test_SimpleHamiltonian_Classical():
    # Generate a test event
    N_DETECTORS = 25
    N_PARTICLES = 50
    detector = SimpleDetectorGeometry([i for i in range(N_DETECTORS)], [10000 for i in range(N_DETECTORS)], [10000 for i in range(N_DETECTORS)], [i+1 for i in range(N_DETECTORS)])
    generator = SimpleGenerator(detector,theta_max=np.pi/3,rng=np.random.default_rng(0))
    
    event = generator.generate_event(N_PARTICLES)
    
    
    # Initialise Hamiltonian
    EPSILON = 1e-5
    GAMMA = 2.0
    DELTA = 1.0
    
    
    ham = SimpleHamiltonian(EPSILON, GAMMA, DELTA)
    ham.construct_hamiltonian(event)
    sol = ham.solve_classicaly()

    THRESHOLD = .45
    
    discretised_solution = (sol > THRESHOLD)
    truth_solution = [seg.hit_from.track_id == seg.hit_to.track_id for seg in ham.segments]
    
    missed = (discretised_solution != truth_solution).sum()
    print(sol)
    assert missed < .01*len(sol)
    
    result = ham.evaluate(sol).reshape([])

    assert np.allclose(result,10378.26496702)

def test_SimpleHamiltonian_Quantum():
    # Generate a test event
    N_DETECTORS = 3
    N_PARTICLES = 2
    detector = SimpleDetectorGeometry([i for i in range(N_DETECTORS)], [10000 for i in range(N_DETECTORS)], [10000 for i in range(N_DETECTORS)], [i+1 for i in range(N_DETECTORS)])
    generator = SimpleGenerator(detector,theta_max=np.pi/3)
    
    event = generator.generate_event(N_PARTICLES)
    
    
    # Initialise Hamiltonian
    EPSILON = 1e-5
    GAMMA = 2.0
    DELTA = 1.0
    
    
    ham = SimpleHamiltonian(EPSILON, GAMMA, DELTA)
    ham.construct_hamiltonian(event)
    sol = ham.solve_hhl()
    
    THRESHOLD = .45
    
    discretised_solution = np.array((sol > THRESHOLD))
    truth_solution = np.array([seg.hit_from.track_id == seg.hit_to.track_id for seg in ham.segments])
    
    missed = (discretised_solution != truth_solution).sum()
    print(sol)
    assert missed < .01*len(sol)
    
def test_SimpleHamiltonian_QuantumLarger():
    # Generate a test event
    N_DETECTORS = 3
    N_PARTICLES = 3
    detector = SimpleDetectorGeometry([i for i in range(N_DETECTORS)], [10000 for i in range(N_DETECTORS)], [10000 for i in range(N_DETECTORS)], [i+1 for i in range(N_DETECTORS)])
    generator = SimpleGenerator(detector,theta_max=np.pi/3)
    
    event = generator.generate_event(N_PARTICLES)
    
    
    # Initialise Hamiltonian
    EPSILON = 1e-5
    GAMMA = 2.0
    DELTA = 1.0
    
    
    ham = SimpleHamiltonian(EPSILON, GAMMA, DELTA)
    ham.construct_hamiltonian(event)
    sol = ham.solve_hhl()
    
    THRESHOLD = .45
    
    discretised_solution = np.array((sol > THRESHOLD))
    truth_solution = np.array([seg.hit_from.track_id == seg.hit_to.track_id for seg in ham.segments])
    
    print(discretised_solution)
    print(truth_solution)
    missed = (discretised_solution != truth_solution).sum()
    print(sol)
    assert missed < .01*len(sol)

    