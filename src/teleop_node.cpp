#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>

#include <iostream>
#include <termios.h>
#include <unistd.h>

class TeleopNode : public rclcpp::Node
{
public:
    TeleopNode()
    : Node("teleop_node")
    {
        publisher_ = this->create_publisher<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10);

        RCLCPP_INFO(this->get_logger(),
                    "\n"
                    "=============================\n"
                    "      Mobile Robot Teleop\n"
                    "=============================\n"
                    "   w : forward\n"
                    "   s : backward\n"
                    "   a : left\n"
                    "   d : right\n"
                    "   x : stop\n"
                    "   q : quit\n"
                    "=============================\n");

        // Read keyboard without requiring Enter
        struct termios settings;
        tcgetattr(STDIN_FILENO, &settings);

        original_settings_ = settings;

        settings.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &settings);
    }

    ~TeleopNode()
    {
        // Restore terminal settings
        tcsetattr(STDIN_FILENO, TCSANOW, &original_settings_);
    }

    void run()
    {
        while (rclcpp::ok())
        {
            char key;

            if (read(STDIN_FILENO, &key, 1) > 0)
            {
                geometry_msgs::msg::Twist cmd;

                switch (key)
                {
                    case 'w':
                        cmd.linear.x = 0.5;
                        cmd.angular.z = 0.0;
                        break;

                    case 's':
                        cmd.linear.x = -0.5;
                        cmd.angular.z = 0.0;
                        break;

                    case 'a':
                        cmd.linear.x = 0.0;
                        cmd.angular.z = 1.0;
                        break;

                    case 'd':
                        cmd.linear.x = 0.0;
                        cmd.angular.z = -1.0;
                        break;

                    case 'x':
                        cmd.linear.x = 0.0;
                        cmd.angular.z = 0.0;
                        break;

                    case 'q':
                    {
                        // Stop robot before exiting
                        cmd.linear.x = 0.0;
                        cmd.angular.z = 0.0;
                        publisher_->publish(cmd);

                        RCLCPP_INFO(this->get_logger(), "Teleop stopped.");
                        return;
                    }

                    default:
                        continue;
                }

                publisher_->publish(cmd);
            }
        }
    }

private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;

    struct termios original_settings_;
};


int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<TeleopNode>();

    node->run();

    rclcpp::shutdown();

    return 0;
}
