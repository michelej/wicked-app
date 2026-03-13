# Wicked App - Frontend

Vue.js 3 frontend application with Pinia, PrimeVue, and Vite.

## Prerequisites

- Node.js 18+ and npm

## Local Development

### Install Dependencies

```bash
npm install
```

### Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Update `VITE_API_URL` if needed (default is `http://localhost:8000`).

### Run Locally

```bash
npm run dev
```

The application will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Docker

### Build Image

```bash
docker build -t wicked-frontend .
```

### Run Container

```bash
docker run -p 5173:5173 wicked-frontend
```

## Project Structure

```
src/
├── main.js           # Application entry point
├── App.vue           # Root component
├── router/           # Vue Router configuration
├── stores/           # Pinia stores
├── services/         # API services
└── views/            # Page components
```

## Technologies

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Next generation frontend tooling
- **Pinia** - State management
- **PrimeVue** - UI component library
- **Vue Router** - Official router for Vue.js
- **Axios** - HTTP client
