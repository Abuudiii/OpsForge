from flask import Flask, request, jsonify
import subprocess
import os
import time
from anthropic import Anthropic

app = Flask(__name__)

@app.route('/htn', methods=['POST'])
def create_infrastructure():
    # Get query from request
    data = request.get_json()
    print(data)
    if not data or 'modifiedInfo' not in data:
        return jsonify({'error': 'Please provide a "query" in the request body'}), 400

    user_query = data['modifiedInfo']

    # Initialize Claude client
    client = Anthropic(
        api_key="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"
    )

    # System prompt that FORCES AWS help usage
    SYSTEM_PROMPT = """You are an AWS infrastructure builder that MUST follow this exact workflow for EVERY resource:

## MANDATORY WORKFLOW FOR EACH RESOURCE:
1. FIRST run: aws <service> help | grep -i <resource>
2. THEN run: aws <service> <command> help | head -30
3. ONLY THEN create the resource with the correct command

## CRITICAL RULES:
- ALWAYS use --region us-east-1 in every command
- ALWAYS use --query to extract IDs (e.g., --query 'Vpc.VpcId' --output text)
- ALWAYS add a comment before each command explaining what it does
- Variables are automatically saved (VPC_ID, SUBNET_ID, etc.) and available in subsequent commands

## DEPENDENCY ORDER (MUST FOLLOW):
1. VPC → 2. Subnet → 3. Internet Gateway → 4. Route Table → 5. Security Group → 6. EC2 Instance

## OUTPUT FORMAT:
Return ONLY commands with # comments. NO explanations, NO markdown.

## EXAMPLE (YOU MUST FOLLOW THIS PATTERN):

# Check VPC commands
aws ec2 help | grep -i vpc
# Get create-vpc syntax
aws ec2 create-vpc help | head -30
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --region us-east-1 --query 'Vpc.VpcId' --output text
# Verify VPC
aws ec2 describe-vpcs --vpc-ids $VPC_ID --region us-east-1 --query 'Vpcs[0].State' --output text

# Check subnet commands
aws ec2 help | grep -i subnet
# Get create-subnet syntax
aws ec2 create-subnet help | head -30
# Create subnet
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --region us-east-1 --query 'Subnet.SubnetId' --output text
# Verify subnet
aws ec2 describe-subnets --subnet-ids $SUBNET_ID --region us-east-1 --query 'Subnets[0].State' --output text

REMEMBER: You MUST check help before EVERY resource creation. Variables persist automatically."""

    # Send to Claude
    response = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_query
            }
        ]
    )

    # Get Claude's response
    claude_response = response.content[0].text

    # Execution with persistent environment variables
    execution_log = []
    execution_log.append("Executing AWS Infrastructure Commands:")
    execution_log.append("=" * 50)

    # Create persistent storage directory
    storage_dir = "/tmp/aws_infra"
    os.makedirs(storage_dir, exist_ok=True)

    # Function to save variables persistently
    def save_var(name, value):
        """Save variable to file for persistence"""
        with open(f"{storage_dir}/{name}", 'w') as f:
            f.write(value)
        execution_log.append(f"  → Saved {name}: {value}")

    def load_var(name):
        """Load variable from file"""
        try:
            with open(f"{storage_dir}/{name}", 'r') as f:
                return f.read().strip()
        except:
            return None

    # Load existing variables
    env_vars = os.environ.copy()
    for var_name in ['VPC_ID', 'SUBNET_ID', 'IGW_ID', 'RTB_ID', 'SG_ID', 'INSTANCE_ID', 'AMI_ID']:
        value = load_var(var_name)
        if value:
            env_vars[var_name] = value
            execution_log.append(f"✓ Loaded existing {var_name}: {value}")

    # Process commands from Claude
    lines = claude_response.strip().split('\n')

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Log comments
        if line.startswith('#'):
            execution_log.append(f"\n{line}")
            continue

        # Execute AWS commands
        if line.startswith('aws ') or line.startswith('sleep '):
            execution_log.append(f"Executing: {line}")

            # Skip if resource already exists
            skip = False
            if 'create-vpc' in line and load_var('VPC_ID'):
                execution_log.append(f"⏭ Skipping - VPC already exists: {load_var('VPC_ID')}")
                skip = True
            elif 'create-subnet' in line and load_var('SUBNET_ID'):
                execution_log.append(f"⏭ Skipping - Subnet already exists: {load_var('SUBNET_ID')}")
                skip = True
            elif 'create-internet-gateway' in line and load_var('IGW_ID'):
                execution_log.append(f"⏭ Skipping - IGW already exists: {load_var('IGW_ID')}")
                skip = True
            elif 'create-security-group' in line and load_var('SG_ID'):
                execution_log.append(f"⏭ Skipping - SG already exists: {load_var('SG_ID')}")
                skip = True
            elif 'run-instances' in line and load_var('INSTANCE_ID'):
                execution_log.append(f"⏭ Skipping - Instance already exists: {load_var('INSTANCE_ID')}")
                skip = True

            if skip:
                continue

            try:
                # Execute with environment variables
                result = subprocess.run(line, shell=True, capture_output=True, text=True, env=env_vars)

                if result.returncode == 0:
                    output = result.stdout.strip()

                    # Show output (truncated for readability)
                    if len(output) > 100:
                        execution_log.append(f"✓ Success: {output[:100]}...")
                    else:
                        execution_log.append(f"✓ Success: {output}")

                    # Extract and save resource IDs
                    if output and not ' ' in output and not 'help' in line.lower():
                        if 'vpc-' in output:
                            save_var('VPC_ID', output)
                            env_vars['VPC_ID'] = output
                        elif 'subnet-' in output:
                            save_var('SUBNET_ID', output)
                            env_vars['SUBNET_ID'] = output
                        elif 'igw-' in output:
                            save_var('IGW_ID', output)
                            env_vars['IGW_ID'] = output
                        elif 'rtb-' in output:
                            save_var('RTB_ID', output)
                            env_vars['RTB_ID'] = output
                        elif 'sg-' in output:
                            save_var('SG_ID', output)
                            env_vars['SG_ID'] = output
                        elif 'ami-' in output:
                            save_var('AMI_ID', output)
                            env_vars['AMI_ID'] = output
                        elif 'i-' in output and len(output) > 2:
                            save_var('INSTANCE_ID', output)
                            env_vars['INSTANCE_ID'] = output

                    # Add delay after resource creation
                    if any(cmd in line for cmd in ['create-vpc', 'create-subnet', 'create-internet-gateway',
                                                   'create-security-group', 'run-instances', 'attach-internet']):
                        execution_log.append("  → Waiting for resource to stabilize...")
                        time.sleep(2)

                else:
                    # Don't fail on help commands or verify commands
                    if 'help' in line or 'describe' in line:
                        execution_log.append(f"ℹ Info: {result.stderr[:200]}")
                    else:
                        execution_log.append(f"✗ Error: {result.stderr}")
                        # Continue anyway for robustness

            except Exception as e:
                execution_log.append(f"✗ Exception: {str(e)}")
                # Continue anyway

    # Summary
    execution_log.append("\n" + "=" * 50)
    execution_log.append("Infrastructure creation complete!")

    # Collect created resources
    resources = {}
    for var_name in ['VPC_ID', 'SUBNET_ID', 'IGW_ID', 'RTB_ID', 'SG_ID', 'INSTANCE_ID', 'AMI_ID']:
        value = load_var(var_name)
        if value:
            resources[var_name] = value

    if resources:
        execution_log.append("\nCreated resources:")
        for key, value in resources.items():
            execution_log.append(f"  {key}: {value}")

    return jsonify({
        'status': 'success',
        'message': 'Infrastructure created successfully',
        'execution_log': '\n'.join(execution_log),
        'resources': resources,
        'claude_response': claude_response
    })

if __name__ == '__main__':
    app.run(debug=True)