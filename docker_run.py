import os
import subprocess
import sys

def check_docker():
    """Check if Docker is installed and running."""
    try:
        subprocess.run(["docker", "version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Docker is not installed. Please install Docker and try again.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Docker is not running. Please start Docker and try again.")
        sys.exit(1)

def build_and_run():
    """Build and run the Docker container from the current directory's Dockerfile, mount current directory, and expose port 8000."""
    current_dir = os.path.basename(os.getcwd())
    image_tag = f"{current_dir.lower()}_image"
    container_name = f"{current_dir.lower()}_container"
    
    print(f"Building Docker image '{image_tag}'...")
    build_cmd = ["docker", "build", "-t", image_tag, "."]
    subprocess.run(build_cmd, check=True)
    
    print(f"Running container '{container_name}' with volume mount and port mapping...")
    run_cmd = [
        "docker", "run", "--rm", "--name", container_name,
        "-v", f"{os.getcwd()}:/app",
        "-p", "8000:8000",
        image_tag
    ]
    subprocess.run(run_cmd, check=True)

if __name__ == "__main__":
    check_docker()
    build_and_run()
