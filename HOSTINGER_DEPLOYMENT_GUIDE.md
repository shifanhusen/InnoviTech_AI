# Automatic Deployment Guide for Hostinger Ubuntu Server

This guide provides all the steps to configure a GitHub Actions workflow that automatically deploys your project to a Hostinger Ubuntu server with Docker.

---

### **Part 1: Prepare Your Hostinger Server**

First, you need to connect to your server and set up an SSH key pair. This allows GitHub Actions to securely log into your server without a password.

**1.1. Connect to Your Server**
Use an SSH client or the VS Code terminal to connect to your Hostinger VPS:
```bash
ssh your-username@your-server-ip
```
*(Replace `your-username` and `your-server-ip` with your actual server credentials).*

**1.2. Install Git (if not already installed)**
The deployment script uses Git to pull the latest code.
```bash
sudo apt-get update
sudo apt-get install -y git
```

**1.3. Add Your User to the Docker Group**
This allows you to run Docker commands without `sudo`.
```bash
sudo usermod -aG docker ${USER}
```
**IMPORTANT**: You must log out and log back in for this change to take effect.
```bash
exit
```
Now, SSH back into your server before continuing.

**1.4. Generate a New SSH Key for GitHub**
This key will be used exclusively by GitHub Actions.
```bash
# When prompted, press Enter to accept the defaults (no passphrase).
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy
```

**1.5. Authorize the New Public Key**
This command adds the new key to the list of keys allowed to log in.
```bash
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys
```

**1.6. Get the Private Key**
You will need to copy the entire output of this command. This is the secret key you will give to GitHub.
```bash
cat ~/.ssh/github_actions_deploy
```
The output will look like this. **Copy everything, from `-----BEGIN...` to `...END-----`**, and save it somewhere safe for the next part.
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
... (many lines of characters) ...
YXRpb25zLWRlcGxveQECAw==
-----END OPENSSH PRIVATE KEY-----
```
You are now finished with the server-side setup.

---

### **Part 2: Set Up Your GitHub Repository and Secrets**

Now, let's create the GitHub repository and securely store the server credentials.

**2.1. Create a New Repository on GitHub**
1.  Go to [github.com/new](https://github.com/new).
2.  Enter a **Repository name** (e.g., `ai-assistant`).
3.  Choose **Private** for better security.
4.  **Do not** initialize with a README, .gitignore, or license.
5.  Click **Create repository**.

**2.2. Configure GitHub Secrets**
This is where you'll store the credentials the GitHub Action needs to access your server.
1.  In your new repository, go to **Settings** > **Secrets and variables** > **Actions**.
2.  Click the **New repository secret** button for each of the secrets below.

**Secret 1: `SERVER_HOST`**
*   **Name:** `SERVER_HOST`
*   **Value:** Your Hostinger server's IP address.

**Secret 2: `SERVER_USERNAME`**
*   **Name:** `SERVER_USERNAME`
*   **Value:** The username you use to SSH into your server (e.g., `ubuntu`).

**Secret 3: `SSH_PRIVATE_KEY`**
*   **Name:** `SSH_PRIVATE_KEY`
*   **Value:** Paste the **entire private key** you copied in step 1.6.

**Secret 4: `PROJECT_PATH`**
*   **Name:** `PROJECT_PATH`
*   **Value:** The absolute path where the project will live on your server. A good choice is `/home/your-username/ai-assistant`.

After adding them, you should have four secrets listed in your repository settings.

---

### **Part 3: Push Your Project to GitHub and Deploy**

This is the final step. You will link your local project to the GitHub repository and push the code. This push will automatically trigger the first deployment.

**3.1. Link Local Project to GitHub**
Run these commands in your **local PowerShell terminal** in the project directory (`c:\Users\shifa\source\InnoviTech AI`).

*(Replace `YOUR-GITHUB-USERNAME` and `YOUR-REPO-NAME` with your actual GitHub details).*
```powershell
# Link your local repo to the one on GitHub
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/YOUR-REPO-NAME.git

# Verify the remote URL
git remote -v
```

**3.2. Push and Trigger Deployment**
This command sends all your code to GitHub, which will automatically start the "Deploy to Ubuntu Server" action.
```powershell
git push -u origin main
```

**3.3. Monitor the Deployment**
1.  Go to the **Actions** tab in your GitHub repository.
2.  You will see a workflow named "Deploy to Ubuntu Server" running.
3.  Click on it to see the live logs as it connects to your server, pulls the code, and runs `docker compose`.

Once the action completes successfully, your AI assistant will be live on your Hostinger server!

**3.4. Verify on the Server**
You can SSH into your server and check that the containers are running:
```bash
docker ps
```
You should see the `ai-assistant-backend`, `ai-assistant-frontend`, `ai-assistant-nginx`, and other containers running.
