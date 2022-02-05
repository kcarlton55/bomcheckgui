
'''
Intial structure before creating a package:

bomcheck/
    src/
        __init__.py
        bomcheckgui.py
    LICENSE.txt
    README.md
    setup.py

Where __init__.py is a text file that is empty.
'''

from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='bomcheckgui',   # name people will use to pip install
    version='1.7.6',
    description='gui for bomcheck',
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=['bomcheckgui'],
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',],
    install_requires = ['bomcheck>=1.8', 'pyside2>=5.15'],
    url='https://github.com/kcarlton55/bomcheckgui',
    author='Kenneth Edward Carlton',
    author_email='kencarlton55@gmail.com',
    entry_points={'gui_scripts': ['bomcheckgui=bomcheckgui:MainWindow']},
    keywords='BOM,BOMs,compare,bill,materials,SolidWorks,SyteLine,ERP',
)
