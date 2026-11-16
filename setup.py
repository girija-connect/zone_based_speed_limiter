from setuptools import setup

package_name = 'speed_limiter'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
    ('share/speed_limiter', ['package.xml']),

    ('share/speed_limiter/launch',
        ['launch/speed_limiter.launch.py']),

    ('share/speed_limiter/config',
        ['config/speed_zone.yaml']),
	],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='girija',
    maintainer_email='girijateli1310@gmail.com',
    description='Zone based speed limiter for navigation',
    license='Apache License 2.0',

    entry_points={
        'console_scripts': [
            'speed_limiter = speed_limiter.speed_limiter:main',
        ],
    },
)