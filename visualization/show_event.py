import vispy.app
import vispy.scene
import vispy.io
import json
import velopix_tracking.event_model.event_model as em
import numpy as np
from velopix_tracking.algorithms.track_following import track_following
SCALING = 6
def load_event(path):
    with open(path) as f:
        json_data = json.load(f)
        event = em.event(json_data)
    return event, json_data

def solve_event(event):
    solver = track_following()
    tracks = solver.solve(event)
    return tracks

def create_scene(size=(600, 600)):
    canvas = vispy.scene.SceneCanvas(
        title="Event display",
        keys="interactive",
        size=size,
        show=True
    )
    
    view = canvas.central_widget.add_view()
    view.camera = vispy.scene.cameras.ArcballCamera(fov=0, center=(239.9433007305307, 0.0, 13.014278441618844), scale_factor=750.0)
    return canvas, view

def show_hits(hits, view, size=5, color = 'red'):
    positions = np.array([[h[2], h[0]*SCALING, h[1]*SCALING] for h in hits])
    hits_vis = vispy.scene.visuals.Markers(
        pos=positions,
        size=size,
        face_color=color,
        edge_color='white',
        edge_width=0,
        scaling=True,
        spherical=False,
        antialias=True
    )
    hits_vis.parent = view.scene
    return hits_vis

def show_tracks(tracks, view, size=2, color='white'):
    segments = []
    for track in tracks:
        zsorted_hits = sorted(track.hits, key=lambda h: h[2])
        for h1, h2 in zip(zsorted_hits[:-1],zsorted_hits[1:]):
            segments.append([h1[2], h1[0]*SCALING, h1[1]*SCALING])
            segments.append([h2[2], h2[0]*SCALING, h2[1]*SCALING])
            
    segments = np.array(segments)
    tracks_vis = vispy.scene.visuals.Line(
        pos = segments,
        connect='segments',
        width=size,
        color=color,
        antialias=True
    )
    tracks_vis.parent = view.scene
    return tracks_vis
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", type=str)
    args = parser.parse_args()
    event, json_data = load_event(args.json_file)
    tracks = solve_event(event)
    
    hit_size = 3
    
    canvas, view = create_scene()
    hits_vis = show_hits(event.hits, view, size=hit_size,color=(1,0,0,1))
    tracks_vis = show_tracks(tracks, view,size=1,color=(1,1,1,0.6))
    
    #img = canvas.render()
    #vispy.io.write_png("out.png", img)

    @canvas.connect
    def on_key_press(ev):
        global view
        if ev.key.name in '+=':
            print(view.camera.scale_factor, view.camera.center)
    
    vispy.app.run()