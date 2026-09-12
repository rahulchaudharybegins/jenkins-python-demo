# Jenkins webhook test , this is testing purpose only
import os
import shutil


BUILD_DIR = "build"
SOURCE_DIR = "app"


def build_application():
    print("Starting application build...")

    if os.path.exists(BUILD_DIR):
        print("Removing previous build...")
        shutil.rmtree(BUILD_DIR)

    os.makedirs(BUILD_DIR)

    shutil.copytree(
        SOURCE_DIR,
        os.path.join(BUILD_DIR, SOURCE_DIR),
        ignore=shutil.ignore_patterns(
            "__pycache__",
            "*.pyc"
        )
    )

    print("Application copied to build directory.")
    print("Build completed successfully.")


if __name__ == "__main__":
    build_application()