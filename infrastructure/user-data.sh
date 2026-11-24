#!/bin/bash
set -e
dnf install -y python3 python3-pip amazon-cloudwatch-agent
mkdir -p /opt/data-pipeline
python3 -m venv /opt/data-pipeline/venv
/opt/data-pipeline/venv/bin/pip install boto3 requests
chown -R ec2-user:ec2-user /opt/data-pipeline
systemctl enable --now amazon-ssm-agent
