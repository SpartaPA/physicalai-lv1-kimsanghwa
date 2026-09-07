from setuptools import find_packages, setup

package_name = 'turtle_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pa16',
    maintainer_email='hwa04866@gmail.com',
    description='turtlesim pose를 구독해 원점까지의 거리를 발행하는 rclpy 패키지',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'distance_publisher = turtle_py.distance_publisher:main',
            'distance_watcher = turtle_py.distance_watcher:main',
            'draw_polygon = turtle_py.draw_polygon:main',
            'tf_broadcaster = turtle_py.tf_broadcaster:main',
            'waypoint_markers = turtle_py.waypoint_markers:main',
        ],
    },
)
