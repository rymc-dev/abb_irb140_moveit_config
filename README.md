# abb_irb140_moveit_config

MoveIt 2 configuration package for the **ABB IRB140** 6-DOF industrial arm with a pneumatic gripper. It holds the semantic robot description, kinematics, controller mapping and launch files that `move_group` needs to plan and execute motions for the arm. It was generated with the MoveIt Setup Assistant and then customised for a simulated pick-and-place workflow.

Built for **ROS 2 Jazzy**.

## What's inside

| Path | Purpose |
|------|---------|
| `config/abb_irb140.srdf` | Planning groups, named poses, end effector and virtual joint |
| `config/abb_irb140.urdf.xacro` | Wraps `abb_irb140_description` and adds the `ros2_control` tags |
| `config/abb_irb140.ros2_control.xacro` | `ros2_control` hardware interface (mock components by default) |
| `config/kinematics.yaml` | KDL IK solver for the arm |
| `config/moveit_controllers.yaml` | Maps MoveIt to `arm_controller` and `gripper_controller` |
| `config/joint_limits.yaml` | Joint velocity and acceleration limits |
| `config/pilz_cartesian_limits.yaml` | Cartesian limits for the Pilz industrial motion planner |
| `config/sensors_3d.yaml` | Octomap sensor config (live point-cloud updater is disabled) |
| `config/initial_positions.yaml` | Initial joint values for the mock hardware |
| `launch/` | Launch files (see below) |
| `scripts/load_static_octomap.py` | Loads a pre-built `.bt` octomap into the planning scene |

### Planning groups

- **`irb140_planning_group`**: the arm, a `base_link` → `tool0` chain (`joint_1`–`joint_6`)
- **`gripper_planning_group`**: the pneumatic gripper joints, attached to `tool0` as the `gripper` end effector

Named poses: `home_pose`, `random_pose` (arm), `open_gripper_pose`, `close_gripper_pose` (gripper).

### Controllers

| Controller | Type | Action namespace |
|-----------|------|------------------|
| `arm_controller` | `FollowJointTrajectory` | `follow_joint_trajectory` |
| `gripper_controller` | `GripperCommand` | `gripper_cmd` |

## Launch files

| Launch file | Description |
|-------------|-------------|
| `demo.launch.py` | Standalone demo: `move_group`, RViz and mock `ros2_control` hardware, no simulator needed |
| `move_group.launch.py` | `move_group` only, for use with an external simulator or the real robot |
| `moveit_rviz.launch.py` | RViz with the MoveIt Motion Planning plugin |
| `rsp.launch.py` | `robot_state_publisher` |
| `spawn_controllers.launch.py` | Spawns the `ros2_control` controllers |
| `static_virtual_joint_tfs.launch.py` | Static TF for the `world` → `base_link` virtual joint |
| `warehouse_db.launch.py` | MoveIt warehouse database (MongoDB) |
| `setup_assistant.launch.py` | Opens the MoveIt Setup Assistant on this package |

### `move_group.launch.py` arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `use_sim_time` | `true` | Use the simulation clock. Set to `false` on the real robot, where nothing publishes `/clock` |
| `load_octomap` | `true` | Load `octomap_file` into the planning scene at startup |
| `octomap_file` | `abb_irb140_description/maps/robot_lab_sim.bt` | Pre-built octree. It must be the binary `.bt` format, not `.ot` |

The launch file also relaxes `allowed_start_tolerance` to 0.5 and sets `allowed_execution_duration_scaling` to 2.0 to work around clock-sync issues seen in simulation. The reasoning is in the comments in `launch/move_group.launch.py`.

## Usage

Build the package and its dependencies in a ROS 2 workspace:

```bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -y
colcon build --packages-select abb_irb140_moveit_config
source install/setup.bash
```

Run the standalone demo with mock hardware:

```bash
ros2 launch abb_irb140_moveit_config demo.launch.py
```

Run only `move_group` alongside a simulator or the real robot:

```bash
ros2 launch abb_irb140_moveit_config move_group.launch.py use_sim_time:=true
```

## Dependencies

- `abb_irb140_description`: robot URDF/xacro, meshes and octomap maps
- MoveIt 2 (`moveit_ros_move_group`, `moveit_kinematics`, `moveit_planners`, `moveit_simple_controller_manager`, `moveit_ros_visualization`, `moveit_setup_assistant`, `moveit_configs_utils`)
- `ros2_control` / `controller_manager`, `robot_state_publisher`, `rviz2`, `xacro`, `tf2_ros`
- `warehouse_ros_mongo` (only for `warehouse_db.launch.py`)

## Related packages

This package is one piece of a larger IRB140 workspace:

- `abb_irb140_description`: robot model
- `abb_irb140_bringup`: top-level launch for Gazebo, MoveIt and perception
- `abb_irb140_motion_control`: MoveIt C++ motion-control and pick-and-place demos
- `abb_irb140_perception`: perception nodes

## License

BSD-3-Clause. See `package.xml`.

## Maintainer

Ryan McKee (<ryanmckee47@icloud.com>)
