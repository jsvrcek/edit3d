#!/usr/bin/env python3
# Copyright 2004-present Facebook. All Rights Reserved.

import numpy as np
from scipy.spatial import cKDTree as KDTree
import trimesh


def compute_trimesh_chamfer(gt_points, gen_mesh, num_mesh_samples=30000):
    """
    This function computes a symmetric chamfer distance, i.e. the sum of both chamfers.

    gt_points: trimesh.points.PointCloud of just poins, sampled from the surface (see
               compute_metrics.ply for more documentation)

    gen_mesh: trimesh.base.Trimesh of output mesh from whichever autoencoding reconstruction
              method (see compute_metrics.py for more)

    """
    # only need numpy array of points
    gt_points_np = gt_points.vertices
    mesh_max = np.amax(gt_points_np, axis=0)
    mesh_min = np.amin(gt_points_np, axis=0)
    mesh_center = (mesh_max + mesh_min) / 2
    max_dist = np.sqrt(np.max(np.sum(gt_points_np ** 2, axis=-1)))
    mesh_scale = 1.0 / max_dist

    gen_points_sampled = trimesh.sample.sample_surface(gen_mesh, num_mesh_samples)[0]
    gen_points_sampled[:, 1] *= -1
    gen_points_sampled = gen_points_sampled / mesh_scale + mesh_center

    # one direction
    gen_points_kd_tree = KDTree(gen_points_sampled)
    one_distances, one_vertex_ids = gen_points_kd_tree.query(gt_points_np)
    gt_to_gen_chamfer = np.mean(np.square(one_distances))

    # other direction
    gt_points_kd_tree = KDTree(gt_points_np)
    two_distances, two_vertex_ids = gt_points_kd_tree.query(gen_points_sampled)
    gen_to_gt_chamfer = np.mean(np.square(two_distances))

    return gt_to_gen_chamfer + gen_to_gt_chamfer
