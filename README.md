# Simulation of mobile robot in Gazebo

A ROS 2 & Gazebo simulation package for a differential-drive mobile robot. This repository contains the complete robot description (URDF/Xacro), kinematic modeling, sensor integration, obstacle avoidance, and teleoperation control setups.

---

## Prerequisites & Dependencies

### System Tested with
* **OS:** Ubuntu 22.04 LTS (or Ubuntu 24.04 LTS)
* **ROS 2:** Jazzy Jalisco
* **Simulator:** Gazebo Harmonic

### Required Packages

[//]: # (Get latest ROS 2 version link)

Install [ROS 2](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html) and [Colcon](https://colcon.readthedocs.io/en/released/user/installation.html)

Run the following command to install required ROS 2 dependencies:

```bash
sudo apt update && sudo apt install -y \
  ros-$ROS_DISTRO-robot-state-publisher \
  ros-$ROS_DISTRO-joint-state-publisher \
  ros-$ROS_DISTRO-rviz2 \
  ros-$ROS_DISTRO-turtlebot3-simulations \
  ros-$ROS_DISTRO-turtlebot3* \
  ros-$ROS_DISTRO-ros-gz \
  ros-$ROS_DISTRO-navigation2 \
  ros-$ROS_DISTRO-nav2-bringup
```

---

## CAD to URDF
* Login to [Onshape](https://www.onshape.com/en/) and create a robot model.
* Make every part in a seperate Part Studio and import them later in the Assembly.
* Avoid using sub-assemblies in the final robot assembly. Sub-assemblies are exported with all its contained meshes instead of one single part, so the urdf file includes them as seperate links.
  * To make a single part from an assembly, open the part studio and use `Union` or `Boolean` functions to fuse all the parts into one single part.
* Rename every joint according to the link names.
* Export the assembly as URDF. Meshes type - STL(Binary)
* Extract the `meshes` and `urdf` directories.

> Onshape's URDF exporter does not add collision tags to the extracted links. Do it manually using the `add_collisions.py` script.
> ```
> python3 add_collisions.py robot.urdf robot_with_collisions.urdf
> ```

---

## URDF Plugins
Add plugins for sensors and robot controller
Refer these for syntax - 
* https://github.com/maponarooo/URDF-Gazebo-Harmonic-sensors
* https://medium.com/@alitekes1/gazebo-sim-plugin-and-sensors-for-acquire-data-from-simulation-environment-681d8e2ad853

Also, take a look at `urdf/mobile_robot.urdf` in the repo.

---

## Launch setup
Setup ROS 2 workspace
```
cd $HOME
mkdir -p ros2_ws/src; cd ros2_ws/src
git clone https://github.com/sohamsarpotdar2001/mobile_robot.git
```

Copy your `robot_with_collisions.urdf` file to `mobile_robot/urdf/` directory.
Edit the `launch/assembly_launch.py` file to replace the line 13 with `robot_with_collisions.urdf` name.

Build the workspace
```
cd ~/ros2_ws
colcon build --packages-select mobile_robot
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

Launch the robot
```
ros2 launch mobile_robot assembly_launch.py
```

---

## Gazebo Simulation

### Create SDF from URDF
Move your robot meshes to the repo
```
mv ~/meshes/* ~/ros2_ws/src/mobile_robot/meshes
```

Generate SDF
```
cd ~/ros2_ws/src/mobile_robot/urdf
gz sdf robot_with_collisions.urdf robot.sdf
```

Move sdf file to `models` directory of the repo.
```
cd ~/ros2_ws/src/mobile_robot/models
mkdir robot
mv ../urdf/robot.sdf robot/model.sdf
```

Copy `model.config` from mobile_robot to robot direectory
```
cp models/mobile_robot/model.config models/robot/model.config
```
Edit `model.config` to change the name of the model to `robot`

Inspect the generated SDF
```
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:~/ros2_ws/install/mobile_robot/share/
cd mobile_robot/models/robot
gz sim model.sdf
```

Check if all the links and joints are positioned properly. Look at the collision geometries by right-clicking the model -> View -> collisions.
Edit the sdf file accordingly if needed.

### Gazebo launch file
Edit the `launch/gazebo_launch.py` file to change the `urdf_file` and `model_path` variables.
If your robot does not have a camera, remove the `ros_gz_image` variable.

Edit the `config/bridge_config.yaml` file to change the topics according to the plugins configured in urdf file.

Launch the robot in gazebo
```
colcon build --packages-select mobile_robot
ros2 launch mobile_robot gazebo_launch.py
```