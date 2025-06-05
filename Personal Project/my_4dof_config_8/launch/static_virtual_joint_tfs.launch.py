from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_static_virtual_joint_tfs_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("my_4dof_arm", package_name="my_4dof_config_8").to_moveit_configs()
    return generate_static_virtual_joint_tfs_launch(moveit_config)
