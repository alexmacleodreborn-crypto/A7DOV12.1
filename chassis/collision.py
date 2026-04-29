# chassis/collision.py

GROUND_Y = 0.0
BOUNCE = 0.2
FRICTION = 0.8

def handle_ground_collision(body):
    if body.position[1] < GROUND_Y:
        body.position[1] = GROUND_Y

        # reverse vertical velocity
        body.velocity[1] *= -BOUNCE

        # apply friction
        body.velocity[0] *= FRICTION
        body.velocity[2] *= FRICTION
