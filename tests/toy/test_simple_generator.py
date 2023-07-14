import trackhhl.toy.simple_generator as gen


def build_simple_detector(n_modules):
    module_id = [i for i in range(n_modules)]
    lx = ly = [10 for i in range(n_modules)]
    z = [i*10 for i in range(n_modules)]
    detector = gen.SimpleDetectorGeometry(module_id=module_id, lx=lx, ly=ly, z=z)
    return detector

def test_SimpleDetectorGeometry():
    build_simple_detector(n_modules=100)
    
def test_SimpleGenerator():
    detector = build_simple_detector(10)
    generator = gen.SimpleGenerator(detector)
    ev1 = generator.generate_event(10)
    ev2 = generator.generate_event(10)
    
    assert ev1 != ev2
