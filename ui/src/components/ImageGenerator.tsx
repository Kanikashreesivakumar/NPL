import React, { useState } from 'react';
import { generateImage, checkHealth } from '../services/api';

export interface GenerateImageResponse {
    status: string;
    image?: string;
    image_id?: string;
}

const ImageGenerator: React.FC = () => {
    const [prompt, setPrompt] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim()) return;

        setLoading(true);
        setError(null);
        setSuccessMessage(null);

        try {
            console.log('🚀 Starting fast image generation...');
            
            const result = await generateImage(prompt);
            if (result.status === 'success' && result.image) {
                setGeneratedImage(`data:image/png;base64,${result.image}`);
                setSuccessMessage(`✅ Image generated and saved to gallery! ()`);
                console.log('✅ Image generated and saved to database!');
                
                // Clear the prompt for next generation
                setPrompt('');
            } else {
                throw new Error('Invalid response from server');
            }
        } catch (err) {
            setError('Failed to generate image. Please try again.');
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto px-8 py-36">
            <div className="glass-card p-20 backdrop-blur-lg bg-white/10 rounded-2xl shadow-2xl">
                <h1 className="text-4xl font-bold text-center bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent mb-16 heading-text">
                    Transform Your Ideas Into Images
                </h1>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        className="w-full p-4 bg-white/5 border border-black text-black rounded-lg input-text"
                        placeholder="Describe your image..."
                        rows={4}
                    />
                    
                    <button
                        type="submit"
                        disabled={loading || !prompt}
                        className={`w-full py-4 rounded-lg font-semibold ${
                            loading || !prompt 
                                ? 'bg-gray-500 cursor-not-allowed' 
                                : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:opacity-90'
                        } text-white transition-all duration-300`}
                    >
                        {loading ? 'Generating...' : 'Generate & Save to Gallery'}
                    </button>
                </form>

                {error && (
                    <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
                        {error}
                    </div>
                )}

                {successMessage && (
                    <div className="mt-4 p-4 bg-green-500/10 border border-green-500/20 rounded-lg text-green-400">
                        {successMessage}
                    </div>
                )}

                {generatedImage && (
                    <div className="mt-8">
                        <h3 className="text-xl font-semibold text-white mb-4">Generated Image:</h3>
                        <img 
                            src={generatedImage} 
                            alt="Generated" 
                            className="w-full rounded-lg shadow-xl"
                        />
                        <p className="text-center text-gray-300 mt-4">
                            🎉 Image saved to gallery! Check the Gallery page to see all your creations.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ImageGenerator;