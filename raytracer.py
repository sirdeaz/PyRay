import pygame
import numpy
import sys
import time
import math


class Shape(object):
    def hit(self, ray):
        return None


class Sphere(Shape):
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


class Plane(Shape):
    def __init__(self, center, normal):
        self.center = numpy.array(center)
        self.normal = numpy.array(normal)

    def hit(self, ray):
        denominator = numpy.dot(self.normal, ray.direction)

        if abs(denominator) > 0.0001:
            t = numpy.dot(self.center - ray.origin, self.normal) / denominator

            if (t > 0.0001):
                hit_point = ray.origin + t * ray.direction
                normal = None  # todo: not sure what to do with this?

                return ShadeRecord(normal=normal, hit_point=hit_point)

        return None


class Box(Shape):
    def hit(self, ray):
        return None


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
        shapes = self.world.shapes

        for shape in shapes:
            if shape.hit(ray):
                return (1.0, 0.0, 0.0)

        return (0.0, 0.0, 0.0)


class ViewPlane(object):
    'Interesting article at https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-generating-camera-rays/generating-camera-rays'

    def __init__(self, resolution, pixel_size):
        self.resolution = resolution
        self.pixel_size = pixel_size

    def iter_row(self, row):
        for column in range(self.resolution[0]):
            origin = numpy.zeros(3)
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
        # self.shapes = [Sphere(center=(0.0, 0.0, 0.0), radius=20.0),
        #                Sphere(center=(-100.0, 150.0, 0.0), radius=100.0),
        #                Sphere(center=(200.0, -50.0, 0.0), radius=80.0),
        #                Plane(center=(0.0, 0.0, 0.0), normal=(0.0, 1.0, 0.0))]

        self.shapes = [Plane(center=(10.0, 10.0, 10.0), normal=(0.0, 1.0, 1.0))]

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


w = World()
w.render()
