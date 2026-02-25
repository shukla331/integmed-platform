'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import Cookies from 'js-cookie';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, setUser } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleDashboardClick = () => {
    const demoUser = {
      id: 'demo-doctor-001',
      name: 'Dr. Priya Sharma',
      mobile: '+919876543210',
      email: 'priya.sharma@integmed.health',
      system: 'allopathy' as const,
      qualification: 'MBBS, MD (Internal Medicine)',
      specialization: 'Internal Medicine',
      role: 'doctor' as const,
    };

    Cookies.set('access_token', 'demo-token-12345', { expires: 1 });
    Cookies.set('user', JSON.stringify(demoUser), { expires: 1 });
    setUser(demoUser);
    router.push('/dashboard');
  };

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

        <div className="flex justify-center mb-12">
          <button
            onClick={handleDashboardClick}
            className="bg-white text-primary-800 px-10 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition shadow-lg"
          >
            Dashboard
          </button>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mt-16">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-white">
            <div className="text-4xl mb-4">ABDM</div>
            <h3 className="text-xl font-bold mb-3">ABDM Integrated</h3>
            <p className="text-gray-200">
              Seamless integration with Ayushman Bharat Digital Mission
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-white">
            <div className="text-4xl mb-4">RX</div>
            <h3 className="text-xl font-bold mb-3">Smart Prescriptions</h3>
            <p className="text-gray-200">
              AI-powered shorthand expansion and interaction checking
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-white">
            <div className="text-4xl mb-4">TL</div>
            <h3 className="text-xl font-bold mb-3">Unified Timeline</h3>
            <p className="text-gray-200">
              Complete health history across all medical systems
            </p>
          </div>
        </div>

        <div className="mt-12 rounded-xl bg-white/10 p-6 text-left text-white backdrop-blur-lg">
          <h3 className="text-xl font-bold mb-4">Explore All Pages</h3>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <Link href="/dashboard" className="rounded-lg bg-white/20 px-4 py-3 hover:bg-white/30 transition">
              Doctor Dashboard
            </Link>
            <Link href="/dashboard/mockup" className="rounded-lg bg-white/20 px-4 py-3 hover:bg-white/30 transition">
              Doctor UI Mockup
            </Link>
            <Link href="/dashboard/patients/new" className="rounded-lg bg-white/20 px-4 py-3 hover:bg-white/30 transition">
              Register Patient
            </Link>
            <Link href="/dashboard/prescriptions/new" className="rounded-lg bg-white/20 px-4 py-3 hover:bg-white/30 transition">
              Prescription Editor
            </Link>
            <Link href="/dashboard/scribe" className="rounded-lg bg-white/20 px-4 py-3 hover:bg-white/30 transition">
              AI Scribe
            </Link>
            <Link href="/admin" className="rounded-lg bg-white/20 px-4 py-3 hover:bg-white/30 transition">
              Clinic Admin Panel
            </Link>
            <Link href="/patient-portal" className="rounded-lg bg-white/20 px-4 py-3 hover:bg-white/30 transition">
              Patient Portal
            </Link>
            <Link href="/login" className="rounded-lg bg-white/20 px-4 py-3 hover:bg-white/30 transition">
              Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
