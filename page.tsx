'use client'

export default function Home() {
  const handleEnterDashboard = () => {
    const demoUser = {
      id: "demo-doctor-001",
      name: "Dr. Priya Sharma",
      mobile: "+919876543210",
      email: "priya.sharma@integmed.health",
      system: "allopathy",
      qualification: "MBBS, MD (Internal Medicine)",
      specialization: "Internal Medicine",
      role: "doctor",
    };
    
    // Store in cookies and redirect. This is the most robust method for a demo
    // as it doesn't depend on client-side state hydration.
    document.cookie = `access_token=demo-token-12345; max-age=${7*24*60*60}; path=/`;
    document.cookie = `user=${JSON.stringify(demoUser)}; max-age=${7*24*60*60}; path=/`;
    window.location.href = '/dashboard';
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">Welcome to the App</h1>
      
      <button
        onClick={handleEnterDashboard}
        className="mt-4 px-8 py-4 bg-blue-600 text-white font-bold text-xl rounded-lg hover:bg-blue-700 transition-colors shadow-lg"
      >
        🏥 Enter Dashboard
      </button>

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-400">
          Click above to enter the dashboard as a demo user.
        </p>
      </div>
    </main>
  )
}