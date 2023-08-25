from setuptools import setup

setup(name='pyutils',
      version='0.1',
      description='A simple library of Python utilities',
      url='https://github.com/dfortin00/pyutils',
      author='Dennis Fortin',
      author_email='dfortin456@gmail.com',
      license='MIT',
      packages=[
          'pyutils',
          'pyutils.utils',
          'pyutils.objects'
      ],
      # zip_safe=False
)
