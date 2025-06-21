import React from 'react';

const About: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 pt-32">
      <div className="max-w-4xl mx-auto px-4">
        <div className="glass-card p-12 backdrop-blur-lg bg-white/10 rounded-2xl shadow-2xl">
          <h1 className="text-4xl font-bold text-white mb-8">About NLP</h1>
          
          <div className="space-y-6 text-gray-300">
            <div className="border-l-4 border-purple-500 pl-4">
              <h2 className="text-2xl font-semibold text-white mb-4">What is NLP?</h2>
              <p className="mb-4">
                NLP (Natural Language Processing) Image Generator is an AI-powered platform 
                that transforms textual descriptions into visual artwork using advanced 
                machine learning models.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              <div className="glass-card p-6">
                <h3 className="text-xl font-semibold text-white mb-4">Features</h3>
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <span className="mr-2">🎨</span>
                    High-quality image generation
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2">💡</span>
                    Intuitive text prompts
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2">🖼️</span>
                    Image history & gallery
                  </li>
                </ul>
              </div>

              <div className="glass-card p-6">
                <h3 className="text-xl font-semibold text-white mb-4">How to Use</h3>
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <span className="mr-2">1.</span>
                    Enter your description
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2">2.</span>
                    Click generate
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2">3.</span>
                    Save or share your creation
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;