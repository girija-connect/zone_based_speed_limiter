from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    config = os.path.join(
        get_package_share_directory('speed_limiter'),
        'config',
        'speed_zone.yaml'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([

        DeclareLaunchArgument('use_sim_time', default_value='true'),

        Node(
            package='speed_limiter',
            executable='speed_limiter',
            name='speed_limiter',
            output='screen',
            parameters=[config, {'use_sim_time': use_sim_time}]
        )

    ])