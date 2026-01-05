
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css' // Assuming global styles might be added later, or we can remove if it errors

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
