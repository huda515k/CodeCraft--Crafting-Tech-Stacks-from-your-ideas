// BuildWorkspace.jsx
import React, { useEffect, useState, useRef } from "react";
import { useLocation } from "react-router-dom";
import { Loader2, Terminal, Globe, Download } from "lucide-react";

export default function BuildWorkspace() {
  const { state } = useLocation();
  const { prompt, category, archType } = state || {};

  const [logs, setLogs] = useState("");
  const [previewUrl, setPreviewUrl] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const hasRun = useRef(false);
  const consoleRef = useRef(null);

  // 🔄 Auto-scroll to bottom when logs update
  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    async function fetchBuild() {
      setLoading(true);
      setLogs("🚀 Initializing AI Build Console...\n");

      try {
        const formData = new FormData();
        formData.append("specs", prompt);
        formData.append("mode", category?.toLowerCase() || "frontend");
        formData.append("arch_type", archType || "Monolith");

        const response = await fetch("http://localhost:4000/api/codecraft/stream", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        if (!response.body) throw new Error("No stream body received");

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        // 🧠 Continuous stream reading loop
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          if (!chunk.trim()) continue;

          // ✅ Append chunk directly
          setLogs((prev) => prev + chunk);

          // 🧩 Parse special links
          if (chunk.includes("__ZIP_LINK__")) {
            const regex = /__ZIP_LINK__\s*(\{.*?\})/gs;
            for (const match of chunk.matchAll(regex)) {
              try {
                const data = JSON.parse(match[1]);
                if (data.download_url) setDownloadUrl(data.download_url);
                if (data.preview_url) setPreviewUrl(data.preview_url);
              } catch (err) {
                console.warn("⚠️ Invalid __ZIP_LINK__ JSON:", err);
              }
            }
          }
        }
      } catch (err) {
        console.error("❌ Stream error:", err);
        setLogs((prev) => prev + `\n❌ Error: ${err.message}\n`);
      } finally {
        setLoading(false);
      }
    }

    fetchBuild();
  }, [prompt, category, archType]);

  return (
    <div className="min-h-screen flex flex-col sm:flex-row bg-gradient-to-br from-gray-900 via-indigo-900 to-purple-900 text-white">
      {/* 🖥️ Console */}
      <div className="w-full sm:w-1/2 border-r border-white/10 p-6 sm:p-10 overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Terminal className="w-6 h-6 text-green-400" /> AI Build Console
        </h2>

        <p className="text-sm text-gray-300 mb-4">{prompt}</p>

        {/* Terminal box */}
        <div
          ref={consoleRef}
          className="bg-[#0a0a0a]/80 text-green-300 font-mono rounded-xl max-h-[80vh] overflow-y-auto shadow-inner border border-white/10"
        >
          {/* keep padding inside so code isn’t glued to edge */}
          <div className="p-4">
            <pre
              key={logs.length}
              className="text-sm font-mono"
              style={{
                whiteSpace: "pre-wrap",
                tabSize: 2,
                lineHeight: 1.5,
                overflowWrap: "break-word",
                wordBreak: "break-word",
              }}
            >
              <code>{logs || "Initializing build..."}</code>
            </pre>

            {downloadUrl && (
              <a
                href={downloadUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 mt-4 bg-blue-600 px-5 py-2 rounded-full text-white hover:bg-blue-700 transition"
              >
                <Download className="w-5 h-5" /> Download ZIP
              </a>
            )}
          </div>
        </div>

        <div className="text-xs text-gray-400 mt-3">
          {loading ? "🟢 Streaming in progress..." : "✅ Stream finished"}
        </div>
      </div>

      {/* 🌐 Preview */}
      <div className="w-full sm:w-1/2 flex items-center justify-center bg-white/10 backdrop-blur-xl p-4 sm:p-8">
        {previewUrl ? (
          <iframe
            src="http://localhost:5174"
            title="Live Preview"
            className="w-full h-[90vh] rounded-2xl border border-white/20 shadow-2xl bg-white"
          />
        ) : (
          <div className="flex flex-col items-center gap-4">
            {loading ? (
              <>
                <Globe className="w-12 h-12 text-indigo-400 animate-pulse" />
                <p className="text-lg text-gray-200">Running your build...</p>
                <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
              </>
            ) : (
              <>
                <Globe className="w-12 h-12 text-gray-400" />
                <p className="text-lg text-gray-300">No preview available</p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
