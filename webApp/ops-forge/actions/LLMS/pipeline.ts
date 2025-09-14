"use server";
import { LambdaClient, InvokeCommand } from "@aws-sdk/client-lambda";
import { completeGroqChat, completeStructuredGroqChat, type ChatMessage } from "./llmActions";

export async function invokeLambda(query: string) {
    // Initialize the Lambda client
    const lambdaClient = new LambdaClient({
        region: "us-east-1", // Make sure this matches your Lambda's region
        credentials: {
            accessKeyId: process.env.AWS_ACCESS_KEY_ID as string,
            secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY as string
        }
    });

    const payload = JSON.stringify({
        "body": {
            heartbeat: false,
            query: query
        }
    });

    // Create the InvokeCommand with InvocationType: 'Event' for asynchronous (fire and forget) execution
    const command = new InvokeCommand({
        FunctionName: "study-platform-mixedparser", // Replace with your Lambda function name
        InvocationType: "Event", // "Event" for async (fire and forget)
        Payload: Buffer.from(payload)
    });

    try {
        // Invoke the Lambda function asynchronously
        await lambdaClient.send(command);
        console.log("Lambda invocation triggered successfully");
        return { success: true, message: "Main Processing started" };
    } catch (error) {
        console.error("Error invoking Lambda function:", error);
        return { success: false, error: "Failed to start main processing" };
    }

}

export async function prepareInvokingLambda(query: string) {
    try {
        type PreparationResult = { action: 'view' | 'modify'; modifiedInfo: string };

        const messages: ChatMessage[] = [
            {
                role: 'system',
                content: [
  "You parse and restructure a user request related to applications, cloud platforms, or infrastructure operations.",
  "First, break the request into clear step-by-step instructions that a computer could execute in AWS, GCP, or Azure environments.",
  "Classify the request as either VIEW (retrieve, inspect, describe, or check status) or MODIFY (create, update, delete, provision, or configure). Only one of these two values is allowed.",
  "Generate 'modifiedInfo' as a clarified, detailed reformulation of the user’s request, adding explicit details, assumptions (like default region or scope if missing), and making the intent unambiguous.",
  "Do not invent unrelated requirements; stay faithful to what the user wants while making it precise enough for execution.",
  "Return strictly a JSON object with the keys: { action: \"VIEW\" | \"MODIFY\", modifiedInfo: \"...\" }.",
  "Output must contain no extra explanation or text outside the JSON."
].join('\\n')
            },
            { role: 'user', content: query }
        ];

        const schema = {
            type: 'object',
            properties: {
                action: { type: 'string', enum: ['view', 'modify'] },
                modifiedInfo: { type: 'string' }
            },
            required: ['action', 'modifiedInfo'],
            additionalProperties: false
        } as const;

        const { object } = await completeStructuredGroqChat<PreparationResult>(messages, schema, { temperature: 0 });
        console.log('Structured preparation result:', object);
        return object; // { action, modifiedInfo }
    } catch (err) {
        console.error('Error in prepareInvokingLambda:', err);
        return { error: 'Groq structured completion failed' };
    }
}
