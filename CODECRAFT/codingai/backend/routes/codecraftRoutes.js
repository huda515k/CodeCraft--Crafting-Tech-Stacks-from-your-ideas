import express from "express";
import multer from "multer";
import {
  generatePromptBackend,
  generatePromptFrontend,
  generateFrontendToBackend,
  streamAIOutput,
} from "../controllers/codecraftController.js";

const router = express.Router();
const upload = multer({ dest: "uploads/" });

// Routes
router.post("/prompt-backend", generatePromptBackend);
router.post("/prompt-frontend", generatePromptFrontend);
router.post("/frontend-backend", upload.single("file"), generateFrontendToBackend);
router.post("/stream", streamAIOutput);

export default router;
