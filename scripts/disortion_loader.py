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
            '/cmd_vel_clear',
            self.listener_callback,
            10)
        
        csv_file_path = os.path.join(os.path.dirname(__file__), 'disortions/')
        self.declare_parameter('PRBS_33Hz_amp=010deg.csv', csv_file_path)
        
        self.twist_commands = []
        self.counter = 0
                
    def listener_callback(self, msg):
        self.get_logger().info(f'Received command: linear={msg.linear.x}, angular={msg.angular.z}')
        
        steering_angle = msg.angular.z
        
        self.counter += 1
        if self.counter < len(self.twist_commands):
            steering_angle = steering_angle + float(self.twist_commands[self.counter])
            self.get_logger().info(f'Applied distortion: {self.twist_commands[self.counter]}')
            
            
        distorted_msg = Twist()
        distorted_msg.linear.x = msg.linear.x
        distorted_msg.angular.z = steering_angle
        self.publisher.publish(distorted_msg)
        self.get_logger().info(f'Published distorted command: linear={distorted_msg.linear.x}, angular={distorted_msg.angular.z}')
        
        
        
        
    def load(self):
        csv_file = self.get_parameter('csv_file').value
        delay = self.get_parameter('delay').value
        
        try:
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        self.twist_commands.append(row[0])
                        self.get_logger().info(f'Loaded: {row[0]}')
                    
        except FileNotFoundError:
            self.get_logger().error(f'CSV file not found: {csv_file}')

def main(args=None):
    rclpy.init(args=args)
    node = DistortionLoader()
    node.load()
    rclpy.shutdown()

if __name__ == '__main__':
    main()