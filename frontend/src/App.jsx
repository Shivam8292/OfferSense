import React, { useState } from "react"
import LandingPage from "./components/LandingPage"
import InputPage from "./components/InputPage"
import LoadingScreen from "./components/LoadingScreen"
import ResultsPage from "./components/ResultsPage"

export default function App() {
  const [page, setPage] = useState("landing") // landing | input | results
  const [results, setResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#FAFAFA] font-sans selection:bg-accent selection:text-white">
      {page === "landing" && (
        <LandingPage onStart={() => setPage("input")} />
      )}
      {page === "input" && (
        <InputPage
          isLoading={isLoading}
          setIsLoading={setIsLoading}
          onResult={(data) => {
            setResults(data)
            setPage("results")
          }}
        />
      )}
      {isLoading && (
        <LoadingScreen />
      )}
      {page === "results" && (
        <ResultsPage
          results={results}
          onReset={() => {
            setResults(null)
            setPage("input")
          }}
        />
      )}
    </div>
  )
}
