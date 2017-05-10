
import os, sys, glob
from pyglet.gl import *
from pyglet import clock
from pyglet import window
import covergl
import anim

Z_NEAR = 1.0
Z_FAR  = 50.0
FOVY   = 20.0

def setup():
    afLightDiffuse = [0.76, 0.75, 0.65, 1.0]
    
    # set some GL-states
    glClearColor(1.0, 0.5, 0.25, 1.0)
    glColor4f(0.25, 0.5, 1.0, 1.0)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_TEXTURE_RECTANGLE_ARB)
    glEnable(GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 1)
    glDisable(GL_DEPTH_TEST)

    # lights and so on */
    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * len(afLightDiffuse))(*afLightDiffuse))

    # setup "camera" */
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, Z_NEAR,
           0.0, 0.0, 0.0,
           0.0, 1.0, 0.0)
    glTranslatef(0.0, 0.0, -Z_NEAR)

if __name__ == "__main__":
    width, height = 640, 480
    try:
        # Try and create a window with multisampling (antialiasing)
        #config = Config(sample_buffers=1, samples=4, 
        #                depth_size=16, double_buffer=True,)
        config = Config(depth_size=16, double_buffer=True,)
        w = window.Window(width=width, height=height, resizable=True, config=config)
    except window.NoSuchConfigException:
        print "No multisampling"
        # Fall back to no multisampling for old hardware
        w = window.Window(width=width, height=height, resizable=True)

    @w.event
    def on_resize(w, h):
        # Override the default on_resize handler to create a 3D projection
        glViewport (0, 0, w, h)
        covergl.change_projection(True, w, h)
        glClear(GL_COLOR_BUFFER_BIT)

    setup()
    covergl.setup_values()

    path = sys.argv[1]
    filenames = glob.glob(path+"/*")[:20]
    curdir = os.path.abspath(os.curdir)
    covers = []
    tracks = []
    for i, fname in enumerate(filenames):
        cover = covergl.Cover(2.0, fname, angle=-70)
        x = i*0.75
        cover.fX.set(x)
        covers.append(cover)
        tracks.append(x)
    covers[0].focus()

    advance = covergl.mk_advance(tracks, covers)
    @w.event
    def on_key_press(symbol, modifiers):
        if symbol == window.key.LEFT: advance(True)
        elif symbol == window.key.RIGHT: advance(False)

    @w.event
    def on_mouse_motion(x, y, dx, dy, tmp_dx=[0]):
        tmp_dx[0] += dx
        if tmp_dx[0] > 20:
            tmp_dx[0] = 0
            advance(False)
        elif tmp_dx[0] < -20:
            tmp_dx[0] = 0
            advance(True)

    clock = clock.get_default()
    clock.set_fps_limit(40)
    clock.schedule(anim.add_time)
    while not w.has_exit:
        dt = clock.tick()
        w.dispatch_events()
        covergl.display(w.width, w.height, covers)
        w.flip()
