import { useState } from 'react';
import ImageGenerator from './components/imagegenerator';
import Navbar from './components/navbar';
import logo from './logo.svg';
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
