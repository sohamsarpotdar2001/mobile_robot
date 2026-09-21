import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, AppendEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # 1. Declare the argument for the URDF path
    urdf_file = PathJoinSubstitution([
        FindPackageShare('mobile_robot'),
        'urdf',
        'mobile_robot.urdf'
    ])

    robot_description = Command([
        'cat ',
        urdf_file
    ])

    # Robot State Publisher Node
    # Note: In ROS 2, the URDF is typically passed via the 'robot_description' parameter
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description
        }]
    )

    # Joint State Publisher GUI Node
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # Static Transform Publisher Node
    # Format: x y z qx qy qz qw frame_id child_frame_id
    # Note: ROS 2 static_transform_publisher uses quaternions for rotation
    map_to_root_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_root',
        arguments=['0', '0', '0', '0', '0', '0', '1', 'map', 'root']
    )

    # RViz Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        map_to_root_node,
        rviz_node,
    ])
