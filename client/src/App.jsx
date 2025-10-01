import React from 'react'
import Home from './components/Home'

const App = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black">
    
      <Home/>

      <div className="mt-12 pb-8">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center border-t border-gray-700/50 pt-8">
            <p className="text-gray-400 text-sm">
              Built with passion🔥by-Shrish Gupta
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App