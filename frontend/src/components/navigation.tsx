import React from 'react'

const Navigation = () => {
  return (
    <div className='py-6 sticky top-0 z-50 bg-gray-950 text-white border-b border-gray-800'>
      <div className='container mx-auto px-4 flex items-center justify-between'>
        <div>
          <div className='text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent'>Nuvio</div>
        <div className='text-sm text-gray-300'>Your AI-Powered Website Cloning Tool</div>
        </div>
        <button className='px-4 py-2  bg-gradient-to-r from-cyan-400 to-blue-500 text-white rounded-full hover:opacity-90 transition-colors'>
          Get Started Now
        </button>
      </div>
    </div>
  )
}

export default Navigation
