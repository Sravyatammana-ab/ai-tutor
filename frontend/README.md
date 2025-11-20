# AI Tutor Frontend

React + Vite frontend for the AI Tutor application.

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

## Configuration

The frontend is configured to proxy API requests to `http://localhost:5000` (backend server).

To change the backend URL, update `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  }
}
```

## Features

- File upload (PDF/DOCX)
- Chat interface
- Language selection
- Audio playback
- Suggested questions
- Conversation history

## Development

The frontend uses:
- React 18
- Vite 5
- Axios for HTTP requests
- CSS for styling

## Build

To build for production:

```bash
npm run build
```

The built files will be in the `dist/` directory.


