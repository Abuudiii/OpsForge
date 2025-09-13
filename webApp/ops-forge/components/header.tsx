"use client"
import Logo from "../components/Logo"
import { Button } from "@/components/ui/button"
import { Sun, Moon } from "lucide-react"

interface HeaderProps {
  isDark: boolean
  toggleTheme: () => void
}

export default function Header({ isDark, toggleTheme }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
      <div className="flex items-center gap-2">
        {/* <img src="icon.png" style={{width:"32px", height:"32px"}}></img> */}
        <Logo></Logo>
        <span className="text-xl font-semibold text-gray-900 dark:text-white">
          OpsForge
        </span>
      </div>
      
      <nav className="hidden md:flex items-center gap-8">
        <a
          href="#"
          className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white font-medium transition-colors"
        >
          Product
        </a>
        <a
          href="#"
          className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white font-medium transition-colors"
        >
          Resources
        </a>
        <a
          href="#"
          className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white font-medium transition-colors"
        >
          Pricing
        </a>
        <a
          href="#"
          className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white font-medium transition-colors"
        >
          Enterprise
        </a>
      </nav>
      
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </Button>
        <Button className="bg-lime-400 hover:bg-lime-500 text-gray-900 font-medium px-6">
          Start Building
        </Button>
      </div>
    </header>
  )
}