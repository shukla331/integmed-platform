'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function HomePage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-700 to-primary-900">
      <nav className="p-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-3xl font-display font-bold text-white">
            Integ<span className="text-primary-300">Med</span>
          </h1>
          <Link
            href="/login"
            className="bg-white text-primary-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-100 transition"
          >
            Login
          </Link>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-20 text-center">
        <h2 className="text-5xl font-display font-bold text-white mb-6">
          Integrated Healthcare Platform
        </h2>
        <p className="text-xl text-gray-200 mb-12">
          Bridging Allopathy and AYUSH for comprehensive patient care
        </p>

        <div className="grid md:grid-cols-3 gap-8 mt-16">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-white">
            <div className="text-4xl mb-4">🔗</div>
            <h3 className="text-xl font-bold mb-3">ABDM Integrated</h3>
            <p className="text-gray-200">
              Seamless integration with Ayushman Bharat Digital Mission
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-white">
            <div className="text-4xl mb-4">💊</div>
            <h3 className="text-xl font-bold mb-3">Smart Prescriptions</h3>
            <p className="text-gray-200">
              AI-powered shorthand expansion and interaction checking
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-white">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-3">Unified Timeline</h3>
            <p className="text-gray-200">
              Complete health history across all medical systems
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
