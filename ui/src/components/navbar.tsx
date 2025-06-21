import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => (
  <nav className="bg-gradient-to-r from-gray-900 to-gray-800 shadow-lg p-4 fixed w-full z-50">
    <div className="container mx-auto flex items-center justify-between">
      <div className="flex items-center space-x-2">
        <Link to="/" className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 hover:scale-105 transition-transform duration-300 font-['Space_Grotesk']">
          NLP
        </Link>
        <span className="text-sm text-gray-400 ml-4">Text to Image Generator</span>
      </div>
      <div className="flex space-x-4 items-center">
        <Link 
          to="/gallery" 
          className="px-4 py-2 text-gray-300 hover:text-white transition-colors duration-300"
        >
          Gallery
        </Link>
        <Link 
          to="/about" 
          className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg text-white hover:opacity-90 transition-opacity duration-300"
        >
          About
        </Link>
        <Link 
          to="/profile" 
          className="px-4 py-2 bg-white/10 rounded-lg text-white hover:bg-white/20 transition-all duration-300 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Profile
        </Link>
      </div>
    </div>
  </nav>
);

export default Navbar;
