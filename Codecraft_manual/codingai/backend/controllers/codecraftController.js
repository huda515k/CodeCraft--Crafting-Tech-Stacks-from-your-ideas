import axios from "axios";
import FormData from "form-data";
import fs from "fs";

/**
 * 🧠 Base FastAPI endpoint
 */
const FASTAPI_BASE = "http://127.0.0.1:5000/api/generate";

/**
 * ============================================================
 * 1️⃣ Prompt → Backend (ZIP)
 * ============================================================
 */
export const generatePromptBackend = async (req, res) => {
  try {
    const { specs, arch_type } = req.body;
    if (!specs || !arch_type) {
      return res.status(400).json({ error: "Specs and arch_type are required" });
    }

    console.log("🚀 Sending backend prompt to FastAPI:", { specs, arch_type });

    const response = await axios.post(
      `${FASTAPI_BASE}/prompt-backend`,
      { specs, arch_type },
      { responseType: "arraybuffer" }
    );

    res.set({
      "Content-Type": "application/zip",
      "Content-Disposition": 'attachment; filename="generated_backend.zip"',
    });
    res.send(response.data);
  } catch (err) {
    console.error("❌ Error generating backend:", err.message);
    res.status(500).json({
      error: "Failed to generate backend",
      details: err.message,
    });
  }
};

/**
 * ============================================================
 * 2️⃣ Frontend ZIP → Backend (Integration)
 * ============================================================
 */
export const generateFrontendToBackend = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "Frontend ZIP file is required" });
    }

    const form = new FormData();
    form.append("arch_type", req.body.arch_type || "Monolith");
    form.append("file", fs.createReadStream(req.file.path));

    console.log("📦 Sending frontend ZIP to FastAPI:", req.file.path);

    const response = await axios.post(`${FASTAPI_BASE}/frontend-backend`, form, {
      headers: form.getHeaders(),
      responseType: "arraybuffer",
    });

    // Remove temp file
    fs.unlink(req.file.path, () => {});

    res.set({
      "Content-Type": "application/zip",
      "Content-Disposition": 'attachment; filename="frontend_to_backend.zip"',
    });
    res.send(response.data);
  } catch (err) {
    console.error("❌ Error generating backend from frontend:", err.message);
    res.status(500).json({
      error: "Failed to generate backend from frontend ZIP",
      details: err.message,
    });
  }
};

/**
 * ============================================================
 * 3️⃣ Prompt → Frontend (ZIP or HTML)
 * ============================================================
 */
export const generatePromptFrontend = async (req, res) => {
  try {
    const { specs } = req.body;
    if (!specs) return res.status(400).json({ error: "Specs are required" });

    console.log("🎨 Sending frontend prompt to FastAPI:", specs);

    const response = await axios.post(
      `${FASTAPI_BASE}/prompt-frontend`,
      { specs },
      { responseType: "arraybuffer" }
    );

    res.set({
      "Content-Type": "application/zip",
      "Content-Disposition": 'attachment; filename="generated_frontend.zip"',
    });
    res.send(response.data);
  } catch (err) {
    console.error("❌ Error generating frontend:", err.message);
    res.status(500).json({
      error: "Failed to generate frontend",
      details: err.message,
    });
  }
};

/**
 * ============================================================
 * 4️⃣ Live Streaming (Prompt → Stream)
 * ============================================================
 */
export const streamAIOutput = async (req, res) => {
  try {
    const { specs, mode, arch_type } = req.body;
    if (!specs || !mode) {
      return res.status(400).json({ error: "Specs and mode are required" });
    }

    console.log(`🛰️ Starting stream from FastAPI (${mode})...`);

    const fastapiRes = await axios({
      method: "post",
      url: "http://127.0.0.1:5000/api/generate/stream",
      data: new URLSearchParams({ specs, mode, arch_type: arch_type || "Monolith" }),
      responseType: "stream",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    fastapiRes.data.on("data", (chunk) => {
      res.write(chunk.toString());
    });

    fastapiRes.data.on("end", () => {
      res.write("data: [END]\n\n");
      res.end();
      console.log("✅ Streaming completed.");
    });
  } catch (err) {
    console.error("❌ Stream error:", err.message);
    res.write(`data: [ERROR] ${err.message}\n\n`);
    res.end();
  }
};
