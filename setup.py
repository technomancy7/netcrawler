from distutils.core import setup
setup(
  name = 'websearcher',
  packages = ['websearcher'],
  version = '19.09.12.2',
  license='gpl-3.0',
  description = 'A collection of tools for searching the internets.',
  author = 'Kaiser',
  author_email = 'technomancer@gmx.com',
  url = 'https://github.com/Kaiz0r/websearcher',
  download_url = 'https://github.com/Kaiz0r/websearcher/archive/19.09.12.2.tar.gz',
  keywords = ['search', 'easy', 'scraper', 'website', 'download', 'links', 'images', 'videos'],
  install_requires=[
          'beautifulsoup4',
      ],
  classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
