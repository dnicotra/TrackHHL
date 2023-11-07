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
    primary_vertices    : list = dataclasses.field(default_factory=list)
    phi_min             : float = 0.0
    phi_max             : float = 2*np.pi
    theta_min           : float = 0.0
    theta_max           : float = np.pi/10
    rng                 : np.random.Generator = np.random.default_rng()
    
    def generate_random_primary_vertices(self, n_events, sigma):
        primary_vertices = []
        for _ in range(n_events):
            x = self.rng.normal(0, sigma[0])
            y = self.rng.normal(0, sigma[1])
            z = self.rng.normal(0, sigma[2])
            primary_vertices.append((x, y, z))
        return primary_vertices
    
    def generate_event(self, n_particles, n_events=1, sigma=(0,0,0)):
        hit_id_counter = count()
        all_events = []

        for _ in range(n_events):
            if n_events == 1:
                primary_vertex = (0,0,0)
            else:
                primary_vertex = self.generate_random_primary_vertices(1,sigma)[0]

            mc_info = []

            hits_per_module = [[] for _ in range(len(self.detector_geometry.module_id))]
            hits_per_track = []

            pvx, pvy, pvz = primary_vertex
            self.primary_vertices.append((pvx, pvy, pvz))

            for track_id in range(n_particles):
                phi = self.rng.uniform(self.phi_min, self.phi_max)
                cos_theta = self.rng.uniform(np.cos(self.theta_max), np.cos(self.theta_min))
                theta = np.arccos(cos_theta)
                sin_theta = np.sin(theta)

                mc_info.append((track_id, em.MCInfo(
                    primary_vertex,
                    phi,
                    theta)))

                vx = sin_theta * np.cos(phi)
                vy = sin_theta * np.sin(phi)
                vz = cos_theta

                track_hits = []
                for idx, (module_id, zm, lx, ly) in enumerate(
                        zip(self.detector_geometry.module_id, self.detector_geometry.z, self.detector_geometry.lx,
                            self.detector_geometry.ly)):
                    t = (zm - pvz) / vz
                    x_hit = pvx + vx * t
                    y_hit = pvy + vy * t

                    if np.abs(x_hit) < lx / 2 and np.abs(y_hit) < ly / 2:
                        hit = em.Hit(next(hit_id_counter), x_hit, y_hit, zm, module_id, track_id)
                        hits_per_module[idx].append(hit)
                        track_hits.append(hit)
                hits_per_track.append(track_hits)

            modules = [em.Module(module_id, z, lx, ly, hits_per_module[idx]) for idx, (module_id, z, lx, ly) in
                       enumerate(
                           zip(self.detector_geometry.module_id, self.detector_geometry.z, self.detector_geometry.lx,
                                self.detector_geometry.ly))]
            tracks = []

            for idx, (track_id, mc_info) in enumerate(mc_info):
                tracks.append(em.Track(track_id, mc_info, hits_per_track[idx]))
            global_hits = [hit for sublist in hits_per_module for hit in sublist]

            all_events.append(em.Event(modules, tracks, global_hits))
        if n_events == 1:
            all_events = all_events[0]
        return all_events
            
