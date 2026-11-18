"""Guard the new-task boundary across collection, training and evaluation."""
import ast
from pathlib import Path
import unittest
import yaml
from scripts.eval.eval_mujoco import parse_args

ROOT = Path(__file__).resolve().parents[1]


class RedCubeDefaults(unittest.TestCase):
    def test_collection_and_deploy_share_new_dataset(self):
        for name in ('collect_data', 'collect_batch', 'collect_manual', 'deploy_act'):
            cfg = yaml.safe_load((ROOT / f'configs/{name}.yaml').read_text())
            self.assertEqual(cfg.get('root', cfg.get('dataset_root')), './data/red_cube_blue_box')
            self.assertEqual(cfg.get('repo_name', cfg.get('dataset_repo_id')), 'local/so101_red_cube_blue_box')
            self.assertEqual(cfg['pick_body_name'], 'body_obj_block_1')
            self.assertEqual(cfg.get('task_name', cfg.get('task')), 'Pick up the red cube and place it in the blue box.')
        self.assertEqual(cfg['checkpoint'], './checkpoints/act_red_cube_blue_box')

    def test_python_defaults_do_not_use_legacy_data(self):
        for name in ('collect/manual_collect_data.py', 'collect/batch_collect_data.py',
                     'deploy/deploy_act.py', 'train/train_act.py'):
            tree = ast.parse((ROOT / 'scripts' / name).read_text())
            values = {node.value for node in ast.walk(tree)
                      if isinstance(node, ast.Constant) and isinstance(node.value, str)}
            self.assertFalse(values & {'demo_data_so101', 'so101_pnp', 'act_y', 'BrianMIR1/EE5108_batch_sim'})
            self.assertIn('red_cube_blue_box', values)
            self.assertIn('local/so101_red_cube_blue_box', values)

    def test_unified_evaluation_targets_red_cube(self):
        cfg = parse_args(['--policy', 'act', '--checkpoint', '/tmp/missing-model',
                          '--dataset-root', '/tmp/missing-data', '--dry-run'])
        self.assertEqual(cfg.pick_body_name, 'body_obj_block_1')
        self.assertEqual(cfg.task, 'Pick up the red cube and place it in the blue box.')
        self.assertEqual(cfg.spawn_min_dist, 0.04)
        self.assertEqual(cfg.spawn_x_max, 0.27)
