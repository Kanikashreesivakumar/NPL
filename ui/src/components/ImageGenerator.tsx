import React, { useState } from 'react';
import { generateImage } from '../services/api';

const ImageGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await generateImage(prompt);
      if (result.status === 'success' && result.image) {
        setGeneratedImage(`data:image/png;base64,${result.image}`);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      setError('Failed to generate image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-8 py-36"> 
      <div className="glass-card p-20 backdrop-blur-lg bg-white/10 rounded-2xl shadow-2xl"> 
        <h1 className="text-4xl font-bold text-center mb-16 text-black">
          Transform Your Ideas Into Images
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full p-4 bg-black/5 border border-black/10 rounded-lg text-black"
            placeholder="Describe your image..."
            rows={4}
          />
          
          <button
            type="submit"
            disabled={loading || !prompt}
            className={`w-full py-4 rounded-lg font-semibold ${
              loading || !prompt 
                ? 'bg-blue-500  cursor-not-allowed' 
                : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:opacity-90'
            }`}
          >
            {loading ? 'Generating...' : 'Generate Image'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
            {error}
          </div>
        )}

        {generatedImage && (
          <div className="mt-8">
            <img 
              src={generatedImage} 
              alt="Generated" 
              className="w-full rounded-lg shadow-xl"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageGenerator;