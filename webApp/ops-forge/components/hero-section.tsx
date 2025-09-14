"use client";

import { useState, useTransition } from "react";
import { readStreamableValue } from "@ai-sdk/rsc"; // ⬅️ v5 import
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowUp } from "lucide-react";
import { streamGroqChat, type ChatMessage } from "@/actions/LLMS/llmActions";

export default function HeroSection() {
  const [inputText, setInputText] = useState("");
  const [response, setResponse] = useState("");
  const [modifying, setModifying] = useState(false);
  const [isStreaming, startTransition] = useTransition();

  const handleSubmit = () => {
    if (!inputText.trim()) return;
    
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
        const { output } = await streamGroqChat(isModifiedMessages);
        setModifying(false); // Clear previous response

        let accumulated = "";
        for await (const token of readStreamableValue(output)) {
          accumulated += token ?? "";
        }

        if (accumulated == "MODIFY") {
          setModifying(true)
        }

      } catch {
        setResponse("Sorry, there was an error processing your request.");
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
        const { output } = await streamGroqChat(messages);
        setResponse(""); // Clear previous response

        let accumulated = "";
        for await (const token of readStreamableValue(output)) {
          accumulated += token ?? "";
          setResponse(accumulated);
        }
      } catch {
        setResponse("Sorry, there was an error processing your request.");
      }
    });
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputText(suggestion);
  };

  return (
    <main className="flex flex-col items-center justify-center px-6 py-20 max-w-4xl mx-auto text-center">
      <h1 className="text-5xl md:text-6xl font-light text-gray-900 dark:text-white mb-8 leading-tight transition-colors">
        Let&apos;s make your dream a <span className="text-lime-400 font-normal">reality.</span>
        <br />
        Right now.
      </h1>

      <p className="text-lg text-gray-700 dark:text-gray-300 mb-4 max-w-2xl transition-colors">
        BuildFlow lets you build fully-functional apps in minutes with just your words.
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
                handleSuggestionClick("Build a reporting dashboard with charts and analytics")
              }
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Reporting Dashboard
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                handleSuggestionClick("Create a gaming platform with user profiles and leaderboards")
              }
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Gaming Platform
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSuggestionClick("Design an onboarding portal for new employees")}
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Onboarding Portal
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSuggestionClick("Build a networking app for professionals")}
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Networking App
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSuggestionClick("Create a room visualizer for interior design")}
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Room Visualizer
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
