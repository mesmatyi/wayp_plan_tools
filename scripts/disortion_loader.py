import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import csv
import time
import os

class DistortionLoader(Node):
    def __init__(self):
        super().__init__('distortion_loader')
        
        self.steering_angle = 0.0
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscriber = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.listener_callback,
            10)
        
        csv_file_path = os.path.join(os.path.dirname(__file__), 'disortions/')
        self.declare_parameter('PRBS_33Hz_amp=010deg.csv', csv_file_path)
        self.declare_parameter('delay', 0.1)
        
    def listener_callback(self, msg):
        self.get_logger().info(f'Received command: linear={msg.linear.x}, angular={msg.angular.z}')
        
        steering_angle = msg.angular.z
        
    def load_and_publish(self):
        csv_file = self.get_parameter('csv_file').value
        delay = self.get_parameter('delay').value
        
        try:
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        twist = Twist()
                        twist.linear.x = float(row[0])
                        twist.angular.z = float(row[1]) if len(row) > 1 else 0.0
                        
                        self.publisher.publish(twist)
                        self.get_logger().info(f'Published: linear={twist.linear.x}, angular={twist.angular.z}')
                        time.sleep(delay)
        except FileNotFoundError:
            self.get_logger().error(f'CSV file not found: {csv_file}')

def main(args=None):
    rclpy.init(args=args)
    node = DistortionLoader()
    node.load_and_publish()
    rclpy.shutdown()

if __name__ == '__main__':
    main()