"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ArrowUp } from "lucide-react"

export default function HeroSection() {
  return (
    <main className="flex flex-col items-center justify-center px-6 py-20 max-w-4xl mx-auto text-center">
      <h1 className="text-5xl md:text-6xl font-light text-gray-900 dark:text-white mb-8 leading-tight transition-colors">
        Let's make your dream a{" "}
        <span className="text-lime-400 font-normal">reality.</span>
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
            className="flex-1 border-0 text-lg placeholder:text-gray-400 dark:placeholder:text-gray-500 focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent dark:text-white"
          />
          <Button size="icon" className="bg-orange-500 hover:bg-orange-600 rounded-xl">
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
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Reporting Dashboard
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Gaming Platform
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Onboarding Portal
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Networking App
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="rounded-full text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Room Visualizer
            </Button>
          </div>
        </div>
      </div>

      {/* Trust Indicators */}
      <div className="flex items-center gap-3">
        <div className="flex -space-x-2">
          <div className="w-8 h-8 bg-blue-500 rounded-full border-2 border-white dark:border-gray-800"></div>
          <div className="w-8 h-8 bg-green-500 rounded-full border-2 border-white dark:border-gray-800"></div>
          <div className="w-8 h-8 bg-purple-500 rounded-full border-2 border-white dark:border-gray-800"></div>
        </div>
        <span className="text-gray-700 dark:text-gray-300 font-medium transition-colors">
          Trusted by 400K+ users
        </span>
      </div>
    </main>
  )
}