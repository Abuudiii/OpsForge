"use server";

import Groq from "groq-sdk";
import { createStreamableValue } from "@ai-sdk/rsc"; // ⬅️ new import

export type ChatMessage = {
  role: "system" | "user" | "assistant";
  content: string;
};

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY!,
});

export async function streamGroqChat(messages: ChatMessage[]) {
  const stream = createStreamableValue<string>("");

  (async () => {
    try {
      const completion = await groq.chat.completions.create({
        model: "meta-llama/llama-4-maverick-17b-128e-instruct",
        messages,
        stream: true,
        temperature: 0.7,
      });

      for await (const chunk of completion) {
        const delta = chunk.choices?.[0]?.delta?.content ?? "";
        if (delta) stream.update(delta);
      }
      stream.done();
    } catch (err: any) {
      stream.error(
        new Error(`Groq streaming failed${err?.message ? `: ${err.message}` : ""}`)
      );
    }
  })();

  return { output: stream.value };
}


// Non-streaming: returns the whole answer at once
export async function completeGroqChat(
  messages: ChatMessage[],
  opts?: { temperature?: number; max_tokens?: number }
) {
  try {
    const resp = await groq.chat.completions.create({
      model: "meta-llama/llama-4-maverick-17b-128e-instruct",
      messages,
      // stream is false by default, but explicit is nice:
      stream: false,
      temperature: opts?.temperature ?? 0.7,
      max_tokens: opts?.max_tokens, // optional, let Groq decide if undefined
    });

    // Concatenate all choice contents (usually there’s just one)
    const content =
      resp.choices?.map((c) => c.message?.content ?? "").join("") ?? "";

    return { content };
  } catch (err: any) {
    // Surface a clean error back to the client
    throw new Error(
      `Groq completion failed${err?.message ? `: ${err.message}` : ""}`
    );
  }
}

export async function completeStructuredGroqChat<T = unknown>(
  messages: ChatMessage[],
  jsonSchema: Record<string, any>,
  opts?: { temperature?: number; max_tokens?: number }
): Promise<{ raw: string; object: T }> {
  const schemaStr = JSON.stringify(jsonSchema);

  const systemGuard: ChatMessage = {
    role: "system",
    content: [
      "You are a service that returns ONLY valid JSON.",
      'You are an instruction rewriter and classifier for cloud console operations. The user will provide a natural language request related to AWS, GCP, or Azure. ### Step 1: Break Down the Request - Parse the user’s request carefully. - Think in set-by-set instructions that a computer in a cloud environment (AWS, GCP, Azure) could execute. - Include all relevant details such as service, resource type, operation, filters, regions, accounts, and expected outputs. - Make assumptions explicit if the user’s request is vague (e.g., if no region is given, assume `us-east-1`). ### Step 2: Classify the Action - If the user request is about creating, updating, deleting, or modifying any resource → classify as `\"MODIFY\"`. - If the user request is about retrieving, viewing, listing, checking status, or describing resources → classify as `\"VIEW\"`. - Only output one of these two values. ### Step 3: Restructure the Prompt - Rewrite the original prompt into a **clearer, more detailed version** of what the user wants. - Expand the intent by clarifying ambiguous parts and making it ready for automation. - Make it precise enough so a cloud system could execute it without confusion. ### Step 4: Output - Return **only JSON**, with no extra text or explanation. - JSON format must be:{ \"action\": \"VIEW\" | \"MODIFY", "modifiedInfo\": \"..." }',
      "Do not include code fences, explanations, or extra text.",
      "Your output MUST validate against this JSON Schema:",
      schemaStr,
    ].join("\n"),
  };

  const reqMessages: ChatMessage[] = [systemGuard, ...messages];

  const resp = await groq.chat.completions.create({
    model: "meta-llama/llama-4-maverick-17b-128e-instruct",
    messages: reqMessages,
    stream: false,
    // Force JSON-only output if supported by the model/SDK:
    response_format: { type: "json_object" } as any,
    temperature: opts?.temperature ?? 0, // lower temp for structure fidelity
    max_tokens: opts?.max_tokens,
  });

  const raw = resp.choices?.[0]?.message?.content ?? "";
  let parsed: T;
  try {
    parsed = JSON.parse(raw) as T;
  } catch {
    // If the model somehow returns non-JSON, surface a clean error
    throw new Error("Model did not return valid JSON. Raw output: " + raw);
  }

  // Return both the raw string and the parsed object to satisfy the declared return type
  return { raw, object: parsed };
}