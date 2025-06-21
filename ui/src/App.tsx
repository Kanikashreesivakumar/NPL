import React from 'react';
import Navbar from './components/navbar';
import ImageGenerator from './components/ImageGenerator';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <ImageGenerator />
      </main>
    </div>
  );
}

export default App;
