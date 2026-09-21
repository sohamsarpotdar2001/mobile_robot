#include <vector>
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

class ScanPub : public rclcpp::Node
{
public:
    ScanPub() : Node("scan_pub")
    {
        lidar_sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
                "/scan", 
                10, 
                std::bind(&ScanPub::scan_callback, 
                    this, 
                    std::placeholders::_1));
    }
    
    void scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
    {
        ranges = msg->ranges;
        unsigned int i = 0;
        while (i != ranges.size())
        {
            RCLCPP_INFO(get_logger(), "value=%.3f counter=%d", ranges[i], i);
            i += 1;
        }
        RCLCPP_INFO(get_logger(), "End of scan. Got %ld values", ranges.size());
    }

private:
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr lidar_sub_;
    std::vector<float> ranges;
};


int main(int argc, char* argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ScanPub>();

    rclcpp::spin(node);
    
    rclcpp::shutdown();
    return 0;
}
