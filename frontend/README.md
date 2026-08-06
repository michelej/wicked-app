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

Update `VITE_API_URL` only if the browser should call a specific public API
URL. If it is empty, the frontend automatically calls the same hostname on
port `8000`.

### Run Locally

```bash
pnpm dev
```

The application will be available at http://localhost:5173

### Build for Production

```bash
pnpm build
```

### Preview Production Build

```bash
pnpm preview
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
