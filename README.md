# FashionNanoBanana 🍌👗

AI-powered fashion analysis and product image generation application.

## 🎯 Overview

FashionNanoBanana combines clothing analysis and product image generation using AI. Upload clothing items and model photos to get detailed fashion analysis and generate professional product listing images.

## 🏗️ Architecture

- **Backend**: FastAPI server with Google Gemini AI integration
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **State Management**: Zustand for clean, centralized state
- **UI Components**: Radix UI with custom styling

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Google Gemini API key

### 1. Setup Backend
```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Start backend:
```bash
python api.py
```
Backend runs at: http://localhost:8000

### 2. Setup Frontend
```bash
cd frontend/my-app
pnpm install
pnpm run dev
```
Frontend runs at: http://localhost:3000

## 📱 Features

### 🔍 AI Clothing Analysis
- Detailed clothing type, color, material analysis
- Style recommendations and seasonal suggestions
- Fashion trend insights

### 🖼️ Product Image Generation
- Generate professional product listing photos
- Multiple angles and poses
- Model wearing the clothing items

### 🎨 Modern UI
- Responsive design for all devices
- Real-time feedback and loading states
- Drag & drop file uploads
- Beautiful product cards for results

## 🎯 Usage

1. **Upload Your Photo**: Add a clear photo of yourself
2. **Upload Clothing**: Add clothing items to analyze
3. **Choose Action**:
   - **Analyze Clothing**: Get AI fashion insights
   - **Generate Product Images**: Create professional product photos
4. **View Results**: See analysis and generated images

## 📁 Project Structure

```
FashionNanoBanana/
├── backend/
│   ├── api.py              # FastAPI server
│   ├── banana.py           # Core AI functions
│   ├── requirements.txt    # Python dependencies
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

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /api/analyze` - Clothing analysis only
- `POST /api/generate` - Full workflow (analysis + images)
- `GET /static/{filename}` - Serve generated images

## 🎨 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Google Gemini AI**: Advanced image analysis
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### Frontend
- **Next.js 14**: React framework with TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: Lightweight state management
- **Radix UI**: Accessible component library
- **Lucide React**: Beautiful icons

## 🔒 Environment Variables

Create `backend/.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🧪 Development

### Backend Development
```bash
cd backend
python api.py  # Runs with auto-reload
```

### Frontend Development
```bash
cd frontend/my-app
pnpm run dev  # Runs with hot reload
```

## 📦 Production Deployment

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend/my-app
pnpm run build
pnpm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini AI for advanced image analysis
- Radix UI for accessible components
- Tailwind CSS for beautiful styling
- Next.js team for the amazing framework
