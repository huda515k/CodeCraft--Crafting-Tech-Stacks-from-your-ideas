# Frontend Generator Module

AI-powered frontend generation that converts UI designs (Figma, Canva, screenshots) into pixel-perfect React code.

## Features

- 🎨 **Vision AI Analysis**: Uses Gemini Flash for accurate UI design analysis
- 📦 **Component Extraction**: Automatically identifies and extracts UI components
- 💅 **Style Extraction**: Extracts colors, typography, spacing, and styling details
- ⚛️ **React Generation**: Generates complete React projects with proper structure
- 📘 **TypeScript Support**: Optional TypeScript support
- 🎯 **Multiple Styling Options**: CSS Modules or Tailwind CSS
- 🔧 **Production Ready**: Generates runnable code with proper project structure

## Architecture

The module follows a multi-step pipeline:

```
UI Image → Gemini Vision Analysis → Component Extraction → Code Generation → React Project
```

### Module Structure

- **`ui_parser.py`**: Analyzes UI images using Gemini vision API
- **`code_generator.py`**: Generates React components and project files
- **`services.py`**: Orchestrates the full pipeline
- **`routes.py`**: FastAPI endpoints for the service
- **`models.py`**: Pydantic models for data structures

## Usage

### Endpoint: `/frontend/generate-react`

Generate a complete React project from a UI image:

```bash
curl -X POST "http://localhost:8000/frontend/generate-react" \
  -F "file=@design.png" \
  -F "additional_context=Add dark mode support" \
  -F "include_typescript=true" \
  -F "styling_approach=css-modules"
```

### Endpoint: `/frontend/upload-ui`

Analyze UI image without generating code:

```bash
curl -X POST "http://localhost:8000/frontend/upload-ui" \
  -F "file=@design.png" \
  -F "additional_context=Focus on mobile responsiveness"
```

### Endpoint: `/frontend/analyze-ui-only`

Get detailed UI analysis JSON:

```bash
curl -X POST "http://localhost:8000/frontend/analyze-ui-only" \
  -F "file=@design.png"
```

## Configuration

Requires `GEMINI_API_KEY` environment variable:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

## Generated Project Structure

```
react-app/
├── package.json
├── tsconfig.json (if TypeScript)
├── src/
│   ├── App.tsx/jsx
│   ├── index.tsx/jsx
│   ├── index.css
│   └── components/
│       ├── Header.tsx/jsx
│       ├── Header.module.css
│       └── ...
└── README.md
```

## Components Generated

The generator identifies and creates:
- Layout components (Header, Footer, Sidebar, Navbar)
- Content components (Cards, Forms, Lists)
- Interactive elements (Buttons, Inputs, Modals)
- Custom components based on design

## Styling Approaches

### CSS Modules (Default)
- Scoped styles per component
- `.module.css` files
- Type-safe class names with TypeScript

### Tailwind CSS
- Utility-first styling
- Configured via `tailwind.config.js`
- Responsive design support

## Example Response

After processing a UI image, you'll get:
- Structured component hierarchy
- Color palette extraction
- Typography information
- Complete React project ZIP

## Requirements

- Python 3.8+
- FastAPI
- Google Generative AI (Gemini)
- PIL (Pillow) for image processing

## Future Enhancements

- [ ] Vue.js support
- [ ] Next.js support
- [ ] Component state management generation
- [ ] Animation extraction and generation
- [ ] Responsive breakpoint detection
- [ ] Accessibility features generation

