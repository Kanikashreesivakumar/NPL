import React, { useState } from 'react';

const ImageGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // API call simulation
      setTimeout(() => {
        setGeneratedImage('https://placeholder.com/400');
        setLoading(false);
      }, 2000);
    } catch (error) {
      console.error('Error generating image:', error);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Transform Your Ideas Into Images
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
              Describe your image
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="A serene landscape with mountains..."
            />
          </div>

          <button
            type="submit"
            disabled={loading || !prompt}
            className={`w-full py-3 px-6 rounded-lg text-white font-medium
              ${loading || !prompt 
                ? 'bg-indigo-400 cursor-not-allowed' 
                : 'bg-indigo-600 hover:bg-indigo-700 transition-colors'}
            `}
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Generating...
              </div>
            ) : (
              'Generate Image'
            )}
          </button>
        </form>

        {generatedImage && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Generated Image</h2>
            <div className="rounded-lg overflow-hidden shadow-lg">
              <img
                src={generatedImage}
                alt="Generated content"
                className="w-full h-auto"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageGenerator;