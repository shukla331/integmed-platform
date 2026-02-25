import Link from 'next/link';

export default function AdminPage() {
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="grid lg:grid-cols-[260px_1fr]">
        <aside className="bg-slate-900 px-6 py-8 text-white">
          <h1 className="text-2xl font-semibold">Integ<span className="text-sky-300">Med</span></h1>
          <nav className="mt-8 space-y-2 text-sm">
            {['Dashboard', 'Analytics', 'Doctors and Staff', 'Patients', 'Appointments', 'ABDM Monitor', 'Compliance'].map((item, index) => (
              <div
                key={item}
                className={`rounded-lg px-3 py-2 ${index === 0 ? 'bg-sky-500/20 text-white' : 'text-slate-300 hover:bg-white/10'}`}
              >
                {item}
              </div>
            ))}
          </nav>
        </aside>

        <main className="p-6">
          <header className="rounded-xl bg-white p-6 shadow-sm">
            <h2 className="text-3xl font-semibold text-slate-900">Clinic Dashboard</h2>
            <p className="mt-1 text-sm text-slate-500">Apollo Hospital Mumbai | Admin View</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Link href="/" className="rounded-lg border border-slate-200 px-3 py-2 text-sm hover:bg-slate-50">Home</Link>
              <Link href="/dashboard" className="rounded-lg border border-slate-200 px-3 py-2 text-sm hover:bg-slate-50">Doctor Dashboard</Link>
              <Link href="/dashboard/mockup" className="rounded-lg border border-slate-200 px-3 py-2 text-sm hover:bg-slate-50">Doctor Mockup</Link>
              <Link href="/patient-portal" className="rounded-lg border border-slate-200 px-3 py-2 text-sm hover:bg-slate-50">Patient Portal</Link>
              <Link href="/login" className="rounded-lg border border-slate-200 px-3 py-2 text-sm hover:bg-slate-50">Login</Link>
            </div>
          </header>

          <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[
              ['Total Patients', '1,247', '+12%'],
              ['Consultations', '342', '+8%'],
              ['Prescriptions', '298', '+15%'],
              ['Revenue', 'INR 4.2L', '-3%'],
            ].map(([label, value, trend]) => (
              <article key={label} className="rounded-xl bg-white p-5 shadow-sm">
                <p className="text-sm text-slate-500">{label}</p>
                <p className="mt-2 text-3xl font-semibold">{value}</p>
                <p className="mt-2 text-xs text-slate-500">{trend} vs last week</p>
              </article>
            ))}
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-2">
            <article className="rounded-xl bg-white p-6 shadow-sm">
              <h3 className="text-xl font-semibold">ABDM Integration Status</h3>
              <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                {[
                  ['Consent Requests', '156'],
                  ['Approved', '142 (91%)'],
                  ['Data Fetches', '128'],
                  ['Avg Response', '1.2 sec'],
                ].map(([k, v]) => (
                  <div key={k} className="rounded-lg bg-slate-50 p-3">
                    <p className="text-slate-500">{k}</p>
                    <p className="mt-1 font-semibold">{v}</p>
                  </div>
                ))}
              </div>
            </article>

            <article className="rounded-xl bg-white p-6 shadow-sm">
              <h3 className="text-xl font-semibold">System Health</h3>
              <div className="mt-4 space-y-3 text-sm">
                {[
                  ['API Server', '99.98% uptime'],
                  ['Database', '45/100 pool usage'],
                  ['AI Scribe Service', '78% utilization'],
                  ['Document OCR', '96.8% success rate'],
                ].map(([k, v]) => (
                  <div key={k} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                    <span>{k}</span>
                    <span className="font-medium">{v}</span>
                  </div>
                ))}
              </div>
            </article>
          </section>

          <section className="mt-6 rounded-xl bg-white p-6 shadow-sm">
            <h3 className="text-xl font-semibold">Active Doctors</h3>
            <div className="mt-4 space-y-3">
              {[
                ['Dr. Priya Sharma', 'Internal Medicine', '48 patients this week'],
                ['Dr. Suresh Nair', 'Ayurveda Specialist', '32 patients this week'],
                ['Dr. Rahul Kapoor', 'General Surgery', '24 patients this week'],
              ].map(([name, specialty, stats]) => (
                <div key={name} className="flex items-center justify-between rounded-lg bg-slate-50 p-3">
                  <div>
                    <p className="font-medium">{name}</p>
                    <p className="text-sm text-slate-500">{specialty}</p>
                  </div>
                  <p className="text-sm text-slate-600">{stats}</p>
                </div>
              ))}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
