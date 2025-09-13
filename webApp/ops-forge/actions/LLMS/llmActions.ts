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
