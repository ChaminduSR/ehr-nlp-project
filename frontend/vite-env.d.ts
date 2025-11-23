/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  // add more env variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Focused module declarations for packages that may not ship types or
// are missing in this environment. Add more as needed.
declare module '@radix-ui/react-hover-card';

export {};
