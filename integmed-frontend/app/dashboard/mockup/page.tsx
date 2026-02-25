'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

type TabKey = 'dashboard' | 'scribe' | 'prescription';

const COMMANDS = [
  { title: 'Start AI Scribe', subtitle: 'Begin ambient documentation' },
  { title: 'New Prescription', subtitle: 'Write prescription with shorthand' },
  { title: 'Request ABDM Consent', subtitle: 'Fetch patient health records' },
  { title: 'Rajesh Kumar', subtitle: 'M/41 Type 2 DM, HTN' },
  { title: 'Priya Mehta', subtitle: 'F/35 Thyroid disorder' },
  { title: 'Dashboard', subtitle: 'View patient timeline' },
  { title: 'Lab Orders', subtitle: 'Order investigations' },
];

export default function DoctorMockupPage() {
  const [tab, setTab] = useState<TabKey>('dashboard');
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [query, setQuery] = useState('');

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setPaletteOpen((prev) => !prev);
      }

      if (event.key === 'Escape') {
        setPaletteOpen(false);
      }
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const filteredCommands = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return COMMANDS;
    return COMMANDS.filter(
      (item) =>
        item.title.toLowerCase().includes(normalized) || item.subtitle.toLowerCase().includes(normalized)
    );
  }, [query]);

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
          <h1 className="text-2xl font-semibold text-slate-900">Integ<span className="text-blue-600">Med</span></h1>
          <div className="flex items-center gap-3">
            <Link href="/" className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-100">
              Home
            </Link>
            <Link href="/dashboard" className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-100">
              Dashboard
            </Link>
            <Link href="/admin" className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-100">
              Admin
            </Link>
            <Link href="/patient-portal" className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-100">
              Patient Portal
            </Link>
            <button
              onClick={() => setPaletteOpen(true)}
              className="rounded-lg border border-slate-200 bg-slate-100 px-3 py-2 text-sm text-slate-600"
            >
              Search  Ctrl+K
            </button>
            <div className="rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-800">Dr. Priya Sharma</div>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl px-6 py-8">
        <h2 className="text-4xl font-semibold tracking-tight text-slate-900">Clinical Workspace</h2>
        <p className="mt-2 text-slate-600">Integrated timeline, AI scribe, and prescription safety panel.</p>

        <div className="mt-6 flex gap-2 border-b border-slate-200">
          {(['dashboard', 'scribe', 'prescription'] as TabKey[]).map((key) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`rounded-t-lg px-4 py-3 text-sm font-medium capitalize ${
                tab === key ? 'border-b-2 border-blue-600 text-blue-700' : 'text-slate-500'
              }`}
            >
              {key}
            </button>
          ))}
        </div>

        {tab === 'dashboard' && (
          <section className="mt-6 grid gap-6 lg:grid-cols-[1fr_320px]">
            <div className="space-y-6">
              <div className="rounded-2xl bg-gradient-to-r from-sky-800 to-slate-900 p-6 text-white shadow-lg">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-2xl font-semibold">Rajesh Kumar</h3>
                    <p className="mt-1 text-sm text-sky-100">M/41 | Type 2 DM | ABHA linked</p>
                  </div>
                  <span className="rounded-md bg-white/20 px-2 py-1 text-xs">Follow-up</span>
                </div>
                <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">
                  {[
                    ['BP', '140/90'],
                    ['HR', '78'],
                    ['Glucose', '142'],
                    ['Weight', '75kg'],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-lg border border-white/20 bg-white/10 p-3">
                      <div className="text-xs text-sky-100">{label}</div>
                      <div className="text-xl font-semibold">{value}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl bg-white p-6 shadow">
                <h4 className="text-xl font-semibold text-slate-900">Health Timeline</h4>
                <div className="mt-5 space-y-4 border-l-2 border-slate-200 pl-4">
                  <article className="rounded-lg bg-slate-50 p-4">
                    <p className="text-xs text-slate-500">Feb 9, 2026</p>
                    <p className="font-medium text-slate-900">Consultation completed</p>
                    <p className="text-sm text-slate-600">HbA1c trend up. Diet counseling reinforced.</p>
                  </article>
                  <article className="rounded-lg bg-amber-50 p-4">
                    <p className="text-xs text-slate-500">Jan 15, 2026</p>
                    <p className="font-medium text-slate-900">Ayurveda review</p>
                    <p className="text-sm text-slate-600">Added Triphala with glucose monitoring advice.</p>
                  </article>
                </div>
              </div>
            </div>

            <aside className="rounded-xl bg-white p-6 shadow">
              <h4 className="text-lg font-semibold text-slate-900">Quick Actions</h4>
              <div className="mt-4 space-y-2">
                {['Start AI Scribe', 'New Prescription', 'Request Consent', 'Send to Locker'].map((item) => (
                  <button key={item} className="w-full rounded-lg border border-slate-200 px-3 py-2 text-left text-sm hover:bg-slate-50">
                    {item}
                  </button>
                ))}
              </div>
              <div className="mt-6 rounded-lg border-l-4 border-amber-500 bg-amber-50 p-3 text-sm text-amber-900">
                Alert: HbA1c trending upward.
              </div>
            </aside>
          </section>
        )}

        {tab === 'scribe' && (
          <section className="mt-6 grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl bg-slate-900 p-6 text-white shadow">
              <h4 className="text-lg font-semibold">Live Recording</h4>
              <div className="mt-6 flex h-40 items-end justify-center gap-1">
                {Array.from({ length: 16 }).map((_, index) => (
                  <div
                    key={index}
                    className="w-1 rounded bg-sky-400"
                    style={{ height: `${20 + ((index * 13) % 60)}px` }}
                  />
                ))}
              </div>
              <p className="mt-6 text-sm text-slate-200">
                Patient reports fatigue for 2 weeks, increased thirst, frequent urination, and fasting glucose
                140 to 160 mg/dL.
              </p>
              <div className="mt-6 flex gap-2">
                <button className="rounded-lg border border-slate-600 px-4 py-2 text-sm">Pause</button>
                <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm">Stop and Generate</button>
              </div>
            </div>

            <div className="rounded-xl bg-white p-6 shadow">
              <h4 className="text-lg font-semibold text-slate-900">Auto-generated SOAP</h4>
              <div className="mt-4 space-y-4 text-sm">
                <div>
                  <p className="font-semibold text-blue-700">Subjective</p>
                  <p className="text-slate-700">Persistent fatigue, thirst, and frequent urination.</p>
                </div>
                <div>
                  <p className="font-semibold text-blue-700">Objective</p>
                  <p className="text-slate-700">BP 140/90, pulse 78, HbA1c 7.8%, fasting glucose 142 mg/dL.</p>
                </div>
                <div>
                  <p className="font-semibold text-blue-700">Assessment</p>
                  <p className="text-slate-700">Type 2 Diabetes Mellitus poorly controlled. Stage 1 hypertension.</p>
                </div>
                <div>
                  <p className="font-semibold text-blue-700">Plan</p>
                  <p className="text-slate-700">Increase Metformin, start Amlodipine, labs in 2 weeks.</p>
                </div>
              </div>
            </div>
          </section>
        )}

        {tab === 'prescription' && (
          <section className="mt-6 grid gap-6 lg:grid-cols-[2fr_1fr]">
            <div className="rounded-xl bg-white p-6 shadow">
              <h4 className="text-lg font-semibold text-slate-900">Prescription Editor</h4>
              <input
                className="mt-4 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm"
                placeholder="Metf 1000 bd 30d"
                readOnly
              />
              <div className="mt-4 space-y-3">
                <div className="rounded-lg border-l-4 border-blue-600 bg-slate-50 p-4">
                  <p className="font-semibold text-slate-900">METFORMIN 1000mg</p>
                  <p className="text-sm text-slate-600">BD | 30 days | after meals</p>
                </div>
                <div className="rounded-lg border-l-4 border-blue-600 bg-slate-50 p-4">
                  <p className="font-semibold text-slate-900">AMLODIPINE 5mg</p>
                  <p className="text-sm text-slate-600">OD | 30 days | bedtime</p>
                </div>
                <div className="rounded-lg border-l-4 border-amber-700 bg-amber-50 p-4">
                  <p className="font-semibold text-slate-900">Triphala Churna</p>
                  <p className="text-sm text-slate-600">5g BD | before meals | warm water</p>
                </div>
              </div>
            </div>

            <aside className="rounded-xl bg-white p-6 shadow">
              <h4 className="text-lg font-semibold text-slate-900">Safety HUD</h4>
              <div className="mt-4 rounded-lg border-l-4 border-amber-500 bg-amber-50 p-3 text-sm text-amber-900">
                Moderate interaction: Triphala may enhance Metformin effects. Monitor glucose.
              </div>
              <ul className="mt-4 space-y-2 text-sm text-slate-700">
                <li>OK Generic names in capitals</li>
                <li>OK Generic-first prescription</li>
                <li>OK Credentials verified</li>
              </ul>
            </aside>
          </section>
        )}
      </main>

      {paletteOpen && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 p-6 pt-20"
          onClick={() => setPaletteOpen(false)}
        >
          <div className="w-full max-w-2xl rounded-xl bg-white shadow-xl" onClick={(event) => event.stopPropagation()}>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search actions, patients, navigation..."
              className="w-full border-b border-slate-200 px-4 py-3 text-sm outline-none"
            />
            <div className="max-h-96 overflow-auto p-2">
              {filteredCommands.map((item) => (
                <div key={item.title} className="rounded-lg px-3 py-2 hover:bg-slate-100">
                  <p className="text-sm font-medium text-slate-900">{item.title}</p>
                  <p className="text-xs text-slate-500">{item.subtitle}</p>
                </div>
              ))}
              {filteredCommands.length === 0 && <p className="px-3 py-4 text-sm text-slate-500">No results</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
