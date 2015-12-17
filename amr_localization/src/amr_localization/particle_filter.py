#!/usr/bin/env python

PACKAGE = 'amr_localization'
NODE = 'particle_filter'

import roslib
roslib.load_manifest(PACKAGE)
import copy
import rospy
import math
import random
from amr_localization.motion_model import MotionModel
from amr_localization.pose import Pose
from amr_localization.particle import Particle
from amr_localization.random_particle_generator import RandomParticleGenerator

class ParticleFilter:

    def __init__(self, map_min_x, map_max_x, map_min_y, map_max_y, weigh_particles_callback):
        self.weigh_particles_callback = weigh_particles_callback
        self.particle_set_size = 100
        self.random_particles_size = 10
        self.motion_model = MotionModel(0.02, 0.01)
        self.random_particle_generator = RandomParticleGenerator(map_min_x, map_max_x, map_min_y, map_max_y)
        self.pose_estimate = Pose()
        self._num_sample_per_draw = 8

        self.particles = []
        for i in range(self.particle_set_size):
            self.particles.append(self.random_particle_generator.generate_particle())


    def update(self, x, y, yaw):
        '''
        ============================== YOUR CODE HERE ==============================
         Instructions: do one complete update of the particle filter. It should
                       generate new particle set based on the given motion
                       parameters and the old particle set, compute the weights of
                       the particles, resample the set, and update the private
                       member field that holds the current best pose estimate
                       (self.pose_estimate). Note that the motion parameters provided
                       to this function are in robot's reference frame.

         Hint: Check motion_model.py for documentation and example how to use it
               for the particle pose update.
               x, y, yaw -- are the odometry update of the robot's pose (increments)


         Remark: to compute the weight of particles, use the weigh_particles_callback member
                 field:

                     weights = self.weigh_particles_callback(particles_list)

         Remark: to generate a comletely random particle use the provided
                 random_particle_generator object:

                     particle = self.random_particle_generator.generate_particle()

         Finally  the best pose estimate and assign it to the corresponding member field
         for visualization:
                     self.pose_estimate = selected_particle.pose
        ============================================================================
        '''
        # apply motion model to particles
        self.motion_model.setMotion(x, y, yaw)
        for particle in self.particles:
            particle.pose = self.motion_model.sample(particle.pose)

        # calculate and update acuumulated weights of particles (creating the roulette)
        weights = self.weigh_particles_callback(self.particles)
        self._weight_mean = sum(weights) / len(weights)
        accumulated_weight = 0.0
        accumulated_weight_list = []
        for i in range(self.particle_set_size):
            self.particles[i].weight = weights[i]
            accumulated_weight = accumulated_weight + weights[i]
            accumulated_weight_list.append(accumulated_weight)
        # normalize weights
        for i in range(self.particle_set_size):
            accumulated_weight_list[i] = accumulated_weight_list[i] * 1.0 / accumulated_weight_list[-1]

        # resample particles:
        self.particles = self._resample(accumulated_weight_list)
#        for i in range(self.particle_set_size):
#            self.particles[i].weight = 1.0

        # set pose_estimate
        self.pose_estimate = self._cal_pose_estimate()


    def _cal_pose_estimate(self):
        """ return the particle with the weight closest to _weight_mean """
        estimate = None
        min_weight_diff = 1.0
        for particle in self.particles:
            weight_diff = abs(particle.weight - self._weight_mean)
            if weight_diff < min_weight_diff:
                estimate = particle
                min_weight_diff = weight_diff
#        max_weight = 0.0
#        for particle in self.particles:
#            if particle.weight > max_weight:
#                estimate = particle
#                max_weight = particle.weight
        return estimate.pose


    def _resample(self, accumulated_weight_list):
        new_particles = []
        random.seed()

        # stochasticly draw from old sample set.
        stochastic_increment = 1.0 / self._num_sample_per_draw
        num_draw_old_set = self.particle_set_size - self.random_particles_size

        # stochastic draw logic
        while len(new_particles) + self._num_sample_per_draw <= num_draw_old_set:
            random_num = random.random()
            random_weight = random_num
            for i in range(self._num_sample_per_draw):
                random_weight = random_num + i * stochastic_increment
                if random_weight > 1.0:
                    random_weight = random_weight - 1.0
                # find and append particle with the generated weight
                found_index = self._find_particle(random_weight)
                new_particles.append(copy.deepcopy(self.particles[found_index]))
        # stochastic draw logic for the remaining particles
        random_num = random.random()
        random_weight = random_num
        for i in range(num_draw_old_set - len(new_particles)):
            random_weight = random_num + i * stochastic_increment
            if random_weight > 1.0:
                random_weight = random_weight - 1.0
            # find and append particle with the generated weight
            found_index = self._find_particle(random_weight)
            new_particles.append(self.particles[found_index])

        # add uniformly distributed random particles
        for i in range(self.random_particles_size):
            new_particles.append(self.random_particle_generator.generate_particle())

        return new_particles


    def _find_particle(self, weight):
        """
        return index of particle matching the accumulated weight value
        expects particles' weights to be increasing through the whole list
        """
        # weight out of range
        if (weight < self.particles[0].weight
                or weight > self.particles[self.particle_set_size - 1].weight):
            return -1
        elif weight <= self.particles[0].weight:
            # recursive function does not check this case
            return 0
        else:
            return self._find_particle_re(weight, self.particle_set_size - 1, 0)


    def _find_particle_re(self, weight, upper_index, lower_index):
        """ recursively search for weight """
        mid_index = int((upper_index + lower_index) / 2)
        # terminal condition - equal weight
        if weight > self.particles[upper_index].weight:
            return upper_index
        # terminal condition - convergence of indices
        if upper_index == lower_index + 1 or upper_index == lower_index:
            return upper_index
        # recursive call
        if weight > self.particles[mid_index].weight:
            return self._find_particle_re(weight, upper_index, mid_index)
        else:
            return self._find_particle_re(weight, mid_index, lower_index)


    def get_particles(self):
        return self.particles

    def get_pose_estimate(self):
        return self.pose_estimate

    def set_external_pose_estimate(self, pose):
        self.random_particle_generator.set_bias(pose, 0.5, 500)