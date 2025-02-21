# Get Started

Before using this project, ensure that you have completed the necessary setup steps. Below are the key prerequisites and configurations required.

---

## 1. Install Dependencies

Before proceeding with any setup, install all required Python dependencies:

```bash
pip install -r requirements.txt
```

This ensures that all necessary packages are installed for the project.

---

## 2. Host YAGO on Blazegraph

To get started, you need to host **YAGO on Blazegraph 4.5**. Detailed setup instructions are provided [here](./src/kg/README.md).

---

## 3. AWS Endpoints for LLMs

Currently, we are using **AWS endpoints** for Large Language Model (LLM) inference. Support will soon be extended to **Hugging Face** local models and **Azure** endpoints.

### Setting up AWS on Ubuntu

Follow these steps to configure AWS services for this project:

### **Step 1: Install AWS CLI**
Run the following commands in your terminal to install AWS CLI on Ubuntu:

```bash
sudo apt update
sudo apt install -y awscli
```

To verify installation:
```bash
aws --version
```

---

### **Step 2: Configure AWS CLI**
Once installed, configure AWS with your credentials:

```bash
aws configure
```
You will be prompted to enter:
- **AWS Access Key ID** (Obtain from AWS IAM)
- **AWS Secret Access Key**
- **Default region name** (e.g., `us-west-2`)
- **Output format** (default: `json`)

---

### **Step 3: Set Up AWS Credentials (Alternative)**
If you want to manually set up AWS credentials, create a credentials file:

```bash
mkdir -p ~/.aws
nano ~/.aws/credentials
```
Add the following details:

```
[default]
aws_access_key_id=YOUR_ACCESS_KEY
aws_secret_access_key=YOUR_SECRET_KEY
region=us-west-2
```
Save and exit (`CTRL + X`, then `Y`, then `Enter`).

---

### **Step 4: Verify AWS Connection**
Run this command to check your AWS identity:

```bash
aws sts get-caller-identity
```

You should see an output with your AWS account details.

---
