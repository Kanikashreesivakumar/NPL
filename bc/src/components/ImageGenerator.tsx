import React, { useState } from 'react';
import { generateImage } from '../services/api';

const ImageGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await generateImage({ prompt });
      setGeneratedImage(`data:image/png;base64,${result.image}`);
    } catch (err) {
      setError('Failed to generate image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter prompt"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Image'}
        </button>
      </form>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {generatedImage && (
        <div>
          <img src={generatedImage} alt="Generated" />
        </div>
      )}
    </div>
  );
};

export default ImageGenerator;