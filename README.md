# FashionNanoBanana 🍌👗

AI-powered fashion analysis and product image generation using Google Gemini AI. Upload clothing items and model photos to get detailed fashion analysis and generate professional product listing images.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ with [uv](https://astral.sh/uv/) package manager
- Node.js 18+ with pnpm
- Google Gemini API key

### Setup
1. **Backend**:
```bash
cd backend
uv venv
uv pip install -r requirements.txt
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
uv run python api.py  # Runs at http://localhost:8000
```

2. **Frontend**:
```bash
cd frontend/my-app
pnpm install
pnpm run dev  # Runs at http://localhost:3000
```

## ✨ Features

- **AI Clothing Analysis**: Detailed type, color, material, style, and seasonal analysis
- **Product Image Generation**: Professional listing photos with multiple angles
- **Modern UI**: Responsive design with drag & drop uploads and real-time feedback

## 🎯 Usage

1. Upload a clear photo of yourself and clothing items
2. Choose: **Analyze Clothing** (insights only) or **Generate Product Images** (full workflow)
3. View AI analysis results and generated professional photos

## 📁 Project Structure

```
FashionNanoBanana/
├── backend/
│   ├── api.py              # FastAPI server
│   ├── banana.py           # Core AI functions
│   ├── requirements.txt    # Python dependencies
│   ├── run.sh             # Convenience script to start backend
│   ├── .venv/             # Virtual environment (created by uv)
│   ├── apparels/          # Sample clothing images
│   ├── model/             # Sample model images
│   └── static/            # Generated images
├── frontend/my-app/
│   ├── app/               # Next.js pages
│   ├── components/        # React components
│   ├── lib/               # Utilities and state
│   ├── package.json       # Node dependencies
│   └── pnpm-lock.yaml     # pnpm lockfile
└── README.md             # This file
```

## 🎨 Tech Stack

**Backend**: FastAPI + Google Gemini AI + Pydantic + Uvicorn
**Frontend**: Next.js 14 + TypeScript + Tailwind CSS + Zustand + Radix UI

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /api/analyze` - Clothing analysis only
- `POST /api/generate` - Full workflow (analysis + images)
- `GET /static/{filename}` - Serve generated images

## 📄 License

MIT License
