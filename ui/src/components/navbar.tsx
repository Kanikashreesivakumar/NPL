import React from 'react';

const Navbar: React.FC = () => (
  <nav className="bg-white shadow p-4 mb-8">
    <div className="container mx-auto flex items-center justify-between">
      <span className="text-xl font-bold">Text to Image Generator</span>
      <div className="flex space-x-4">
        <button onClick={() => window.location.href = '/gallery'} className="px-4 py-2 text-gray-700 hover:text-indigo-600">
          Gallery
        </button>
        <button onClick={() => window.location.href = '/about'} className="px-4 py-2 text-gray-700 hover:text-indigo-600">
          About
        </button>
      </div>
    </div>
  </nav>
);

export default Navbar;
