from setuptools import find_packages, setup

setup(
    name="agentsdk",
    verison="0.0.1",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "agent=agentsdk.chat:main",
        ],
    },
)
