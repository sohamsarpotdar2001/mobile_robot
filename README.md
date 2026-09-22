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
  ```
  python3 add_collisions.py robot.urdf
  ```

---

## URDF Plugins
Add plugins for sensors and robot controller
Refer these for syntax - 
* https://github.com/maponarooo/URDF-Gazebo-Harmonic-sensors
* https://medium.com/@alitekes1/gazebo-sim-plugin-and-sensors-for-acquire-data-from-simulation-environment-681d8e2ad853

Also, take a look at `urdf/mobile_robot.urdf` in the repo.