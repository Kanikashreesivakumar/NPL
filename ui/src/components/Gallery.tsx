import React, { useState, useEffect } from 'react';

interface GeneratedImage {
  id: string;
  url: string;
  prompt: string;
  createdAt: Date;
}

const Gallery: React.FC = () => {
  const [images, setImages] = useState<GeneratedImage[]>([
    {
      id: '1',
      url: 'https://picsum.photos/800/600?random=1',
      prompt: 'A serene landscape with mountains',
      createdAt: new Date('2025-06-21')
    },
    {
      id: '2',
      url: 'https://picsum.photos/800/600?random=2',
      prompt: 'Abstract digital art in neon colors',
      createdAt: new Date('2025-06-20')
    },
    {
      id: '3',
      url: 'https://picsum.photos/800/600?random=3',
      prompt: 'Futuristic cityscape at night',
      createdAt: new Date('2025-06-19')
    }
  ]);
  const [filter, setFilter] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'prompt'>('date');

  const filteredAndSortedImages = images
    .filter(img => img.prompt.toLowerCase().includes(filter.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === 'date') {
        return b.createdAt.getTime() - a.createdAt.getTime();
      }
      return a.prompt.localeCompare(b.prompt);
    });

  const deleteImage = (id: string) => {
    setImages(images.filter(img => img.id !== id));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 py-20 px-4">
      <div className="container mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-white">Image History</h1>
          <div className="flex gap-4">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'prompt')}
              className="px-4 py-2 rounded-lg bg-white/10 border border-white/20 
                text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="date">Sort by Date</option>
              <option value="prompt">Sort by Prompt</option>
            </select>
            <input
              type="text"
              placeholder="Search by prompt..."
              className="w-64 px-4 py-2 rounded-lg bg-white/10 border border-white/20 
                text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAndSortedImages.map((image) => (
            <div key={image.id} className="glass-card group">
              <div className="relative overflow-hidden rounded-lg">
                <img
                  src={image.url}
                  alt={image.prompt}
                  className="w-full h-64 object-cover transform transition-transform duration-300 
                    group-hover:scale-110"
                />
                <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t 
                  from-black/90 to-transparent opacity-0 group-hover:opacity-100 
                  transition-opacity duration-300">
                  <p className="text-white text-sm font-medium mb-2">{image.prompt}</p>
                  <div className="flex justify-between items-center">
                    <p className="text-gray-300 text-xs">
                      {new Date(image.createdAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                    <button
                      onClick={() => deleteImage(image.id)}
                      className="text-red-400 hover:text-red-300 transition-colors duration-300"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredAndSortedImages.length === 0 && (
          <div className="text-center text-gray-400 py-16 glass-card">
            <p className="text-xl mb-2">No images found</p>
            <p>Generate some images to see them here!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Gallery;