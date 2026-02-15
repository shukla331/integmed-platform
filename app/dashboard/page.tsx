'use client';

import { useAuthStore } from '@/lib/store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, logout } = useAuthStore();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-display font-bold text-primary-900">
            Integ<span className="text-primary-500">Med</span>
          </h1>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="font-medium">{user.name}</div>
              <div className="text-sm text-gray-500">{user.qualification}</div>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-primary-700 to-primary-900 rounded-2xl p-8 text-white mb-8">
          <h2 className="text-3xl font-display font-bold mb-2">
            Welcome back, Dr. {user.name.split(' ')[user.name.split(' ').length - 1]}!
          </h2>
          <p className="text-gray-200">
            {user.system.charAt(0).toUpperCase() + user.system.slice(1)} • {user.specialization || 'General Practice'}
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="text-3xl mb-2">👥</div>
            <div className="text-2xl font-bold text-gray-900">124</div>
            <div className="text-sm text-gray-500">Total Patients</div>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="text-3xl mb-2">📋</div>
            <div className="text-2xl font-bold text-gray-900">8</div>
            <div className="text-sm text-gray-500">Today's Appointments</div>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="text-3xl mb-2">💊</div>
            <div className="text-2xl font-bold text-gray-900">15</div>
            <div className="text-sm text-gray-500">Prescriptions (This Week)</div>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="text-3xl mb-2">🔔</div>
            <div className="text-2xl font-bold text-gray-900">3</div>
            <div className="text-sm text-gray-500">Pending Consents</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <Link
              href="/dashboard/patients/new"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition"
            >
              <div className="text-2xl mb-2">➕</div>
              <div className="font-medium">Register Patient</div>
              <div className="text-sm text-gray-500">Add new patient record</div>
            </Link>
            
            <Link
              href="/dashboard/prescriptions/new"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition"
            >
              <div className="text-2xl mb-2">📝</div>
              <div className="font-medium">New Prescription</div>
              <div className="text-sm text-gray-500">Write prescription with shorthand</div>
            </Link>
            
            <Link
              href="/dashboard/scribe"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition"
            >
              <div className="text-2xl mb-2">🎙️</div>
              <div className="font-medium">AI Scribe</div>
              <div className="text-sm text-gray-500">Start ambient documentation</div>
            </Link>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-4 p-3 hover:bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-primary-700">RK</span>
              </div>
              <div className="flex-1">
                <div className="font-medium">Rajesh Kumar</div>
                <div className="text-sm text-gray-500">Consultation completed • 2 hours ago</div>
              </div>
              <button className="text-primary-500 text-sm">View</button>
            </div>
            
            <div className="flex items-center gap-4 p-3 hover:bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-primary-700">PM</span>
              </div>
              <div className="flex-1">
                <div className="font-medium">Priya Mehta</div>
                <div className="text-sm text-gray-500">Prescription signed • 5 hours ago</div>
              </div>
              <button className="text-primary-500 text-sm">View</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
