# chassis/integrator.py

def step(bodies, dt):
    for body in bodies:
        body.integrate(dt)
