import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Anthropic client
# Make sure to set your API key as an environment variable: ANTHROPIC_API_KEY
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

client = Anthropic(api_key=api_key)
def send_prompt_to_claude(prompt, max_tokens=1000, system_prompt=None):
    """
    Send a prompt to Claude and get a response

    Args:
        prompt: The text prompt to send to Claude
        max_tokens: Maximum number of tokens in the response
        system_prompt: Optional system prompt to set context

    Returns:
        The response text from Claude
    """
    try:
        messages = [{"role": "user", "content": prompt}]

        response = client.messages.create(
            model="claude-opus-4-1-20250805",  # Claude Opus 4.1 model
            max_tokens=max_tokens,
            messages=messages,
            system=system_prompt if system_prompt else None
        )
        # Extract text from the response
        content = response.content[0]

        # Check the type of content block and extract text accordingly
        if content.type == "text":
            return content.text
        else:
            # For non-text blocks, return a string representation
            return f"[{content.type} block]: {str(content)}"

    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Example prompt
    prompt = "Create a VPC in the us-east-1 region with a CIDR block of 10.0.0.0/16, a public subnet within this VPC in the same region with a CIDR block of 10.0.1.0/24, and launch an EC2 instance of type t2.micro with Amazon Linux 2 AMI in the public subnet, assigning a public IP address to the instance."

    print("Sending prompt to Claude...")
    response = send_prompt_to_claude(prompt)
    print(f"\nClaude's response:\n{response}")