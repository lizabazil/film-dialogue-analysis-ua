import React from 'react'
import ReactDOM from 'react-dom/client'
import { MantineProvider, createTheme } from '@mantine/core';
import App from './App.jsx'

// Імпортуємо обов'язкові стилі Mantine
import '@mantine/core/styles.css';
import '@mantine/dropzone/styles.css';

// Створюємо тему, схожу на твої скріншоти
const theme = createTheme({
  fontFamily: 'Inter, sans-serif',
  primaryColor: 'violet', // Фіолетовий акцент як на скріншоті
  defaultRadius: 'md',    // Заокруглені кути
  shadows: {
    md: '0 4px 20px rgba(0, 0, 0, 0.05)', // М'яка тінь
  },
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <MantineProvider theme={theme}>
      <App />
    </MantineProvider>
  </React.StrictMode>,
)