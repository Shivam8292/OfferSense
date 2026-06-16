import React from "react"

export default function LandingPage({ onStart }) {
  return (
    <div className="min-h-screen bg-background text-textPrimary flex flex-col justify-between p-6 md:p-12 font-sans select-none">
      {/* Brand logo/name */}
      <div className="flex justify-start">
        <span className="text-2xl font-bold tracking-tight text-accent">OfferSense</span>
      </div>

      {/* Hero Section */}
      <div className="max-w-4xl mx-auto my-auto text-center flex flex-col items-center">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-tight mb-6">
          Know your worth.
        </h1>
        <p className="text-lg md:text-2xl text-textSecondary font-medium max-w-2xl mb-8 leading-relaxed">
          Don't leave money on the table. Analyze your offer letter in 30 seconds. Get market benchmarks and step-by-step negotiation guidance.
        </p>
        <button
          onClick={onStart}
          className="px-8 py-4 bg-accent hover:bg-indigo-500 active:bg-indigo-700 transition duration-200 text-white font-bold text-lg rounded-lg shadow-sm border border-transparent"
        >
          Analyze My Offer
        </button>
      </div>

      {/* Feature / Benefit Cards */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-12 md:mt-0">
        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-accent mb-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-2">Dual Input Mode</h3>
          <p className="text-textSecondary text-sm leading-relaxed">
            Upload your offer letter PDF for auto-extraction, or enter your details manually.
          </p>
        </div>

        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-accent mb-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-2">Market Salary Data</h3>
          <p className="text-textSecondary text-sm leading-relaxed">
            Compare your compensation against live market benchmarks filtered by role, experience, and location.
          </p>
        </div>

        <div className="p-6 bg-surface border border-border rounded-xl">
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-accent mb-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-2">Negotiation Scripts</h3>
          <p className="text-textSecondary text-sm leading-relaxed">
            Get word-for-word email templates and verbal scripts to speak confidently with HR.
          </p>
        </div>
      </div>

      {/* Footer copyright */}
      <div className="text-center text-xs text-textSecondary mt-8 md:mt-4">
        © {new Date().getFullYear()} OfferSense. All rights reserved.
      </div>
    </div>
  )
}
