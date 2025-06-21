
import React from 'react';

const Profile: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 pt-32">
      <div className="max-w-4xl mx-auto px-4">
        <div className="glass-card p-12 backdrop-blur-lg bg-white/10 rounded-2xl shadow-2xl">
          <div className="flex items-center space-x-8 mb-8">
            <div className="w-24 h-24 rounded-full bg-gradient-to-r from-blue-400 to-purple-600 flex items-center justify-center text-white text-3xl font-bold">
              U
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">User Profile</h1>
              <p className="text-gray-400">Member since 2024</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-white">Account Details</h2>
              <div className="space-y-4">
                <div className="glass-card p-4">
                  <p className="text-sm text-gray-400">Email</p>
                  <p className="text-white">user@example.com</p>
                </div>
                <div className="glass-card p-4">
                  <p className="text-sm text-gray-400">Images Generated</p>
                  <p className="text-white">42</p>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
              <div className="space-y-4">
                <div className="glass-card p-4">
                  <p className="text-white">Last generated image: 2 hours ago</p>
                </div>
                <div className="glass-card p-4">
                  <p className="text-white">Gallery visits: 15</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;