import numpy as np
import trackhhl.event_model as em
import dataclasses
from itertools import count

@dataclasses.dataclass(frozen=True)
class SimpleDetectorGeometry:
    module_id   : list[int]
    lx          : list[float]
    ly          : list[float]
    z           : list[float]
    
    def __getitem__(self, index):
        return (self.module_id[index], self.lx[index], self.ly[index], self.z[index])
    
    def __len__(self):
        return len(self.module_id)
    
 
@dataclasses.dataclass()   
class SimpleGenerator:
    detector_geometry   : SimpleDetectorGeometry
    phi_min             : float = 0.0
    phi_max             : float = 2*np.pi
    theta_min           : float = 0.0
    theta_max           : float = np.pi/10
    primary_vertex      : tuple = (0.0,0.0,0.0)
    rng                 : np.random.Generator = np.random.default_rng()
    
    
    def generate_event(self, n_particles):
        hit_id_counter = count()
        mc_info = []
        
        hits_per_module = [[] for _ in range(len(self.detector_geometry.module_id))]
        hits_per_track  = []
        
        pvx, pvy, pvz = self.primary_vertex
        
        for track_id in range(n_particles):
            phi         = self.rng.uniform(self.phi_min, self.phi_max)
            cos_theta   = self.rng.uniform(np.cos(self.theta_max), np.cos(self.theta_min))
            theta = np.arccos(cos_theta)
            sin_theta = np.sin(theta)
            
            mc_info.append((track_id, em.MCInfo(
                self.primary_vertex,
                phi,
                theta)))
            
            vx = sin_theta*np.cos(phi)
            vy = sin_theta*np.sin(phi)
            vz = cos_theta
            
            track_hits = []
            for idx, (module_id, zm, lx ,ly) in enumerate(zip(self.detector_geometry.module_id, self.detector_geometry.z, self.detector_geometry.lx, self.detector_geometry.ly)):
                t = (zm - pvz)/vz
                x_hit = pvx + vx*t
                y_hit = pvy + vy*t
                
                if np.abs(x_hit) < lx/2 and np.abs(y_hit) < ly/2:
                    hit = em.Hit(next(hit_id_counter), x_hit, y_hit, zm, module_id, track_id)
                    hits_per_module[idx].append(hit)
                    track_hits.append(hit)
            hits_per_track.append(track_hits)
        
        modules = [em.Module(module_id, z, lx ,ly, hits_per_module[idx]) for idx, (module_id, z, lx ,ly) in enumerate(zip(self.detector_geometry.module_id, self.detector_geometry.z, self.detector_geometry.lx, self.detector_geometry.ly))]
        tracks = []
        
        for idx, (track_id, mc_info) in enumerate(mc_info):
               tracks.append(em.Track(track_id, mc_info, hits_per_track[idx]))
        global_hits = [hit for sublist in hits_per_module for hit in sublist]
        
        return em.Event(modules, tracks, global_hits)
            