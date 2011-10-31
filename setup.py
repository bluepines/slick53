
from distutils.core import setup

if __name__ == '__main__':
    setup(name='Slick53',
          version='0.91',
          description='Python Interface to Route53',
          author='Brad Carleton',
          author_email='brad.carleton@bluepines.org',
          url='http://github.com/bluepines/Slick53',
          #package_dir = {'': '.'},
          packages = ['slick53', 'slick53.route53'],
          requires=['boto (>=2.0)']
    )
