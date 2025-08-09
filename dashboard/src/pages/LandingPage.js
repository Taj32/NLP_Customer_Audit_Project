import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaChartLine, FaComments, FaBrain } from 'react-icons/fa';

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Hero Section */}
      <header className="bg-white shadow flex items-center justify-center">
        <div className="py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">Conversight</h1>
        </div>
      </header>

      <main className="flex-grow">
        {/* Hero content */}
        <section
          className="relative text-white py-20"
          style={{
            backgroundColor: '#1E3A8A', // Blue background
          }}
        >
          {/* Background Image */}
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: `url('/mic.png')`,
              backgroundSize: 'contain',
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'center',
              opacity: 0.8, // Slight transparency for the image
            }}
          ></div>

          {/* Content */}
          <div className="relative max-w-5xl mx-auto text-center px-6">
            <h2 className="text-5xl font-extrabold mb-6">Understand Your Customers Like Never Before</h2>
            <p className="text-lg text-blue-100 max-w-3xl mx-auto mb-8">
              Conversight uses Generative AI and NLP to capture, analyze, and audit real-world customer interactions.
              Get actionable insights to boost satisfaction, improve retention, and grow your business.
            </p>
            <div className="space-x-4">
              <button
                onClick={() => navigate('/login')}
                className="bg-white text-blue-700 font-semibold py-3 px-8 rounded-lg shadow hover:bg-gray-100"
              >
                Log In
              </button>
              <button
                onClick={() => window.open('mailto:contact@conversight.ai')}
                className="bg-transparent border border-white text-white font-semibold py-3 px-8 rounded-lg hover:bg-white hover:text-blue-700"
              >
                Contact Us
              </button>
            </div>
          </div>
        </section>

        {/* Additional Sections */}
        <section className="py-16 bg-gray-50">
          <div className="max-w-6xl mx-auto px-6">
            <h3 className="text-3xl font-bold text-center text-gray-800 mb-12">Why Conversight?</h3>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
                <FaComments className="text-blue-600 text-4xl mb-4" />
                <h4 className="text-xl font-semibold mb-2">Conversation Capture</h4>
                <p className="text-gray-600">
                  Seamlessly record and process customer interactions, whether in-person, over the phone, or online.
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
                <FaBrain className="text-blue-600 text-4xl mb-4" />
                <h4 className="text-xl font-semibold mb-2">AI-Powered Insights</h4>
                <p className="text-gray-600">
                  Use advanced NLP to detect sentiment, intent, and satisfaction levels in real-time.
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
                <FaChartLine className="text-blue-600 text-4xl mb-4" />
                <h4 className="text-xl font-semibold mb-2">Actionable Analytics</h4>
                <p className="text-gray-600">
                  Visualize trends, pinpoint improvement areas, and measure the impact of changes to your service.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-6 text-center">
        <p>© {new Date().getFullYear()} Conversight. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default LandingPage;
