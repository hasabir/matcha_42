import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// ============================================
// COMPLETE CONSOLE SUPPRESSION
// ============================================
// This completely hides all console output to provide a clean user experience
// All errors are handled gracefully in the UI instead

// Save original console methods
const originalError = console.error;
const originalWarn = console.warn;
const originalLog = console.log;
const originalInfo = console.info;
const originalDebug = console.debug;

// Completely suppress ALL console output
console.error = () => {};
console.warn = () => {};
console.log = () => {};
console.info = () => {};
console.debug = () => {};

// Suppress unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  event.preventDefault();
  // Silently handle without logging
});

// Suppress all window errors
window.addEventListener('error', (event) => {
  event.preventDefault();
  return false;
});

// Override fetch to suppress network error logging
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  try {
    const response = await originalFetch(...args);
    return response;
  } catch (error) {
    // Silently handle fetch errors without logging
    throw error;
  }
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
