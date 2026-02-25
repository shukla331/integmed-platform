'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function AIScribePage() {
  const router = useRouter();
  const { user } = useAuthStore();

  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [soapNote, setSoapNote] = useState({
    subjective: '',
    objective: '',
    assessment: '',
    plan: '',
  });
  const [recordingTime, setRecordingTime] = useState(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording]);

  const handleStartRecording = () => {
    setIsRecording(true);
    setRecordingTime(0);
    setTranscript('');

    setTimeout(() => {
      setTranscript((prev) => `${prev}Patient presents with fatigue, increased thirst, and frequent urination. `);
    }, 2000);
  };

  const handleStopRecording = () => {
    setIsRecording(false);

    setTimeout(() => {
      setSoapNote({
        subjective:
          'Patient reports persistent fatigue for 2 weeks, increased thirst and urination. No fever, no weight loss. Denies smoking or alcohol use.',
        objective:
          'BP 140/90 mmHg, Pulse 78 bpm, Temperature 98.6 F, Weight 75 kg, Height 170 cm. Patient appears tired but in no acute distress.',
        assessment:
          'Type 2 Diabetes Mellitus, likely new onset. Differential diagnosis includes stress-induced hyperglycemia. Labs pending: HbA1c, fasting glucose, lipid profile.',
        plan:
          'Start Metformin 500mg twice daily after meals for 30 days. Order HbA1c, fasting glucose, lipid profile. Diet counseling and daily 30-minute walk. Follow-up in 2 weeks.',
      });
    }, 1500);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-900">
            Integ<span className="text-blue-500">Med</span>
          </h1>
          <div className="text-sm text-gray-600">{user?.name}</div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="mb-6">
          <button onClick={() => router.push('/dashboard')} className="text-blue-600 hover:text-blue-800 text-sm">
            {'<-'} Back to Dashboard
          </button>
        </div>

        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">AI Medical Scribe</h2>
          <p className="text-gray-600">Ambient voice documentation with automatic SOAP note generation</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h3 className="text-lg font-bold text-gray-900 mb-6">Voice Recording</h3>

              <div className="flex justify-center mb-8">
                <div
                  className={`relative w-32 h-32 rounded-full flex items-center justify-center ${
                    isRecording ? 'bg-red-100 animate-pulse' : 'bg-gray-100'
                  }`}
                >
                  <span className="text-5xl">{isRecording ? 'REC' : 'MIC'}</span>
                  {isRecording && <div className="absolute inset-0 rounded-full border-4 border-red-500 animate-ping" />}
                </div>
              </div>

              {isRecording && (
                <div className="text-center mb-6">
                  <div className="text-4xl font-mono font-bold text-red-600">{formatTime(recordingTime)}</div>
                  <div className="text-sm text-gray-500 mt-1">Recording in progress...</div>
                </div>
              )}

              <div className="flex gap-4">
                {!isRecording ? (
                  <button
                    onClick={handleStartRecording}
                    className="flex-1 bg-blue-600 text-white py-4 rounded-xl font-bold text-lg hover:bg-blue-700 transition"
                  >
                    Start Recording
                  </button>
                ) : (
                  <button
                    onClick={handleStopRecording}
                    className="flex-1 bg-red-600 text-white py-4 rounded-xl font-bold text-lg hover:bg-red-700 transition"
                  >
                    Stop and Process
                  </button>
                )}
              </div>

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
                <strong>How to use:</strong>
                <ul className="mt-2 space-y-1">
                  <li>• Speak naturally during consultation</li>
                  <li>• Transcript appears live</li>
                  <li>• SOAP note auto-generates after stop</li>
                  <li>• Review before saving</li>
                </ul>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Live Transcript</h3>
              <div className="bg-gray-50 rounded-lg p-4 min-h-[150px] max-h-[300px] overflow-y-auto">
                {transcript ? (
                  <p className="text-gray-700">{transcript}</p>
                ) : (
                  <p className="text-gray-400 italic">Transcript will appear here during recording...</p>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-6">Generated SOAP Note</h3>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Subjective</label>
                <textarea
                  value={soapNote.subjective}
                  onChange={(e) => setSoapNote({ ...soapNote, subjective: e.target.value })}
                  placeholder="Patient symptoms and history..."
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Objective</label>
                <textarea
                  value={soapNote.objective}
                  onChange={(e) => setSoapNote({ ...soapNote, objective: e.target.value })}
                  placeholder="Exam findings and vitals..."
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Assessment</label>
                <textarea
                  value={soapNote.assessment}
                  onChange={(e) => setSoapNote({ ...soapNote, assessment: e.target.value })}
                  placeholder="Clinical assessment..."
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Plan</label>
                <textarea
                  value={soapNote.plan}
                  onChange={(e) => setSoapNote({ ...soapNote, plan: e.target.value })}
                  placeholder="Treatment and follow-up plan..."
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  disabled={!soapNote.subjective}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Save to Encounter
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 p-4 bg-amber-50 border border-amber-300 rounded-lg text-sm text-amber-900">
          <strong>Demo Mode:</strong> This is simulated AI scribe behavior. Production will use speech-to-text and medical NLP.
        </div>
      </div>
    </div>
  );
}
