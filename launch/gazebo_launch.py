import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_path = get_package_share_directory('mobile_robot')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')
    yaml_path = os.path.join(pkg_path, 'config', 'bridge_config.yaml')

    urdf_file = os.path.join(
        pkg_path,
        'urdf',
        'mobile_robot.urdf'
    )

    model_sdf = os.path.join(
        pkg_path,
        'models',
        'mobile_robot',
        'model.sdf'
    )

    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    world = LaunchConfiguration('world')

    # Declare launch arguments
    declare_x_position_cmd = DeclareLaunchArgument(
        'x_pose',
        default_value='-2.0',
        description='X position of the robot'
    )

    declare_y_position_cmd = DeclareLaunchArgument(
        'y_pose',
        default_value='-0.5',
        description='Y position of the robot'
    )

    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value='empty_world.world',
        description='Gazebo world file'
    )

    world_path = PathJoinSubstitution([
        get_package_share_directory('turtlebot3_gazebo'),
        'worlds',
        world
    ])

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r -s -v2 ', world_path], 'on_exit_shutdown': 'true'}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-g -v2 '}.items()
    )

    start_gazebo_ros_spawner_cmd = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'mobile_robot',
            '-file', model_sdf,
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.5',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '3.142'
        ],
        output='screen',
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {
                'robot_description':
                    open(urdf_file).read()
            }
        ],
        output='screen'
    )

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={yaml_path}',
        ],
        output='screen'
    )

    ros_gz_image = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=[
            '/camera/image',
            '/camera/depth_image',
        ],
        output='screen'
    )

    set_env_vars_resources = AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.dirname(pkg_path)
    )


    return LaunchDescription([
        set_env_vars_resources,
        declare_x_position_cmd,
        declare_y_position_cmd,
        declare_world_cmd,

        gzclient_cmd,
        gzserver_cmd,

        robot_state_publisher,
        start_gazebo_ros_spawner_cmd,
        ros_gz_bridge,
        ros_gz_image
    ])

