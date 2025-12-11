import React, { useState, useRef, useEffect } from "react";
import {
  ArrowUp,
  Paperclip,
  X,
  Loader2,
  ChevronDown,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function LovableUI() {
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);
  const [category, setCategory] = useState("Backend");
  const [archType, setArchType] = useState("Monolith");
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false);
  const [showArchDropdown, setShowArchDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const navigate = useNavigate();

  const categories = ["Backend", "Frontend", "Integration"];
  const architectures = ["Monolith", "Microservices"];

  const handleFileAttach = (e) => setFile(e.target.files?.[0] || null);
  const handleAttachClick = () => fileInputRef.current?.click();
  const handleRemoveFile = () => setFile(null);
  const handleInputChange = (e) => setMessage(e.target.value);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        180
      )}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (!message.trim()) return;
    navigate("/BuildWorkspace", {
      state: { prompt: message, category, archType },
    });
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-start py-10 bg-gradient-to-b from-indigo-50 via-white to-purple-50 text-center px-4 sm:px-6">
      <div className="flex items-center gap-2 bg-white/70 px-5 py-2 rounded-full shadow-sm mb-6">
        <span className="text-sm font-semibold text-gray-700">Live Build</span>
        <span className="text-sm text-gray-500">powered by CodeCrafter</span>
      </div>

      <h1 className="text-4xl sm:text-6xl font-extrabold text-gray-800 mb-4 leading-tight">
        Build Smarter, Code Faster ⚡
      </h1>
      <p className="text-gray-500 text-base sm:text-lg mb-8">
        Type your idea and let AI create your app.
      </p>

      <div className="w-full max-w-3xl bg-white/80 shadow-xl rounded-3xl p-4 sm:p-6 border border-white/40 backdrop-blur-lg transition-all">
        <div className="flex flex-col sm:flex-row items-end sm:items-center gap-3">
          <div className="flex-1 relative">
            {file && (
              <div className="flex items-center bg-gradient-to-r from-purple-100 to-pink-100 text-gray-700 text-sm rounded-md px-3 py-1 mb-2 w-fit shadow-sm border border-gray-200">
                <Paperclip className="w-4 h-4 mr-2 text-gray-500" />
                <span className="truncate max-w-[200px]">{file.name}</span>
                <button onClick={handleRemoveFile} className="ml-2 hover:text-red-500">
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleInputChange}
              placeholder={`Ask AI to create a ${category.toLowerCase()} for my...`}
              className="w-full resize-none text-gray-700 text-base sm:text-lg focus:outline-none placeholder-gray-400 bg-transparent border border-gray-200 rounded-xl p-3 shadow-inner focus:ring-2 focus:ring-indigo-400 transition-all"
              style={{ minHeight: "48px" }}
            />
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleAttachClick}
              className="p-2 hover:bg-indigo-100 text-indigo-600 rounded-full hover:cursor-pointer"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileAttach} />

            <button
              onClick={handleSend}
              className="p-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:opacity-90 rounded-full text-white transition shadow-md flex items-center justify-center hover:cursor-pointer"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ArrowUp className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* category + architecture */}
        <div className="flex flex-wrap gap-3 mt-4">
          <div className="relative">
            <button
              onClick={() => setShowCategoryDropdown(!showCategoryDropdown)}
              className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium px-3 py-2 rounded-full border border-gray-200 shadow-sm hover:cursor-pointer"
            >
              {category}
              <ChevronDown className="w-4 h-4 text-gray-500" />
            </button>
            {showCategoryDropdown && (
              <div className="absolute z-10 mt-2 w-36 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden text-left">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => {
                      setCategory(cat);
                      setShowCategoryDropdown(false);
                    }}
                    className={`block w-full px-4 py-2 text-sm hover:bg-indigo-50 ${
                      cat === category ? "bg-indigo-100 font-semibold" : ""
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            )}
          </div>

          {(category === "Backend" || category === "Integration") && (
            <div className="relative">
              <button
                onClick={() => setShowArchDropdown(!showArchDropdown)}
                className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium px-3 py-2 rounded-full border border-gray-200 shadow-sm  hover:cursor-pointer " 
              >
                {archType}
                <ChevronDown className="w-4 h-4 text-gray-500" />
              </button>
              {showArchDropdown && (
                <div className="absolute z-10 mt-2 w-40 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden text-left">
                  {architectures.map((arch) => (
                    <button
                      key={arch}
                      onClick={() => {
                        setArchType(arch);
                        setShowArchDropdown(false);
                      }}
                      className={`block w-full px-4 py-2 text-sm hover:bg-indigo-50 ${
                        arch === archType ? "bg-indigo-100 font-semibold" : ""
                      }`}
                    >
                      {arch}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
