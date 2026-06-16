import React, { useState, useEffect } from "react"

const MESSAGES = [
  "Reading your offer letter...",
  "Extracting compensation details...",
  "Checking live market rates from database...",
  "Comparing with regional statistics...",
  "Crafting your tailored negotiation script...",
  "Almost there..."
]

export default function LoadingScreen() {
  const [msgIndex, setMsgIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setMsgIndex((prevIndex) => (prevIndex + 1) % MESSAGES.length)
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="fixed inset-0 bg-background flex flex-col justify-center items-center p-6 z-50 select-none">
      {/* Centered loader spinner */}
      <div className="relative w-24 h-24 mb-8">
        {/* Outer glowing ring */}
        <div className="absolute inset-0 border-4 border-border rounded-full"></div>
        {/* Inner animated spinning loader */}
        <div className="absolute inset-0 border-4 border-t-accent border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
      </div>

      {/* Rotating message */}
      <div className="h-8 flex items-center justify-center">
        <p className="text-lg md:text-xl text-textPrimary font-medium text-center tracking-wide transition-opacity duration-300 animate-pulse">
          {MESSAGES[msgIndex]}
        </p>
      </div>

      <p className="text-xs text-textSecondary mt-12 uppercase tracking-widest">
        OfferSense Analyzer
      </p>
    </div>
  )
}
