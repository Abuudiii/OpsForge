# OpsForge

## Inspiration
Cloud infrastructure can be hard to deploy and set up, especially for those with limited exposure. Even experienced cloud developers often spend a significant amount of time configuring infrastructure through Infrastructure-as-Code (IaC) tools like **Terraform** or **AWS CloudFormation**.

## What It Does
OpsForge automates the provisioning of cloud infrastructure by leveraging **AI**.  

- Uses **Groq** to classify user queries.  
- Pulls the most up-to-date **AWS CLI data** using **Sonar API** from **Perplexity**.  
- Feeds commands into our **LLM**, which provisions infrastructure with the appropriate configurations.  

This enables streamlined development and reduces friction in the DevOps cycle. Startups, in particular, can accelerate deployment and empower developers to focus on building rather than setup.

## How We Built It
OpsForge turns **natural language** into **cloud infrastructure changes**:  

1. User enters a prompt in the **Next.js frontend**.  
2. **Groq** classifies the prompt.  
3. **Perplexity’s Sonar API** retrieves the correct AWS CLI commands.  
4. Our **AI model** runs these commands to trigger the appropriate AWS infrastructure changes.  

## Challenges We Ran Into
- Defining a clear project scope — cloud infrastructure design and maintenance is broad with many possible approaches.  
- Coordinating multiple moving parts (frontend, AI model, Sonar, AWS) into a single streamlined workflow.  

## Accomplishments We're Proud Of
- Strong **team collaboration** and willingness to learn across different technical backgrounds.  
- Successfully integrating **many cloud tools** into one cohesive system.  
- Creating a productive developer experience for provisioning infrastructure via **natural language**.  

## What We Learned
- Hands-on experience with **cloud infrastructure technologies**.  
- How to combine **Next.js frontend** with a comprehensive backend powered by AI.  
- The importance of cross-disciplinary brainstorming when tackling complex system design.  

## What's Next for OpsForge
Currently, our prototype supports **AWS cloud development**. Future plans include expanding support to:  
- **Google Cloud Platform (GCP)**  
- **Microsoft Azure**  
- Other popular cloud tools used by enterprises and startups  

## Built With
- **Amazon Web Services (AWS)**  
- **Azure**  
- **Groq**  
- **JavaScript**  
- **Next.js**  
- **OpenAI**  
- **Perplexity (Sonar API)**  
- **Python**  
- **React**  
- **TypeScript**  

---
