import Link from 'next/link';

export default function PatientPortalPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-100 to-slate-100">
      <header className="border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
          <h1 className="text-2xl font-semibold text-slate-900">Integ<span className="text-blue-600">Med</span></h1>
          <div className="rounded-xl bg-blue-50 px-4 py-2 text-sm text-blue-900">Rajesh Kumar | Patient #12345</div>
        </div>
      </header>

      <section className="bg-gradient-to-r from-sky-800 to-slate-900 px-6 py-10 text-white">
        <div className="mx-auto w-full max-w-7xl">
          <h2 className="text-4xl font-semibold">Welcome back, Rajesh</h2>
          <p className="mt-2 text-sm text-sky-100">Your health dashboard | Last updated today at 10:30 AM</p>
          <div className="mt-6 grid gap-4 md:grid-cols-4">
            {[
              ['3', 'Active Prescriptions'],
              ['1', 'Upcoming Appointment'],
              ['12', 'Health Records'],
              ['2', 'Pending Consents'],
            ].map(([value, label]) => (
              <div key={label} className="rounded-xl border border-white/20 bg-white/10 p-4">
                <p className="text-3xl font-semibold">{value}</p>
                <p className="text-sm text-sky-100">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <main className="mx-auto grid w-full max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[250px_1fr]">
        <aside className="h-fit rounded-xl bg-white p-3 shadow-sm">
          <div className="mb-3 rounded-lg border border-slate-200 bg-slate-50 p-3">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Navigate</p>
            <div className="flex flex-col gap-2 text-sm">
              <Link href="/" className="rounded px-2 py-1 hover:bg-slate-200">Home</Link>
              <Link href="/dashboard" className="rounded px-2 py-1 hover:bg-slate-200">Doctor Dashboard</Link>
              <Link href="/dashboard/mockup" className="rounded px-2 py-1 hover:bg-slate-200">Doctor Mockup</Link>
              <Link href="/admin" className="rounded px-2 py-1 hover:bg-slate-200">Clinic Admin</Link>
              <Link href="/login" className="rounded px-2 py-1 hover:bg-slate-200">Login</Link>
            </div>
          </div>
          {['Dashboard', 'Prescriptions', 'Lab Reports', 'Appointments', 'Consent Requests', 'Health Timeline', 'Settings'].map(
            (item, index) => (
              <div
                key={item}
                className={`mb-1 rounded-lg px-3 py-2 text-sm ${index === 0 ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-slate-100'}`}
              >
                {item}
              </div>
            )
          )}
        </aside>

        <div className="space-y-6">
          <section className="rounded-xl bg-white p-6 shadow-sm">
            <h3 className="text-2xl font-semibold">Pending Consent Requests</h3>
            <div className="mt-4 space-y-4">
              <article className="rounded-xl border-2 border-amber-300 bg-amber-50 p-4">
                <p className="font-semibold">Health Record Access Request</p>
                <p className="text-sm text-slate-600">Dr. Priya Sharma requested records for clinical consultation.</p>
                <div className="mt-3 flex gap-2">
                  <button className="rounded-lg bg-green-700 px-4 py-2 text-sm text-white">Approve</button>
                  <button className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm">Deny</button>
                </div>
              </article>

              <article className="rounded-xl border-2 border-green-300 bg-green-50 p-4">
                <p className="font-semibold">AYUSH Center Access Request</p>
                <p className="text-sm text-slate-600">Dr. Suresh Nair requested access for treatment planning.</p>
                <div className="mt-3 flex gap-2">
                  <button className="rounded-lg bg-green-700 px-4 py-2 text-sm text-white">Approve</button>
                  <button className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm">Deny</button>
                </div>
              </article>
            </div>
          </section>

          <section className="rounded-xl bg-white p-6 shadow-sm">
            <h3 className="text-2xl font-semibold">Recent Prescriptions</h3>
            <div className="mt-4 space-y-3">
              <article className="rounded-xl border border-blue-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Feb 9, 2026 | Dr. Priya Sharma</p>
                <p className="mt-2 font-medium">METFORMIN 1000mg, AMLODIPINE 5mg, Triphala Churna</p>
                <p className="text-sm text-slate-600">Status: Active</p>
              </article>
              <article className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Jan 15, 2026 | Dr. Suresh Nair</p>
                <p className="mt-2 font-medium">Ashwagandha Churna, Brahmi Ghrita</p>
                <p className="text-sm text-slate-600">Status: Completed</p>
              </article>
            </div>
          </section>

          <section className="rounded-xl bg-white p-6 shadow-sm">
            <h3 className="text-2xl font-semibold">Health Timeline</h3>
            <div className="mt-4 space-y-3 border-l-2 border-slate-200 pl-4">
              <article className="rounded-lg bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Feb 9, 2026</p>
                <p className="font-medium">Consultation - Internal Medicine</p>
                <p className="text-sm text-slate-600">BP 140/90, Weight 75kg, BMI 26.2</p>
              </article>
              <article className="rounded-lg bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Jan 15, 2026</p>
                <p className="font-medium">Wearable Data Summary</p>
                <p className="text-sm text-slate-600">HRV 42 ms, Sleep 78/100, Daily steps 7200</p>
              </article>
              <article className="rounded-lg bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Dec 15, 2025</p>
                <p className="font-medium">Laboratory Results</p>
                <p className="text-sm text-slate-600">HbA1c 7.8%, Fasting Glucose 142 mg/dL</p>
              </article>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
