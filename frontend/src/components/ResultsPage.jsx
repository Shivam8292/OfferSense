import React, { useState } from "react"

export default function ResultsPage({ results, onReset }) {
  const [activeScriptTab, setActiveScriptTab] = useState("email") // email | verbal
  const [toastMsg, setToastMsg] = useState("")

  if (!results) return null

  const { extracted, market, verdict, counter_offer, script } = results

  const userCTC = extracted.ctc_lpa || 0
  const avgCTC = market.avg_ctc || 0
  const topCTC = market.p75_ctc || (avgCTC * 1.3)
  const maxVal = Math.max(userCTC, avgCTC, topCTC) || 1

  const userWidth = `${(userCTC / maxVal) * 100}%`
  const avgWidth = `${(avgCTC / maxVal) * 100}%`
  const topWidth = `${(topCTC / maxVal) * 100}%`

  // Decide colors based on negotiation verdict
  let userBarColor = "bg-success" // Green
  let verdictBorderColor = "border-success"
  let verdictBgColor = "bg-success/5"
  let verdictTextColor = "text-success"
  let verdictLabel = "✅ Fair Offer"

  if (verdict.should_negotiate) {
    const isSigUnder = Math.abs(verdict.percentage_diff || 0) >= 20
    userBarColor = isSigUnder ? "bg-danger" : "bg-warning" // Red or Amber
    verdictBorderColor = isSigUnder ? "border-danger" : "border-warning"
    verdictBgColor = isSigUnder ? "bg-danger/5" : "bg-warning/5"
    verdictTextColor = isSigUnder ? "text-danger" : "text-warning"
    verdictLabel = isSigUnder ? "🚨 Significantly Under Market" : "⚠️ Slightly Under Market"
  }

  // Toast helper
  const showToast = (msg) => {
    setToastMsg(msg)
    setTimeout(() => {
      setToastMsg("")
    }, 2500)
  }

  const handleCopy = (text, typeLabel) => {
    navigator.clipboard.writeText(text)
    showToast(`${typeLabel} copied to clipboard!`)
  }

  const handleShare = () => {
    const pctLabel = verdict.should_negotiate 
      ? `${Math.abs(verdict.percentage_diff)}% under market` 
      : `${Math.abs(verdict.percentage_diff)}% above market`
    
    const shareText = `I used OfferSense to analyze my job offer as a ${extracted.role} at ${extracted.company} — I was ${pctLabel}! Check if your offer is fair: http://offersense.vercel.app #SalaryNegotiation #Freshers #Careers`
    
    navigator.clipboard.writeText(shareText)
    showToast("Share text copied! Post it on LinkedIn/Twitter.")
  }

  return (
    <div className="min-h-screen bg-background text-textPrimary py-12 px-6 md:px-12 font-sans relative">
      
      {/* Toast Notification */}
      {toastMsg && (
        <div className="fixed bottom-8 right-8 bg-[#1E1E24] border border-accent text-accent px-5 py-3 rounded-lg shadow-lg text-sm font-semibold flex items-center gap-2 animate-bounce z-50">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
          {toastMsg}
        </div>
      )}

      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Top Header */}
        <div className="flex justify-between items-center border-b border-border pb-4">
          <span className="text-xl font-bold tracking-tight text-accent">OfferSense</span>
          <button
            onClick={onReset}
            className="px-4 py-2 border border-border text-sm font-semibold rounded-lg hover:bg-surface transition duration-150"
          >
            Analyze Another Offer
          </button>
        </div>

        {/* Block 1 — Offer Summary */}
        <div className="bg-surface border border-border p-6 rounded-xl grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-[10px] uppercase font-bold tracking-wider text-textSecondary mb-1">Position</p>
            <p className="text-lg font-bold text-textPrimary truncate">{extracted.role}</p>
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold tracking-wider text-textSecondary mb-1">Company</p>
            <p className="text-lg font-bold text-textPrimary truncate">{extracted.company}</p>
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold tracking-wider text-textSecondary mb-1">Location</p>
            <p className="text-lg font-bold text-textPrimary">{extracted.city}</p>
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold tracking-wider text-textSecondary mb-1">Offered CTC</p>
            <p className="text-lg font-extrabold text-accent">₹{userCTC} LPA</p>
          </div>
        </div>

        {/* Block 2 — Market Comparison Chart (SIGNATURE ELEMENT) */}
        <div className="bg-surface border border-border p-6 rounded-xl space-y-6">
          <h3 className="text-sm font-bold uppercase tracking-wider text-textSecondary">Market Comparison</h3>
          
          <div className="space-y-4">
            {/* Bar 1: Your Offer */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-textPrimary">Your Offer</span>
                <span className="font-extrabold">₹{userCTC} LPA</span>
              </div>
              <div className="w-full bg-[#1E1E1E] h-8 rounded-md overflow-hidden flex items-center">
                <div 
                  className={`h-full ${userBarColor} transition-all duration-500 ease-out`}
                  style={{ width: userWidth }}
                ></div>
              </div>
            </div>

            {/* Bar 2: Market Average */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-textSecondary">Market Average (AmbitionBox)</span>
                <span className="font-extrabold text-textSecondary">₹{avgCTC} LPA</span>
              </div>
              <div className="w-full bg-[#1E1E1E] h-8 rounded-md overflow-hidden flex items-center">
                <div 
                  className="h-full bg-textSecondary transition-all duration-500 ease-out"
                  style={{ width: avgWidth }}
                ></div>
              </div>
            </div>

            {/* Bar 3: Top 25% Earners */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-textSecondary">Top 25% Earners</span>
                <span className="font-extrabold text-textSecondary">₹{topCTC} LPA</span>
              </div>
              <div className="w-full bg-[#1E1E1E] h-8 rounded-md overflow-hidden flex items-center">
                <div 
                  className="h-full bg-accent transition-all duration-500 ease-out"
                  style={{ width: topWidth }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Block 3 — Verdict Card */}
        <div className={`border ${verdictBorderColor} ${verdictBgColor} p-6 rounded-xl space-y-3`}>
          <h4 className={`text-lg font-bold ${verdictTextColor} flex items-center gap-2`}>
            {verdictLabel}
          </h4>
          <p className="text-textPrimary text-sm leading-relaxed">
            {verdict.reasoning}
          </p>
        </div>

        {/* Block 4 — Counter Offer (if applicable) */}
        {counter_offer.suggested_ctc && (
          <div className="bg-surface border border-border p-6 rounded-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <p className="text-xs font-bold text-textSecondary uppercase tracking-wider mb-1">Recommended Counter Ask</p>
              <h3 className="text-3xl font-extrabold text-success">₹{counter_offer.suggested_ctc} LPA</h3>
            </div>
            <div className="max-w-md bg-background/50 border border-border p-4 rounded-lg">
              <p className="text-xs text-textSecondary italic leading-relaxed">
                {counter_offer.rationale}
              </p>
            </div>
          </div>
        )}

        {/* Block 5 — Negotiation Script */}
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <div className="flex border-b border-border bg-[#1A1A1A]">
            <button
              onClick={() => setActiveScriptTab("email")}
              className={`flex-1 py-4 text-center text-xs font-bold uppercase tracking-wider transition-colors duration-150 ${
                activeScriptTab === "email"
                  ? "bg-surface text-accent border-t-2 border-accent"
                  : "text-textSecondary hover:text-textPrimary"
              }`}
            >
              📧 Email Template
            </button>
            <button
              onClick={() => setActiveScriptTab("verbal")}
              className={`flex-1 py-4 text-center text-xs font-bold uppercase tracking-wider transition-colors duration-150 ${
                activeScriptTab === "verbal"
                  ? "bg-surface text-accent border-t-2 border-accent"
                  : "text-textSecondary hover:text-textPrimary"
              }`}
            >
              🗣️ Verbal Talking Points
            </button>
          </div>

          <div className="p-6 space-y-4">
            {activeScriptTab === "email" ? (
              <div className="space-y-4">
                <div className="bg-background border border-border p-4 rounded-lg relative">
                  <pre className="text-xs font-mono text-textPrimary leading-relaxed whitespace-pre-wrap select-all max-h-96 overflow-y-auto">
                    {script.email || "Email script template not available."}
                  </pre>
                </div>
                <div className="flex justify-end">
                  <button
                    onClick={() => handleCopy(script.email, "Email template")}
                    className="px-5 py-2.5 bg-accent hover:bg-indigo-500 active:bg-indigo-700 transition duration-150 text-white text-xs font-bold rounded-lg flex items-center gap-2"
                  >
                    Copy Email Template
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-background border border-border p-4 rounded-lg relative">
                  <pre className="text-xs font-mono text-textPrimary leading-relaxed whitespace-pre-wrap select-all max-h-96 overflow-y-auto">
                    {script.verbal || "Verbal talking points not available."}
                  </pre>
                </div>
                <div className="flex justify-end">
                  <button
                    onClick={() => handleCopy(script.verbal, "Verbal tips")}
                    className="px-5 py-2.5 bg-accent hover:bg-indigo-500 active:bg-indigo-700 transition duration-150 text-white text-xs font-bold rounded-lg flex items-center gap-2"
                  >
                    Copy Verbal Points
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Block 6 — Actions */}
        <div className="flex flex-col md:flex-row gap-4 justify-between items-center bg-surface/50 border border-border p-6 rounded-xl">
          <div>
            <h4 className="text-sm font-bold text-textPrimary">Help others know their worth!</h4>
            <p className="text-xs text-textSecondary">Share your results summary anonymously or support the community.</p>
          </div>
          <button
            onClick={handleShare}
            className="w-full md:w-auto px-6 py-3 bg-[#1D9BF0] hover:opacity-90 transition duration-150 text-white font-bold rounded-lg text-sm flex items-center justify-center gap-2"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
            </svg>
            Share on LinkedIn
          </button>
        </div>

      </div>
    </div>
  )
}
