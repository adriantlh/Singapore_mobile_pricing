# GCP Free Tier Deployment Guide: SG Mobile Price Tracker

This guide covers deploying the 6-container Docker stack to a Google Cloud Platform (GCP) `e2-micro` instance.

## 1. Create the VM Instance (Manual)

1.  Login to [Google Cloud Console](https://console.cloud.google.com/).
2.  Go to **Compute Engine** > **VM Instances**.
3.  Click **Create Instance**.
4.  **Name**: `sg-price-tracker`
5.  **Region**: `us-central1`, `us-east1`, or `us-west1` (Required for "Always Free" tier).
6.  **Machine Configuration**:
    *   Series: `E2`
    *   Machine Type: `e2-micro` (2 vCPU, 1 GB RAM).
7.  **Boot Disk**:
    *   Operating System: `Ubuntu`
    *   Version: `22.04 LTS`
    *   Size: `30 GB` (Standard Persistent Disk).
8.  **Firewall**:
    *   [x] Allow HTTP traffic
    *   [ ] Allow HTTPS traffic (Enable if you plan to set up SSL later).
9.  Click **Create**.

---

## 2. Server Provisioning (SSH)

Once the VM is running, click the **SSH** button in the GCP console to open a terminal. Run the following commands:

### A. Create Swap Memory (Critical)
Because the `e2-micro` only has 1GB of RAM, we must allocate virtual memory to prevent the 6 Docker containers from crashing during the build or run phase.

```bash
# Create a 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent after reboot
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### B. Install Docker & Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Allow your user to run docker without sudo
sudo usermod -aG docker $USER
newgrp docker
```

---

## 3. Deploy Code (Local Machine)

On **your local computer**, run the following command to sync the project files to the VM. 
Replace `YOUR_GCP_USER` and `YOUR_VM_IP` with your actual GCP SSH username and the VM's External IP.

```bash
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude '.gemini' ./ YOUR_GCP_USER@YOUR_VM_IP:~/sg-price-tracker
```

---

## 4. Launch the Stack (SSH)

Go back to your **GCP SSH terminal** and run:

```bash
# Navigate to the project folder
cd ~/sg-price-tracker

# Start all 6 containers in detached mode
docker compose up -d --build
```

---

## 5. Verification

1.  Find your **External IP** in the GCP Compute Engine dashboard.
2.  Open a browser and navigate to `http://YOUR_EXTERNAL_IP`.
3.  The dashboard should load, and the "Top Deals" carousel will begin populating after the first automated scrape (or after you trigger one manually).

### Manual Scrape Trigger (Optional)
If you want to pull data immediately without waiting for the 12-hour schedule:
```bash
docker exec singapore_mobile_pricing-worker-1 python3 -c "from src.orchestrator import scrape_all_sources; scrape_all_sources.delay()"
```
