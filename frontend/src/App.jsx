import { useState } from "react"

export default function App() {
  const [page, setPage] = useState("landing") // landing | input | loading | results
  const [results, setResults] = useState(null)

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#FAFAFA] flex flex-col items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-5xl font-extrabold text-accent mb-4">OfferSense</h1>
        <p className="text-xl text-textSecondary mb-8">Know your worth. Negotiate with confidence.</p>
        <div className="p-6 bg-surface border border-border rounded-xl">
          <p className="text-success font-semibold">Frontend setup successfully initialized with Tailwind CSS!</p>
          <p className="text-sm text-textSecondary mt-2">Currently on page state: <code className="text-accent">{page}</code></p>
        </div>
      </div>
    </div>
  )
}
