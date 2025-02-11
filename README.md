# Project Setup and Execution

## Prerequisites
Make sure you have the following installed on your system:
- Docker
- Python 3

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Run the project** using Docker:
   ```bash
   python3 docker_run.py
   ```
   This will automatically build and run a Docker container with the current directory mounted to `/app` and port `8000` mapped to `localhost:8000`.

## Project Structure
```
.
├── Dockerfile
├── docker_run.py  # Script to build and run the container
├── app/           # Application source code
└── README.md      # This file
```

## Notes
- Ensure that Docker is running before executing `docker_run.py`.
- The application will be available on `http://localhost:8000`.
- Any changes in the project directory will be reflected inside the Docker container since it is mounted as a volume.

## Troubleshooting
- If you encounter permission issues, try running the command with `sudo` (on Linux/Mac):
  ```bash
  sudo python3 docker_run.py
  ```
- Verify that Docker is installed and running:
  ```bash
  docker version
  ```

