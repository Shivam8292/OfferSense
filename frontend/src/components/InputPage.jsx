import React, { useState, useRef } from "react"

const API_BASE_URL = "http://localhost:8000"

export default function InputPage({ isLoading, setIsLoading, onResult }) {
  const [activeTab, setActiveTab] = useState("pdf") // pdf | manual
  const [errorMsg, setErrorMsg] = useState("")

  // Tab 1: PDF Upload State
  const [selectedFile, setSelectedFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  // Tab 2: Manual Input State
  const [formData, setFormData] = useState({
    role: "",
    company: "",
    city: "Bangalore",
    ctc_lpa: "",
    experience_years: ""
  })

  // PDF Upload Handlers
  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === "application/pdf") {
        setSelectedFile(file)
        setErrorMsg("")
      } else {
        setErrorMsg("Only PDF files are accepted.")
      }
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type === "application/pdf") {
        setSelectedFile(file)
        setErrorMsg("")
      } else {
        setErrorMsg("Only PDF files are accepted.")
      }
    }
  }

  const triggerFileSelect = () => {
    fileInputRef.current.click()
  }

  // Manual Input Handler
  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }))
  }

  // Submit Handler
  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg("")
    setIsLoading(true)

    try {
      if (activeTab === "pdf") {
        if (!selectedFile) {
          setErrorMsg("Please select or drop an offer letter PDF first.")
          setIsLoading(false)
          return
        }

        const data = new FormData()
        data.append("file", selectedFile)

        const response = await fetch(`${API_BASE_URL}/analyze/pdf`, {
          method: "POST",
          body: data
        })

        if (!response.ok) {
          const errData = await response.json()
          throw new Error(errData.detail || "PDF extraction failed. Please try manual entry.")
        }

        const result = await response.json()
        setIsLoading(false)
        onResult(result)

      } else {
        // Manual Submission
        const { role, company, city, ctc_lpa, experience_years } = formData
        if (!role || !company || !city || !ctc_lpa || experience_years === "") {
          throw new Error("All form fields are required.")
        }

        const payload = {
          role,
          company,
          city,
          ctc_lpa: parseFloat(ctc_lpa),
          experience_years: parseInt(experience_years)
        }

        const response = await fetch(`${API_BASE_URL}/analyze/manual`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        })

        if (!response.ok) {
          const errData = await response.json()
          throw new Error(errData.detail || "Analysis failed. Please check your inputs.")
        }

        const result = await response.json()
        setIsLoading(false)
        onResult(result)
      }
    } catch (err) {
      setErrorMsg(err.message || "An unexpected error occurred.")
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background text-textPrimary flex flex-col justify-center items-center p-6 font-sans">
      <div className="w-full max-w-lg">
        {/* Brand / Home Link */}
        <h2 className="text-3xl font-extrabold tracking-tight text-center text-accent mb-2">OfferSense</h2>
        <p className="text-center text-textSecondary text-sm mb-8">Enter your details to calculate market fit</p>

        {/* Error Box */}
        {errorMsg && (
          <div className="mb-6 p-4 bg-danger/10 border border-danger text-danger text-sm rounded-lg flex items-center gap-3">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Tab Controls */}
        <div className="flex border-b border-border mb-6">
          <button
            onClick={() => { setActiveTab("pdf"); setErrorMsg("") }}
            className={`flex-1 pb-3 text-center font-bold border-b-2 text-sm transition duration-150 ${
              activeTab === "pdf"
                ? "border-accent text-accent"
                : "border-transparent text-textSecondary hover:text-textPrimary"
            }`}
          >
            Upload PDF
          </button>
          <button
            onClick={() => { setActiveTab("manual"); setErrorMsg("") }}
            className={`flex-1 pb-3 text-center font-bold border-b-2 text-sm transition duration-150 ${
              activeTab === "manual"
                ? "border-accent text-accent"
                : "border-transparent text-textSecondary hover:text-textPrimary"
            }`}
          >
            Enter Manually
          </button>
        </div>

        {/* Form Wrap */}
        <form onSubmit={handleSubmit} className="bg-surface border border-border p-6 rounded-xl">
          {activeTab === "pdf" ? (
            /* Tab 1: PDF Upload */
            <div className="space-y-6">
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={triggerFileSelect}
                className={`w-full py-12 px-4 border-2 border-dashed rounded-lg flex flex-col items-center justify-center cursor-pointer transition duration-150 ${
                  dragActive ? "border-accent bg-accent/5" : "border-border hover:border-textSecondary"
                }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="application/pdf"
                  className="hidden"
                />

                <svg className="w-12 h-12 text-textSecondary mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                </svg>

                {selectedFile ? (
                  <div className="text-center">
                    <p className="text-sm font-semibold text-textPrimary mb-1">Selected File:</p>
                    <p className="text-xs text-accent truncate max-w-xs">{selectedFile.name}</p>
                    <p className="text-[10px] text-textSecondary mt-1">Click or drag another to change</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="text-sm font-semibold">Drop your offer letter PDF here</p>
                    <p className="text-xs text-textSecondary mt-1">or click to browse from files</p>
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={!selectedFile}
                className="w-full py-3 bg-accent disabled:opacity-50 hover:bg-indigo-500 active:bg-indigo-700 transition duration-150 text-white font-bold rounded-lg"
              >
                Analyze Offer Letter
              </button>
            </div>
          ) : (
            /* Tab 2: Manual Entry Form */
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-textSecondary uppercase tracking-wider mb-2">Job Role</label>
                <input
                  type="text"
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  placeholder="e.g. Software Engineer"
                  required
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg text-textPrimary placeholder-textSecondary/50 focus:outline-none focus:border-accent text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-textSecondary uppercase tracking-wider mb-2">Company Name</label>
                <input
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleInputChange}
                  placeholder="e.g. TCS"
                  required
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg text-textPrimary placeholder-textSecondary/50 focus:outline-none focus:border-accent text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-textSecondary uppercase tracking-wider mb-2">City</label>
                  <select
                    name="city"
                    value={formData.city}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-background border border-border rounded-lg text-textPrimary focus:outline-none focus:border-accent text-sm appearance-none"
                  >
                    <option value="Bangalore">Bangalore</option>
                    <option value="Mumbai">Mumbai</option>
                    <option value="Delhi">Delhi</option>
                    <option value="Hyderabad">Hyderabad</option>
                    <option value="Pune">Pune</option>
                    <option value="Chennai">Chennai</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-textSecondary uppercase tracking-wider mb-2">Experience (Years)</label>
                  <input
                    type="number"
                    name="experience_years"
                    value={formData.experience_years}
                    onChange={handleInputChange}
                    placeholder="e.g. 0 for fresher"
                    min="0"
                    max="40"
                    required
                    className="w-full px-4 py-3 bg-background border border-border rounded-lg text-textPrimary placeholder-textSecondary/50 focus:outline-none focus:border-accent text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-textSecondary uppercase tracking-wider mb-2">CTC Offered (LPA)</label>
                <input
                  type="number"
                  step="0.1"
                  name="ctc_lpa"
                  value={formData.ctc_lpa}
                  onChange={handleInputChange}
                  placeholder="e.g. 6.5"
                  min="0.5"
                  max="100"
                  required
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg text-textPrimary placeholder-textSecondary/50 focus:outline-none focus:border-accent text-sm"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 bg-accent hover:bg-indigo-500 active:bg-indigo-700 transition duration-150 text-white font-bold rounded-lg text-sm mt-2"
              >
                Analyze Offer
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
