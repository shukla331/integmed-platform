'use client';

import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import Cookies from 'js-cookie';

export default function HomePage() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);

  const handleDashboardClick = () => {
    const demoUser = {
      id: 'demo-doctor-001',
      name: 'Dr. Priya Sharma',
      mobile: '+919876543210',
      email: 'priya.sharma@integmed.health',
      system: 'allopathy',
      qualification: 'MBBS, MD (Internal Medicine)',
      specialization: 'Internal Medicine',
      role: 'doctor',
    };

    // Keep middleware and client store in sync for demo access.
    Cookies.set('access_token', 'demo-access-token', { expires: 1 });
    login(demoUser);
    router.push('/dashboard');
  };

  const handleLogin = () => {
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 via-blue-900 to-blue-800">
      <header className="absolute top-0 left-0 right-0 z-50">
        <nav className="max-w-7xl mx-auto px-6 py-6 flex justify-between items-center">
          <div className="text-3xl font-bold text-white">
            Integ<span className="text-blue-300">Med</span>
          </div>
          <button
            onClick={handleLogin}
            className="px-6 py-2 bg-white text-blue-900 rounded-lg font-medium hover:bg-blue-50 transition"
          >
            Login
          </button>
        </nav>
      </header>

      <main className="relative pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Integrated Healthcare Platform
            </h1>
            <p className="text-xl text-blue-200 max-w-3xl mx-auto">
              Bridging Allopathy and AYUSH for comprehensive patient care
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition">
              <div className="text-5xl mb-4">AB</div>
              <h3 className="text-2xl font-bold text-white mb-3">ABDM Integrated</h3>
              <p className="text-blue-200">
                Seamless integration with Ayushman Bharat Digital Mission
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition">
              <div className="text-5xl mb-4">RX</div>
              <h3 className="text-2xl font-bold text-white mb-3">Smart Prescriptions</h3>
              <p className="text-blue-200">
                AI-powered shorthand expansion and interaction checking
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition">
              <div className="text-5xl mb-4">TL</div>
              <h3 className="text-2xl font-bold text-white mb-3">Unified Timeline</h3>
              <p className="text-blue-200">
                Complete health history across all medical systems
              </p>
            </div>
          </div>

          <div className="mt-20 flex justify-center">
            <button
              onClick={handleDashboardClick}
              className="group relative px-12 py-6 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-2xl font-bold text-2xl shadow-2xl hover:shadow-blue-500/50 hover:from-blue-700 hover:to-blue-900 transition-all duration-300 transform hover:scale-105"
            >
              <span className="relative z-10 flex items-center gap-4">
                <span className="text-4xl group-hover:animate-bounce">DM</span>
                <span>Dashboard</span>
                <span className="text-3xl">{'->'}</span>
              </span>

              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-400 to-blue-600 opacity-0 group-hover:opacity-30 blur-2xl transition-opacity duration-300"></div>
            </button>
          </div>

          <div className="mt-8 text-center">
            <p className="text-sm text-blue-300 bg-blue-900/30 inline-block px-6 py-3 rounded-full border border-blue-400/30">
              Demo Mode | Automatically logged in as Dr. Priya Sharma
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
