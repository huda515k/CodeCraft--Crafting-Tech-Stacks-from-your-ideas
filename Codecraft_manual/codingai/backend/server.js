import express from "express";
import multer from "multer";
import cors from "cors";
import axios from "axios";
import FormData from "form-data";

const app = express();
const upload = multer(); // in-memory
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// FastAPI backend base URL
const FASTAPI_URL = "http://127.0.0.1:8002";

/**
 * Universal CodeCraft Streaming Endpoint
 * Handles: Backend, Frontend, and Integration
 */
app.post("/api/codecraft/stream", upload.single("file"), async (req, res) => {
  try {
    const { specs, mode, arch_type } = req.body;

    // build multipart form
    const formData = new FormData();
    formData.append("specs", specs || "");
    formData.append("mode", mode || "backend");
    formData.append("arch_type", arch_type || "Monolith");
    if (req.file)
      formData.append("file", req.file.buffer, {
        filename: req.file.originalname || "upload.zip",
      });

    // send to FastAPI and pipe response as stream
    const response = await axios.post(
      `${FASTAPI_URL}/api/generate/stream`,
      formData,
      {
        responseType: "stream",
        headers: formData.getHeaders(),
      }
    );

    // forward the text stream to frontend
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    response.data.pipe(res);

    response.data.on("end", () => {
      console.log("✅ Stream finished successfully.");
      res.end();
    });

    response.data.on("error", (err) => {
      console.error("❌ Stream error:", err.message);
      if (!res.headersSent) {
        res.status(500).json({ error: "Upstream stream error" });
      } else res.end();
    });
  } catch (err) {
    console.error("❌ Proxy error:", err.message);
    if (!res.headersSent)
      res.status(500).json({ error: "Proxy stream failed" });
    else res.end();
  }
});

// 🏠 Root endpoint - API info
app.get("/", (req, res) => {
  res.json({
    message: "✅ CodeCraft Proxy Server Running",
    version: "1.0.0",
    endpoints: {
      stream: "POST /api/codecraft/stream",
      download: "GET /api/download/:filename"
    },
    backend: FASTAPI_URL,
    status: "operational"
  });
});

// ✅ Proxy for ZIP downloads
app.get("/api/download/:filename", async (req, res) => {
  const { filename } = req.params;
  const targetUrl = `${FASTAPI_URL}/api/download/${filename}`;

  try {
    const response = await axios.get(targetUrl, { responseType: "stream" });

    res.setHeader(
      "Content-Disposition",
      `attachment; filename="${filename}"`
    );
    res.setHeader("Content-Type", "application/zip");

    response.data.pipe(res);

    response.data.on("end", () => {
      console.log(`✅ File ${filename} downloaded successfully.`);
    });
  } catch (error) {
    console.error("❌ Download proxy error:", error.message);
    res.status(500).send("Failed to fetch ZIP from FastAPI");
  }
});


app.listen(4002, "0.0.0.0", () =>
  console.log("🚀 Node proxy running at http://0.0.0.0:4002")
);