import dataclasses

@dataclasses.dataclass(frozen=True)
class Hit:
    hit_id: int
    x: float
    y: float
    z: float
    module_id: int
    track_id: int

    def __getitem__(self, index):
        return (self.x, self.y, self.z)[index]
    
    def __eq__(self, __value: object) -> bool:
        if self.hit_id == __value.hit_id:
            return True
        else:
            return False

@dataclasses.dataclass(frozen=True)
class Module:
    module_id: int
    z: float
    lx: float
    ly: float
    hits: list[Hit]
    
    def __eq__(self, __value: object) -> bool:
        if self.module_id == __value.module_id:
            return True
        else:
            return False

@dataclasses.dataclass
class MCInfo:
    primary_vertex  : tuple
    theta           : float
    phi             : float
    
    
@dataclasses.dataclass(frozen=True)
class Track:
    track_id: int
    mc_info : MCInfo
    hits    : list[Hit]
    
    def __eq__(self, __value: object) -> bool:
        if self.track_id == __value.track_id:
            return True
        else:
            return False

@dataclasses.dataclass(frozen=True)
class Event:
    modules: list[Module]
    tracks: list[Track]
    hits: list[Hit]
    
    
    
    
@dataclasses.dataclass(frozen=True)
class Segment:
    segment_id  : int
    hit_from    : Hit
    hit_to      : Hit
    
    def __eq__(self, __value: object) -> bool:
        if self.segment_id == __value.segment_id:
            return True
        else:
            return False
    
    
    def to_vect(self):
        return (self.hit_to.x - self.hit_from.x, 
                self.hit_to.y - self.hit_from.y, 
                self.hit_to.z - self.hit_from.z)
    
    
    def __mul__(self, __value):
        v_1 = self.to_vect()
        v_2 = __value.to_vect()
        n_1 = (v_1[0]**2 + v_1[1]**2 + v_1[2]**2)**0.5
        n_2 = (v_2[0]**2 + v_2[1]**2 + v_2[2]**2)**0.5
        
        return (v_1[0]*v_2[0] + v_1[1]*v_2[1] + v_1[2]*v_2[2])/(n_1*n_2)

