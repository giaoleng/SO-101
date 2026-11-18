import math
from pathlib import Path
import unittest

import mujoco
import numpy as np
from mujoco_env.task_geometry import bin_placement_geometry

ROOT = Path(__file__).resolve().parents[1]


class TestTaskGeometry(unittest.TestCase):
    def setUp(self):
        self.model = mujoco.MjModel.from_xml_path(str(ROOT / 'asset/scene_so101_y.xml'))
        self.data = mujoco.MjData(self.model)
        self.body = self.model.body('body_obj_block_1')
        self.adr = int(self.model.jnt_qposadr[int(self.body.jntadr[0])])

    def place(self, x=0, y=0, z=0.0245, yaw=0):
        origin = self.model.body('body_obj_bin').pos
        self.data.qpos[self.adr:self.adr + 3] = origin + [x, y, z]
        self.data.qpos[self.adr + 3:self.adr + 7] = [math.cos(yaw/2), 0, 0, math.sin(yaw/2)]
        mujoco.mj_forward(self.model, self.data)
        return bin_placement_geometry(self.model, self.data, 'body_obj_block_1', 'body_obj_bin')

    def test_resting_inside(self):
        xy, z, rim = self.place()
        self.assertTrue(xy and z)
        self.assertAlmostEqual(rim, 0.8305)

    def test_corner_crossing_wall(self):
        self.assertTrue(self.place(x=0.032)[0])
        self.assertFalse(self.place(x=0.04)[0])
        self.assertFalse(self.place(x=0.032, yaw=math.pi/4)[0])

    def test_not_placed(self):
        self.assertFalse(self.place(z=0.06)[1])  # above rim
        self.assertFalse(self.place(z=0.01)[1])  # through floor
        self.assertFalse(self.place(x=0.15)[0])  # outside box

    def test_colors_and_capacity(self):
        target_geom = int(self.body.geomadr[0])
        self.assertGreater(self.model.geom_rgba[target_geom, 0], self.model.geom_rgba[target_geom, 2])
        for name in ('bin_floor', 'bin_wall_x_pos', 'bin_wall_x_neg', 'bin_wall_y_pos', 'bin_wall_y_neg'):
            rgba = self.model.geom(name).rgba
            self.assertGreater(rgba[2], rgba[0])
        self.assertTrue(self.place()[0])

class TestSuccessGates(unittest.TestCase):
    setUp = TestTaskGeometry.setUp
    place = TestTaskGeometry.place

    def test_release_lift_and_contact_gates(self):
        from types import SimpleNamespace
        from mujoco_env.y_env import SimpleEnv
        self.place()
        site_id = self.model.site('gripperframe').id
        self.data.site_xpos[site_id, 2] = 1.0
        contacts = [('body_obj_block_1', 'body_obj_bin')]
        positions = lambda name: self.data.xpos[self.model.body(name).id]
        env = SimpleEnv.__new__(SimpleEnv)
        env.env = SimpleNamespace(model=self.model, data=self.data,
                                  get_p_body=positions,
                                  get_contact_body_names=lambda: contacts)
        env.pick_body_name = 'body_obj_block_1'
        env.place_body_name = 'body_obj_bin'
        env.success_height_threshold = None
        env._target_was_lifted = True
        env._target_rest_height = 0.8125
        env._lift_height_delta = 0.035
        env._is_gripper_open = lambda threshold: True
        self.assertTrue(env.check_success())
        env._target_was_lifted = False
        self.assertFalse(env.check_success())
        env._target_was_lifted = True
        contacts.clear()
        self.assertFalse(env.check_success())
        contacts.extend([('body_obj_block_1', 'body_obj_bin'), ('body_obj_block_1', 'gripper')])
        self.assertFalse(env.check_success())
        contacts.pop()
        env._is_gripper_open = lambda threshold: False
        self.assertFalse(env.check_success())
        env._is_gripper_open = lambda threshold: True
        self.data.site_xpos[site_id, 2] = 0.82
        self.assertFalse(env.check_success())

    def test_physical_floor_support(self):
        self.place(z=0.045)
        for _ in range(500):
            mujoco.mj_step(self.model, self.data)
        xy, z, _ = bin_placement_geometry(self.model, self.data, 'body_obj_block_1', 'body_obj_bin')
        self.assertTrue(xy and z)
        target = self.body.id
        box = self.model.body('body_obj_bin').id
        pairs = [(self.model.geom_bodyid[c.geom1], self.model.geom_bodyid[c.geom2])
                 for c in self.data.contact]
        self.assertTrue(any(set(pair) == {target, box} for pair in pairs))


if __name__ == '__main__':
    unittest.main()
