# AltMX 技術スタック

## Frontend
- **Framework**: React 18 + TypeScript 5.0
- **UI/Styling**: TailwindCSS + HeadlessUI
- **Testing**: Vitest + React Testing Library
- **E2E Testing**: Playwright
- **Build Tool**: Vite
- **Component Catalog**: Storybook
- **Deployment**: Vercel

## Backend
- **Framework**: FastAPI (Python 3.10+)
- **Testing**: pytest + httpx
- **API Documentation**: Auto-generated OpenAPI/Swagger
- **Deployment**: AWS (preferred over Azure)

## AI Integration
- **Primary LLM**: Claude API
- **Secondary LLM**: Gemini API (no GPT-4)
- **Voice Technology**: 
  - Text-to-Speech: Google Cloud Text-to-Speech API または Web Speech API
  - Speech-to-Text: Google Cloud Speech-to-Text API, OpenAI Whisper API, または Web Speech API

## Database & Storage
- **Database**: Supabase (PostgreSQL)
- **Real-time**: WebSocket (Socket.io)

## External APIs
- **Chat Integration**: SLACK API (優先), LINEWORKS API
- **Office Integration**: Microsoft Graph API

## Cloud Services
- **Preferred**: Google Cloud + AWS
- **Excluded**: Azure (per user preference)

## Development Environment
- **OS**: Windows
- **Package Manager**: npm (frontend), pip (backend)
- **Version Control**: Git/GitHub
- **Monorepo**: npm workspaces