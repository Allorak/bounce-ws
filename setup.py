from setuptools import setup, find_packages

setup(
    name="ws_framework",
    version="0.9.1",
    author="Mike Moiseev",
    author_email="mvmoiseev@miem.hse.ru",
    description="A simple framework for websocket event-based messaging using flask websockets under the hood",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://git.miem.hse.ru/vt3/websocket-api",
    packages=find_packages(),
    install_requires=[
        "uvicorn",
        "fastapi",
        "loguru"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Framework :: Flask",
        "Natural Language :: English"
    ],
    python_requires='>=3.8'
)