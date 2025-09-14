"use client";

import { useState, useTransition } from "react";
import { readStreamableValue } from "@ai-sdk/rsc"; // ⬅️ v5 import
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowUp } from "lucide-react";
import { streamGroqChat, completeGroqChat, type ChatMessage } from "@/actions/LLMS/llmActions";
import { prepareInvokingLambda } from "@/actions/LLMS/pipeline"; // server action for background prep

export default function HeroSection() {
  const [inputText, setInputText] = useState("");
  const [response, setResponse] = useState("");
  const [modifying, setModifying] = useState(false);
  const [isStreaming, startTransition] = useTransition();

  // Toggle between streaming and non-streaming easily by swapping this reference:
  //const chatFn = completeGroqChat; // <- Non-streaming (bulk) mode
  const chatFn = streamGroqChat; // <- Streaming mode (default)

  type StreamingResult = { output: any };
  type NonStreamingResult = { content: string };
  type ChatFn = (messages: ChatMessage[]) => Promise<StreamingResult | NonStreamingResult>;

  const isStreamingResult = (res: any): res is StreamingResult => res && "output" in res;

  const runChat = async (
    fn: ChatFn,
    messages: ChatMessage[],
    onToken: (partial: string) => void,
    onDone?: () => void
  ) => {
    const result = await fn(messages);
    if (isStreamingResult(result)) {
      let acc = "";
      for await (const token of readStreamableValue(result.output)) {
        acc += token ?? "";
        onToken(acc);
      }
      onDone?.();
    } else {
      onToken(result.content);
      onDone?.();
    }
  };

  const handleSubmit = () => {
    if (!inputText.trim()) return;

  // Fire-and-forget server action to prepare invocation (no UI response handling needed)
  prepareInvokingLambda(inputText).catch(() => { /* intentionally ignore errors for UI */ });
    
    // Adding the modify deducing part
    const isModifiedMessages: ChatMessage[] = [
      {
        role: "system",
        content: "If the user is going to modify the cloud infrastructure project and is stated as a command that changes anything then respond with only MODIFY else respond with only NOMODIFY"
      },
      { role: "user", content: inputText }
    ]

    startTransition(async () => {
      try {
        // For lightweight classification a single full response is fine; reuse chatFn abstraction
        let classification = "";
        await runChat(
          chatFn as ChatFn,
          isModifiedMessages,
          (partial) => {
            classification = partial; // we only care about final token set
          }
        );
        setModifying(classification.trim() === "MODIFY");
      } catch {
        // Non-fatal for main response; just ignore classification errors
        setModifying(false);
      }
    });

    console.log("is modifying", modifying);

    const messages: ChatMessage[] = [
      {
        role: "system",
        content:
          "You are a helpful assistant that helps users build applications. Provide clear, actionable advice.",
      },
      { role: "user", content: inputText },
    ];

    startTransition(async () => {
      try {
        setResponse("");
        await runChat(chatFn as ChatFn, messages, (partial) => setResponse(partial));
      } catch {
        setResponse("Sorry, there was an error processing your request.");
      }
    });
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputText(suggestion);
  };

  return (
    <main className="flex flex-col items-center justify-center px-1 py-20 max-w-4xl mx-auto text-center">
      <h1 className="text-5xl md:text-6xl font-light text-gray-900 dark:text-white mb-8 leading-tight transition-colors">

        Your go to solution to <span className="text-orange-400 font-normal">conquering</span>
        <br />
        cloud infrastructure
      </h1>

      <p className="text-lg text-gray-700 dark:text-gray-300 mb-4 max-w-2xl transition-colors">
        OpsForge lets you build fully-functional projects in minutes with just your words.
      </p>
      <p className="text-lg text-gray-700 dark:text-gray-300 mb-12 transition-colors">
        No coding necessary.
      </p>

      {/* Search Box */}
      <div className="w-full max-w-3xl bg-white dark:bg-gray-800 rounded-2xl shadow-lg dark:shadow-gray-900/20 p-6 mb-8 transition-colors">
        <div className="flex items-center gap-4 mb-6">
          <Input
            placeholder="What do you want to build?"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isStreaming && handleSubmit()}
            className="flex-1 border-0 text-lg placeholder:text-gray-400 dark:placeholder:text-gray-500 focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent dark:text-white"
          />
          <Button
            size="icon"
            onClick={handleSubmit}
            disabled={isStreaming || !inputText.trim()}
            className="bg-orange-500 hover:bg-orange-600 disabled:opacity-50 rounded-xl"
          >
            <ArrowUp className="w-5 h-5" />
          </Button>
        </div>

        <div className="text-left">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 transition-colors">
            Not sure where to start? Try one of these:
          </p>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                handleSuggestionClick("Create a VPC in the Virgina region")
              }
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Create a VPC 
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                handleSuggestionClick("Read S3 contents in us-east-1")
              }
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Read S3 Contents 
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSuggestionClick("Configure Route 53 records without interupting endpoints")}
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Configure Route 53 Records
            </Button>             
          </div>
        </div>
      </div>

      {/* Response Display */}
      {(response || isStreaming) && (
        <div className="w-full max-w-3xl bg-white dark:bg-gray-800 rounded-2xl shadow-lg dark:shadow-gray-900/20 p-6 mb-8 transition-colors">
          <div className="text-left">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              {isStreaming ? "Generating response..." : "Here’s what I suggest:"}
            </h3>
            <div className="prose prose-gray dark:prose-invert max-w-none">
              <p className="whitespace-pre-wrap text-gray-700 dark:text-gray-300">
                {response}
                {isStreaming && <span className="animate-pulse">▋</span>}
              </p>
            </div>
          </div>
        </div>
      )}

    </main>
  );
}
