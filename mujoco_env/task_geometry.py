"""Placement detector for the SO100/SO101 obj_bin.xml scene contract only.

Requires named floor/four axis-aligned walls and a single box pick geom.
Unsupported scenes raise; OMY uses its separate SimpleEnv success branch.
"""
import numpy as np


def bin_placement_geometry(model, data, pick_body_name, place_body_name):
    """Return full-footprint containment, floor placement, and world rim height.

    The cube may protrude above this shallow tray. Its bottom must rest on the
    floor, its centre must be below the rim, and every corner must clear walls.
    Contact/release/lift-history checks belong to SimpleEnv.check_success.
    """
    bin_id = model.body(place_body_name).id
    rotation = data.xmat[bin_id].reshape(3, 3)
    origin = data.xpos[bin_id]
    floor = model.geom('bin_floor')
    walls = [model.geom(name) for name in (
        'bin_wall_x_pos', 'bin_wall_x_neg', 'bin_wall_y_pos', 'bin_wall_y_neg')]
    if any(int(g.bodyid[0]) != bin_id for g in [floor, *walls]):
        raise ValueError('Box collision geoms must belong to the place body')
    # Geoms are axis-aligned in the box frame; fail clearly if this changes.
    if any(not np.allclose(g.quat, [1, 0, 0, 0]) for g in [floor, *walls]):
        raise ValueError('Box collision geoms must be axis-aligned in the box frame')
    xp, xn, yp, yn = walls
    lo = np.array([xn.pos[0] + xn.size[0], yn.pos[1] + yn.size[1]])
    hi = np.array([xp.pos[0] - xp.size[0], yp.pos[1] - yp.size[1]])
    floor_top = float(floor.pos[2] + floor.size[2])
    rim = min(float(g.pos[2] + g.size[2]) for g in walls)
    pick_id = model.body(pick_body_name).id
    start, count = int(model.body_geomadr[pick_id]), int(model.body_geomnum[pick_id])
    if count != 1 or int(model.geom_type[start]) != 6:  # mjGEOM_BOX
        raise ValueError('Pick object must have exactly one box geom')
    center = rotation.T @ (data.geom_xpos[start] - origin)
    relative_rotation = rotation.T @ data.geom_xmat[start].reshape(3, 3)
    extent = np.abs(relative_rotation) @ model.geom_size[start]
    xy_ok = bool(np.all(center[:2] - extent[:2] > lo) and
                 np.all(center[:2] + extent[:2] < hi))
    # 2 mm permits contact-solver penetration, not floating above the floor.
    contact_tolerance = 0.002 + float(model.geom_margin[start])
    z_ok = bool(abs(center[2] - extent[2] - floor_top) <= contact_tolerance
                and center[2] < rim)
    rim_world_z = max(float(data.geom_xpos[g.id, 2] +
                          np.abs(data.geom_xmat[g.id].reshape(3, 3)[2]) @ g.size)
                      for g in walls)
    return xy_ok, z_ok, rim_world_z
