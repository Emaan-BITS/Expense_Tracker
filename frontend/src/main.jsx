import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import App from './App.jsx'
import './styles.css'

// StrictMode runs effects twice in development, so a useEffect that fetches
// will show two requests in the network tab. That's expected, not a bug.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
