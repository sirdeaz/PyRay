import pygame
import numpy
import sys
import time

class Sphere(object):
    def __init__(self, center, radius):
        self.center = numpy.array(center)
        self.radius = numpy.array(radius)
        self.radius2 = self.radius * self.radius

    def hit(self, ray):
        'Heavily based on the geometric solution from https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-sphere-intersection'

        L = self.center - ray.origin
        D = ray.direction

        tca = numpy.dot(L, D)

        if tca < 0:
            return None

        d2 = numpy.dot(L, L) - tca * tca

        if d2 > self.radius2:
            return None

        thc = numpy.sqrt(self.radius2 - d2)

        t0 = tca - thc

        hit_point = ray.origin + t0 * ray.direction
        normal = None  # todo: not sure what to do with this?

        return ShadeRecord(normal=normal, hit_point=hit_point)


class Ray(object):
    def __init__(self, origin, direction):
        self.origin = numpy.array(origin)
        self.direction = numpy.array(direction)


class ShadeRecord(object):
    def __init__(self, hit_point, normal):
        self.hit_point = hit_point
        self.normal = normal


class Tracer(object):
    def __init__(self, world):
        self.world = world

    def trace_ray(self, ray):
        if self.world.sphere.hit(ray):
            return (1.0, 0.0, 0.0)
        else:
            return (0.0, 0.0, 0.0)


class ViewPlane(object):
    'Interesting article at https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-generating-camera-rays/generating-camera-rays'

    def __init__(self, resolution, pixel_size):
        self.resolution = resolution
        self.pixel_size = pixel_size

    def iter_row(self, row):
        for column in range(self.resolution[0]):
            origin = numpy.zeros(3)
            # origin[0] = self.pixel_size*(column - self.resolution[0] / 2 + 0.5)
            # origin[1] = self.pixel_size*(row - self.resolution[1] / 2 + 0.5)
            # I've created a grid in excel with a size of 20, 20 to investigate why this simple calculation works
            origin[0] = self.pixel_size*(column - self.resolution[0] / 2 + 0.5)
            origin[1] = self.pixel_size*(self.resolution[1] / 2 - row - 0.5)
            origin[2] = 100.0  # see article, there's a calculation that includes a FOV component

            yield (Ray(origin=origin, direction=(0.0, 0.0, -1.0)), (column,
                                                                    row))

    def __iter__(self):
        for row in range(self.resolution[1]):
            yield self.iter_row(row)


class World(object):
    def __init__(self):
        self.viewplane = ViewPlane(resolution=(640, 480), pixel_size=1.0)
        self.background_color = (0.0, 0.0, 0.0)
        self.sphere = Sphere(center=(0.0, 0.0, 0.0), radius=20.0)

    def render(self):
        pygame.display.init()
        window = pygame.display.set_mode(self.viewplane.resolution)

        pxarray = pygame.PixelArray(window)

        tracer = Tracer(self)

        start_time = time.time()

        for row in self.viewplane:
            for ray, pixel in row:
                color = tracer.trace_ray(ray)
                pxarray[pixel[0]][pixel[1]] = (int(color[0]*255),
                                               int(color[1]*255),
                                               int(color[2]*255))

        pygame.display.flip()

        print("Rendering is ready... it took %s seconds" % str(round(time.time() - start_time, 2)))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit(0)
                    print("I've hit the quit button")


w = World()
w.render()
