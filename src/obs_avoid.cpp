#include <vector>
#include <cmath>
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

class ObstacleAvoidance : public rclcpp::Node
{
public:
    ObstacleAvoidance() : Node("obs_avoid")
    {
        timer_cb_grp_ = create_callback_group(rclcpp::CallbackGroupType::Reentrant);
        sub_options_.callback_group = nullptr;
        publisher_ = create_publisher<geometry_msgs::msg::Twist>(
                "/cmd_vel", 
                10);
        
        lidar_sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
                "/scan", 
                10, 
                std::bind(&ObstacleAvoidance::scan_callback, 
                    this, 
                    std::placeholders::_1), 
                sub_options_);

        timer_ = create_wall_timer(
                std::chrono::milliseconds(100),
                std::bind(&ObstacleAvoidance::movebot, this),
                timer_cb_grp_);
    }
    
    void scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
    {
        ranges = msg->ranges;
        for (int i = 0,j = 9; i < 3 && j < 12; i++,j++)
        {
            float sum1 = 0.0, sum2 = 0.0;
            float count1 = 0.0, count2 = 0.0;
            for (int k = i*30,l = j*30; 
                    k < (i+1)*30 && l < (j+1)*30; 
                    k++,l++)
            {
                if (std::isfinite(ranges[k]))
                {
                    sum1 += std::round(ranges[k]*100)/100.0;
                    count1++;
                }

                if (std::isfinite(ranges[l]))
                {
                    sum2 += std::round(ranges[l]*100)/100.0;
                    count2++;
                }
            }           
            if (count1 > 0.0)
                avg_scan[i] = sum1 / count1;
            else
                avg_scan[i] = 0.0;

            if (count2 > 0.0)
                avg_scan[j - 6] = sum2 / count2;
            else
                avg_scan[j - 6] = 0.0;
        }
        RCLCPP_INFO(get_logger(), "Scan Updated");
    }

    void movebot()
    {
        geometry_msgs::msg::Twist msg;
        
        float left  = (avg_scan[2] + avg_scan[1])/2.0 > 0.0 ? (avg_scan[2] + avg_scan[1])/2.0 : 3.5;
        float right = (avg_scan[3] + avg_scan[4])/2.0 > 0.0 ? (avg_scan[3] + avg_scan[4])/2.0 : 3.5;
        std::array<float, 4> values = {
            avg_scan[0],
            avg_scan[1],
            avg_scan[4],
            avg_scan[5]
        };

        float sum = 0.0;
        int count = 0;

        for (float value : values)
        {
            if (value != 0.0f)
            {
                sum += value;
                count++;
            }
        }

        float front = count > 0 ? sum / count : 3.5;


        const float front_obstacle_dist = 1.0;
        const float side_obstacle_dist = 0.5;

        if (front < front_obstacle_dist)
        {
            msg.linear.x = 0.0;

            if (left < side_obstacle_dist && right < side_obstacle_dist)
                msg.linear.x = -0.15;
            else if (left > right)
                msg.angular.z = 1.2;
            else
                msg.angular.z = -1.2;
        }
        else
        {
            msg.linear.x = 0.15;

            if (left < side_obstacle_dist)
            {
                msg.angular.z = -1.2;
            }
            else if (right < side_obstacle_dist)
            {
                msg.angular.z = 1.2;
            }
            else
            {
                msg.angular.z = 0.0;
            }
        }
        publisher_->publish(msg);
        RCLCPP_INFO(get_logger(), "Sending velocity commands linear=%f angular=%f", msg.linear.x, msg.angular.z);
    }

private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr lidar_sub_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::SubscriptionOptions sub_options_;
    rclcpp::CallbackGroup::SharedPtr timer_cb_grp_;
    std::vector<float> ranges;
    std::array<float, 6> avg_scan = {0,0,0,0,0,0};
};

int main(int argc, char* argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ObstacleAvoidance>();

    rclcpp::executors::MultiThreadedExecutor executor;    
    executor.add_node(node);

    executor.spin();
    
    rclcpp::shutdown();
    return 0;
}
