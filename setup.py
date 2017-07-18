from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))


long_description = ''

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = ''

setup(
    name='django-oscar-webpay',

    version='0.2.22',

    description='An application for intagrating WebPay with oscar based e-commerce sites',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/RaydelMiranda/django-oscar-webpay',

    # Author details
    author='Raydel Miranda',
    author_email='raydel.miranda.gomez@gmail.com',

    license='LGPL',
    data_files=[('', ['README.md'])],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Environment :: Web Environment',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='development web django webpay ecommerce',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=[
        'oscar_webpay',
        'oscar_webpay.certificates',
        'oscar_webpay.libwebpay',
        'oscar_webpay.dashboard',
        'oscar_webpay.exceptions'
    ],

    include_package_data=True,

    install_requires=['suds==0.4', 'py-wsse==0.1'],
)
