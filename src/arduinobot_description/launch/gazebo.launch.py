from launch import LaunchDescription
from pathlib import Path

from launch_ros.actions import Node
from launch.actions import (
    DeclareLaunchArgument,
    SetEnvironmentVariable,
    IncludeLaunchDescription
)

from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

import os

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    arduinobot_description_dir = get_package_share_directory(
        "arduinobot_description"
    )

    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(
            arduinobot_description_dir,
            "urdf",
            "arduinobot.urdf.xacro"
        ),
        description="Absolute path to robot urdf file"
    )

    robot_description = ParameterValue(
        Command([
            "xacro ",
            LaunchConfiguration("model")
        ]),
        value_type=str
    )

    gazebo_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[
            str(Path(arduinobot_description_dir).parent.resolve())
        ]
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True
            }
        ]
    )

    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui"
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            )
        ),
        launch_arguments={
            "gz_args": "-v 4 -r empty.sdf"
        }.items()
    )

    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-name", "arduinobot"
        ]
    )

    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock]",
            "/image_raw@sensor_msgs/msg/Image@gz.msgs.Image",
            "/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo"       
            ]
    )


    return LaunchDescription([
        model_arg,
        gazebo_resource_path,
        robot_state_publisher,
        joint_state_publisher_gui,
        gazebo,
        gz_spawn_entity,
        gz_ros2_bridge
    ])