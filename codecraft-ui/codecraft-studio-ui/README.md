# CodeCraft Studio UI

A modern, chat-based UI for CodeCraft - AI-Powered Code Generation Platform.

## Features

- 💬 **Chat Interface** - Natural conversation flow for code generation
- 🎨 **Modern Design** - Built with shadcn/ui and Tailwind CSS
- 🌓 **Theme Support** - Light and dark mode with persistent preferences
- 📦 **Multiple Modules** - Support for all CodeCraft modules:
  - Frontend to Backend
  - Backend to Frontend
  - ERD to Backend
  - Prompt to Backend (with real-time streaming)
  - Prompt to Frontend
  - UI to Frontend
- 📝 **Code Preview** - Real-time code preview with file tabs
- 📥 **Download Support** - Download generated projects as ZIP files
- ⚙️ **Settings** - Customize theme and profile
- 👤 **User Profile** - View and manage your profile

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm/bun
- CodeCraft backend running on `http://localhost:8000`

### Installation

1. **Navigate to the studio UI directory:**
```bash
cd codecraft-ui/codecraft-studio-ui
```

2. **Install dependencies:**
```bash
npm install
# or
bun install
```

3. **Create a `.env` file (optional):**
```env
VITE_API_URL=http://localhost:8000
```

4. **Start the development server:**
```bash
npm run dev
# or
bun run dev
```

5. **Open your browser:**
Navigate to `http://localhost:8080`

## Usage

1. **Select a Module** - Choose from the available modules at the top
2. **Enter Your Prompt** - Describe what you want to build
3. **Upload Files** (if required) - Drag and drop or click to upload
4. **Generate** - Click send or press Enter
5. **Preview Code** - View generated code in the right panel
6. **Download** - Click "Download ZIP" to get the complete project

## Available Modules

### Frontend to Backend
Upload a frontend ZIP file to generate a backend API.

### Backend to Frontend
Upload a backend ZIP file to generate frontend code (coming soon).

### ERD to Backend
Upload an ERD image to generate a complete backend.

### Prompt to Backend
Enter a natural language prompt to generate backend code with real-time streaming.

### Prompt to Frontend
Enter a natural language prompt to generate frontend code (coming soon).

### UI to Frontend
Upload UI design images to generate frontend React code. Supports multiple screens.

## Project Structure

```
codecraft-studio-ui/
├── src/
│   ├── components/      # UI components (shadcn/ui)
│   ├── contexts/        # React contexts (Theme)
│   ├── pages/          # Page components
│   ├── services/       # API service layer
│   ├── types/          # TypeScript types
│   ├── data/           # Constants and configuration
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Entry point
├── public/             # Static assets
├── index.html          # HTML template
└── package.json        # Dependencies
```

## Technology Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **React Router** for navigation
- **shadcn/ui** for UI components
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **TanStack Query** for data fetching

## API Integration

The UI communicates with the CodeCraft backend API. Make sure the backend is running and accessible at the configured API URL.

### API Endpoints Used

- `POST /nodegen/prompt-to-backend-stream` - Stream backend generation
- `POST /nodegen/frontend-to-backend` - Generate backend from frontend
- `POST /agent/upload-erd` - Generate backend from ERD
- `POST /frontend/generate-react` - Generate frontend from single UI image
- `POST /frontend/generate-multi-screen` - Generate frontend from multiple UI images
- `GET /nodegen/download/:projectId` - Download generated project

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## License

Same as the main CodeCraft project.
