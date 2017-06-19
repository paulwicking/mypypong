try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'description': 'MyPyPong',
	'author': 'wowsuchnamaste',
	'url': 'github.com/wowsuchnamaste',
	'download_url': 'github.com/wowsuchnamaste/mypypong',
	'author_email': 'my email',
	'version': '0.1'
	'install_requires': ['nose'],
	'packages': ['mypypong'],
	'scripts': [],
	'name': 'mypypong'
}

setup(**config)
