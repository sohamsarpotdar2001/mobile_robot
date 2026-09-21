# Simulation of mobile robot in Gazebo

A ROS 2 & Gazebo simulation package for a differential-drive mobile robot. This repository contains the complete robot description (URDF/Xacro), kinematic modeling, sensor integration, obstacle avoidance, and teleoperation control setups.

---

## 🛠️ Prerequisites & Dependencies

### System Requirements
* **OS:** Ubuntu 22.04 LTS (or Ubuntu 24.04 LTS)
* **ROS 2:** Jazzy Jalisco
* **Simulator:** Gazebo Harmonic

### Required ROS 2 Packages
Run the following command to install required ROS 2 dependencies (replace `<ros-distro>` with `jazzy`):

```bash
sudo apt update && sudo apt install -y \
  ros-<ros-distro>-robot-state-publisher \
  ros-<ros-distro>-joint-state-publisher \
  ros-<ros-distro>-rviz2 \
  ros-<ros-distro>-turtlebot3-simulations \
  ros-<ros-distro>-turtlebot3* \
  ros-<ros-distro>-ros-gz \
  ros-<ros-distro>-navigation2 \
  ros-<ros-distro>-nav2-bringup
```
