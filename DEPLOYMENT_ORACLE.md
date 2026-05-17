# Oracle Cloud Free Tier Deployment Guide: SG Mobile Price Tracker

This guide covers deploying the 6-container Docker stack to an Oracle Cloud **Always Free ARM (Ampere)** instance. This is the recommended platform because it provides up to **24 GB of RAM**, allowing the aggregator to run without memory pressure.

## 1. Create the VM Instance (Manual)

1.  Login to [Oracle Cloud Console](https://cloud.oracle.com/).
2.  Go to **Compute** > **Instances** > **Create Instance**.
3.  **Name**: `sg-price-tracker`
4.  **Placement**: Use the default Availability Domain.
5.  **Image and Shape**:
    *   Click **Change Shape**.
    *   Select **Ampere** (ARM-based processor).
    *   Select **VM.Standard.A1.Flex**.
    *   Configure it for **1-4 OCPUs** and **6-24 GB of RAM** (Stay within the "Always Free" label).
    *   Select **Ubuntu 22.04** or **Oracle Linux 8** (Ubuntu is recommended).
6.  **Networking**: 
    *   Ensure **Assign a public IPv4 address** is selected.
7.  **SSH Keys**: Generate or upload your public key. **Save the private key locally!**
8.  Click **Create**.

---

## 2. Configure Cloud Firewall (VCN Security List)

Oracle Cloud blocks all traffic by default. You must open Port 80 in the cloud console:

1.  On the Instance Details page, click on the **Subnet** link (e.g., `Public Subnet...`).
2.  Click on the **Security List** for the VCN.
3.  Click **Add Ingress Rules**:
    *   **Source CIDR**: `0.0.0.0/0`
    *   **IP Protocol**: `TCP`
    *   **Destination Port Range**: `80`
    *   **Description**: `Allow HTTP access to dashboard`
4.  Click **Add Ingress Rules**.

---

## 3. Server Provisioning (SSH)

SSH into your instance:
`ssh -i path/to/your/private_key ubuntu@YOUR_VM_IP`

Run these commands to install Docker and fix the OS-level firewall:

### A. Install Docker & Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Allow your user to run docker
sudo usermod -aG docker $USER
newgrp docker
```

### B. Fix OS Firewall (Ubuntu Specific)
Oracle's Ubuntu images have strict `iptables` rules that can block Port 80 even if opened in the cloud console. Run these to clear them:

```bash
# Open Port 80 and 443 at the OS level
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# If UFW is not installed, or rules still persist:
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo netfilter-persistent save
```

---

## 4. Deploy Code (Local Machine)

On **your local computer**, run the following command to sync the project.

```bash
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude '.gemini' ./ ubuntu@YOUR_VM_IP:~/sg-price-tracker
```

---

## 5. Launch the Stack (SSH)

Go back to your **Oracle SSH terminal**:

```bash
cd ~/sg-price-tracker

# Start all 6 containers
docker compose up -d --build
```

---

## 6. Verification

1.  Navigate to `http://YOUR_EXTERNAL_IP` in your browser.
2.  The dashboard should load. Since this is an ARM instance with plenty of RAM, you do **not** need a swap file.
3.  The Docker build will be much faster than on AWS/GCP.

### Manual Scrape Trigger
```bash
docker exec singapore_mobile_pricing-worker-1 python3 -c "from src.orchestrator import scrape_all_sources; scrape_all_sources.delay()"
```
