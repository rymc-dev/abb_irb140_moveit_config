import os

from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("abb_irb140", package_name="abb_irb140_moveit_config").to_moveit_configs()

    # sensors_3d.yaml's PointCloudOctomapUpdater/DepthImageOctomapUpdater
    # plugins only build the octomap live from a running camera; there's no
    # MoveIt launch-time option to pre-load a built octree, so a pre-built
    # map (e.g. abb_irb140_description's maps/robot_lab_sim.bt, captured
    # from the wrist camera) has to be pushed into the planning scene via
    # move_group's `load_map` service (moveit_msgs/srv/LoadMap) after it
    # comes up -- see scripts/load_static_octomap.py.
    declare_load_octomap = DeclareLaunchArgument(
        'load_octomap',
        default_value='true',
        description="Load octomap_file into move_group's planning scene via the load_map service on startup",
    )
    declare_octomap_file = DeclareLaunchArgument(
        'octomap_file',
        default_value=os.path.join(
            get_package_share_directory('abb_irb140_description'), 'maps', 'robot_lab_sim.bt'
        ),
        description=(
            'Pre-built octree to load for planning (load_octomap:=true only). '
            "Must be the binary .bt octree -- MoveIt's OccupancyMapMonitor "
            "can't read the .ot format."
        ),
    )

    # Move Group Node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"trajectory_execution.allowed_execution_duration_scaling": 2.0,},
            {"publish_robot_description_semantic": True},
            {"use_sim_time": True},
        ],
    )

    # Waits for move_group's load_map service and calls it once; harmless to
    # leave running alongside move_group_node above since it exits right
    # after the call.
    static_octomap_loader_node = Node(
        package="abb_irb140_moveit_config",
        executable="load_static_octomap.py",
        output="screen",
        parameters=[{"octomap_path": LaunchConfiguration('octomap_file')}],
        condition=IfCondition(LaunchConfiguration('load_octomap')),
    )

    return LaunchDescription([
        declare_load_octomap,
        declare_octomap_file,
        move_group_node,
        static_octomap_loader_node,
    ])