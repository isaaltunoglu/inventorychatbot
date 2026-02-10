Google Cloud VM Deployment Guide
Requirements
Python 3.10+

4GB+ RAM (Required for NLU models)

Internet access (For initial model download)

Installation
1. Install System Packages
Run the following command to prepare the environment:

2. Copy Project Files
Move your project files to the VM (using scp, git clone, etc.):

3. Create Python Virtual Environment
Keep your dependencies isolated and clean:

4. Manual Testing
Before going live, test the application manually:

Open http://<VM_IP>:8000 in your browser to verify.

5. Setup Systemd Service (For 24/7 Operation)
This ensures the app restarts automatically if the server reboots:

6. Check Service Status
Monitor the health of your application:

Firewall (GCP)
You must open port 8000 in the GCP Console to allow traffic:

Navigate to VPC Network > Firewall.

Create a new rule:

Direction: Ingress

Targets: All instances / Specific tag

Source IP ranges: 0.0.0.0/0

Protocols and ports: tcp:8000
