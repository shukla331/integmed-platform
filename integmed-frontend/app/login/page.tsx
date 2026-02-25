'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import api from '@/lib/api';
import Cookies from 'js-cookie';

export default function LoginPage() {
  const router = useRouter();
  const setUser = useAuthStore((state) => state.setUser);
  
  const [step, setStep] = useState<'mobile' | 'otp'>('mobile');
  const [mobile, setMobile] = useState('');
  const [otp, setOtp] = useState('');
  const [txnId, setTxnId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.initDoctorAuth(mobile);
      setTxnId(response.txn_id);
      setStep('otp');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const { user } = await api.verifyDoctorAuth(txnId, otp);
      
      // Store user in cookie for persistence
      Cookies.set('user', JSON.stringify(user), { expires: 7 });
      
      // Update auth store
      setUser(user);
      
      // Redirect based on role
      if (user.role === 'admin') {
        router.push('/admin');
      } else {
        router.push('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-700 to-primary-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-display font-bold text-primary-900">
            Integ<span className="text-primary-500">Med</span>
          </h1>
          <p className="text-gray-500 mt-2">Integrated Healthcare Platform</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Mobile Step */}
        {step === 'mobile' && (
          <form onSubmit={handleSendOTP} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                HPR-Linked Mobile Number
              </label>
              <input
                type="tel"
                value={mobile}
                onChange={(e) => setMobile(e.target.value)}
                placeholder="+91 98765 43210"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                required
                pattern="^\+91[0-9]{10}$"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter your HPR-registered mobile number
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-500 text-white py-3 rounded-lg font-medium hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Sending OTP...
                </span>
              ) : (
                'Send OTP'
              )}
            </button>
          </form>
        )}

        {/* OTP Step */}
        {step === 'otp' && (
          <form onSubmit={handleVerifyOTP} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enter OTP
              </label>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="123456"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-center text-2xl tracking-widest font-mono"
                required
                maxLength={6}
                autoComplete="one-time-code"
              />
              <p className="text-xs text-gray-500 mt-1">
                OTP sent to {mobile}
              </p>
            </div>

            <button
              type="submit"
              disabled={loading || otp.length !== 6}
              className="w-full bg-primary-500 text-white py-3 rounded-lg font-medium hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Verifying...
                </span>
              ) : (
                'Verify & Login'
              )}
            </button>

            <button
              type="button"
              onClick={() => {
                setStep('mobile');
                setOtp('');
                setError('');
              }}
              className="w-full text-primary-500 text-sm hover:text-primary-700"
            >
              ← Change mobile number
            </button>
          </form>
        )}

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-gray-100 text-center text-xs text-gray-400">
          <p>🏥 IntegMed • Demo Environment</p>
          <p className="mt-1">Real HPR integration pending government approval</p>
        </div>

        {/* ====== TEMPORARY: SKIP LOGIN BUTTON ====== */}
        {/* DELETE THIS ENTIRE SECTION WHEN REAL AUTH IS READY */}
        <button
          onClick={() => {
            // Auto-login as demo doctor
            const demoUser = {
              id: "demo-doctor-001",
              name: "Dr. Priya Sharma",
              mobile: "+919876543210",
              email: "priya.sharma@integmed.health",
              system: "allopathy" as const,
              qualification: "MBBS, MD (Internal Medicine)",
              specialization: "Internal Medicine",
              role: "doctor" as const,
            };
            
            // Store fake token
            Cookies.set('access_token', 'demo-token-12345', { expires: 7 });
            Cookies.set('user', JSON.stringify(demoUser), { expires: 7 });
            
            // Update state
            setUser(demoUser);
            
            // Go to dashboard
            router.push('/dashboard');
          }}
          className="mt-6 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 animate-pulse"
        >
          🚀 SKIP LOGIN - GO TO DASHBOARD
        </button>
        <p className="text-center text-xs text-gray-400 mt-2">
          (For demo/testing only - bypasses authentication)
        </p>
        {/* ====== END TEMPORARY SECTION ====== */}
      </div>
    </div>
  );
}
/* Force rebuild 02/23/2026 14:54:16 */


