# IntegMed Frontend

Next.js 14 application for the IntegMed healthcare platform.

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

## Features

✅ HPR-based authentication
✅ Prescription management with shorthand
✅ Drug interaction checking
✅ Patient dashboard
✅ Responsive design
✅ TypeScript
✅ Tailwind CSS

## Environment Setup

Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```

## Build for Production

```bash
npm run build
npm start
```

## Docker

```bash
docker build -t integmed/frontend .
docker run -p 3000:3000 integmed/frontend
```
