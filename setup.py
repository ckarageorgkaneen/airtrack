from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='airtrack',
    version='1.0',
    packages=['airtrack'],
    author=['Chris Karageorgiou Kaneen'],
    author_email='ckarageorgkaneen@gmail.com',
    long_description=readme(),
    license_files=('LICENSE',),
    url='https://github.com/ckarageorgkaneen/airtrack',
)
