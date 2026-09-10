import os
import shutil


BUILD_DIR = "build"


def build_application():
    print("Starting application build...")

    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)

    os.makedirs(BUILD_DIR)

    shutil.copytree(
        "app",
        os.path.join(BUILD_DIR, "app")
    )

    print("Application copied to build directory.")
    print("Build completed successfully.")


if __name__ == "__main__":
    build_application()