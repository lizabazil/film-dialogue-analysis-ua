import React from 'react'
import ReactDOM from 'react-dom/client'
import { MantineProvider, createTheme } from '@mantine/core';
import App from './App.jsx'

import '@mantine/core/styles.css';
import '@mantine/dropzone/styles.css';

const theme = createTheme({
  fontFamily: 'Inter, sans-serif',
  primaryColor: 'violet',
  defaultRadius: 'md',
  shadows: {
    md: '0 4px 20px rgba(0, 0, 0, 0.05)',
  },
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <MantineProvider theme={theme}>
      <App />
    </MantineProvider>
  </React.StrictMode>,
)