from distutils.core import setup
setup(
  name = 'netcrawler',
  packages = ['netcrawler'],
  version = '19.12.23',
  license='gpl-3.0',
  description = 'A collection of tools for searching the internets.',
  author = 'Kaiser',
  author_email = 'technomancer@gmx.com',
  url = 'https://github.com/Kaiz0r/netcrawler',
  download_url = 'https://github.com/Kaiz0r/netcrawler/archive/19.12.23.tar.gz',
  keywords = ['search', 'easy', 'scraper', 'website', 'download', 'links', 'images', 'videos'],
  install_requires=[
          'beautifulsoup4',
          'requests'
      ],
  classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
