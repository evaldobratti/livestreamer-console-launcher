from setuptools import setup

setup(name='twitchlauncher',
      version='0.1',
      description='Console livestreamer launcher from twitch streams.',
      keywords='livestreamer twitch',
      url='https://github.com/evaldobratti/twitchlauncher',
      author='Evaldo Bratti',
      author_email='evaldo.bratti@gmail.com',
      license='WTFPL',
      packages=['twitchlauncher'],
      entry_points={
          "console_scripts": ["twitchlauncher=twitchlauncher:main"]
      },
      install_requires=['requests', 'requests[security]', 'livestreamer'])