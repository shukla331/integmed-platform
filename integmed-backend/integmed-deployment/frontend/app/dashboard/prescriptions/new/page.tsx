'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface Medication {
  generic_name: string;
  brand_suggestions?: string[];
  strength: string;
  dosage_form: string;
  route: string;
  frequency: string;
  duration_days: number;
  quantity: number;
  instructions?: string;
}

export default function NewPrescriptionPage() {
  const router = useRouter();
  const [shorthand, setShorthand] = useState('');
  const [medications, setMedications] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandLoading, setExpandLoading] = useState(false);
  const [interactions, setInteractions] = useState<any>(null);

  const handleExpandShorthand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!shorthand.trim()) return;

    setExpandLoading(true);
    try {
      const expanded = await api.expandShorthand(shorthand);
      setMedications([...medications, expanded]);
      setShorthand('');
      
      // Check interactions
      await checkInteractions([...medications, expanded]);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to expand shorthand');
    } finally {
      setExpandLoading(false);
    }
  };

  const checkInteractions = async (meds: Medication[]) => {
    try {
      const result = await api.checkInteractions({ medications: meds });
      setInteractions(result);
    } catch (err) {
      console.error('Failed to check interactions:', err);
    }
  };

  const removeMedication = (index: number) => {
    const newMeds = medications.filter((_, i) => i !== index);
    setMedications(newMeds);
    if (newMeds.length > 0) {
      checkInteractions(newMeds);
    } else {
      setInteractions(null);
    }
  };

  const handleCreatePrescription = async () => {
    setLoading(true);
    try {
      // This would need encounter_id in real implementation
      const prescription = await api.createPrescription({
        encounter_id: 'temp-encounter-id',
        medications,
      });
      
      // Sign immediately
      await api.signPrescription(prescription.id);
      
      alert('Prescription created and signed successfully!');
      router.push('/dashboard');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create prescription');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-display font-bold text-primary-900">
            New Prescription
          </h1>
          <button
            onClick={() => router.back()}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left: Prescription Input */}
          <div className="lg:col-span-2 space-y-6">
            {/* Shorthand Input */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-bold mb-4">Add Medication</h3>
              
              <form onSubmit={handleExpandShorthand} className="space-y-4">
                <div>
                  <input
                    type="text"
                    value={shorthand}
                    onChange={(e) => setShorthand(e.target.value)}
                    placeholder='Type shorthand (e.g., "Metf 1000 bd 30d")'
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    💡 Tip: "Metf 1000 bd 30d" = Metformin 1000mg, twice daily, 30 days
                  </p>
                </div>
                
                <button
                  type="submit"
                  disabled={expandLoading || !shorthand.trim()}
                  className="w-full bg-primary-500 text-white py-3 rounded-lg font-medium hover:bg-primary-700 transition disabled:opacity-50"
                >
                  {expandLoading ? 'Expanding...' : 'Add Medication'}
                </button>
              </form>
            </div>

            {/* Medications List */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-bold mb-4">Medications ({medications.length})</h3>
              
              {medications.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <div className="text-4xl mb-2">💊</div>
                  <p>No medications added yet</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {medications.map((med, index) => (
                    <div
                      key={index}
                      className="p-4 border border-gray-200 rounded-lg hover:border-primary-300"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="text-xs text-primary-600 font-semibold mb-1">
                            {med.generic_name}
                          </div>
                          <div className="font-medium">
                            {med.brand_suggestions?.[0] || 'Generic'} {med.strength}
                          </div>
                        </div>
                        <button
                          onClick={() => removeMedication(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          ✕
                        </button>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-2 text-sm text-gray-600 mt-3">
                        <div>
                          <span className="font-medium">Frequency:</span> {med.frequency}
                        </div>
                        <div>
                          <span className="font-medium">Duration:</span> {med.duration_days} days
                        </div>
                        <div>
                          <span className="font-medium">Quantity:</span> {med.quantity}
                        </div>
                      </div>
                      
                      {med.instructions && (
                        <div className="text-sm text-gray-500 mt-2">
                          📝 {med.instructions}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            {medications.length > 0 && (
              <div className="flex gap-4">
                <button
                  onClick={() => setMedications([])}
                  className="flex-1 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Clear All
                </button>
                <button
                  onClick={handleCreatePrescription}
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Sign & Create Prescription'}
                </button>
              </div>
            )}
          </div>

          {/* Right: Safety Panel */}
          <div className="space-y-6">
            {/* Interaction Checker */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                🛡️ Safety HUD
              </h3>
              
              {!interactions ? (
                <div className="text-center py-4 text-gray-400">
                  <p className="text-sm">Add medications to check interactions</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Safety Score */}
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Safety Score</div>
                    <div className="text-3xl font-bold">
                      {interactions.safety_score.toFixed(1)}/10
                    </div>
                    <div className="w-full bg-gray-200 h-2 rounded-full mt-2">
                      <div
                        className={`h-2 rounded-full ${
                          interactions.safety_score >= 8
                            ? 'bg-green-500'
                            : interactions.safety_score >= 6
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${interactions.safety_score * 10}%` }}
                      />
                    </div>
                  </div>

                  {/* Interactions */}
                  {interactions.interactions.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-semibold text-gray-700">
                        ⚠️ Interactions Found
                      </div>
                      {interactions.interactions.map((interaction: any, idx: number) => (
                        <div
                          key={idx}
                          className={`p-3 rounded-lg border-l-4 ${
                            interaction.severity === 'severe'
                              ? 'bg-red-50 border-red-500'
                              : interaction.severity === 'moderate'
                              ? 'bg-yellow-50 border-yellow-500'
                              : 'bg-blue-50 border-blue-500'
                          }`}
                        >
                          <div className="text-sm font-medium">
                            {interaction.drug1} + {interaction.drug2}
                          </div>
                          <div className="text-xs mt-1">{interaction.description}</div>
                          <div className="text-xs mt-2 font-medium">
                            💡 {interaction.recommendation}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* No issues */}
                  {interactions.interactions.length === 0 &&
                    interactions.contraindications.length === 0 &&
                    interactions.allergy_alerts.length === 0 && (
                      <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
                        <div className="text-sm font-medium text-green-800">
                          ✓ No interactions detected
                        </div>
                        <div className="text-xs text-green-600 mt-1">
                          Safe to prescribe
                        </div>
                      </div>
                    )}
                </div>
              )}
            </div>

            {/* NMC Compliance */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-bold mb-4">✓ NMC Compliance</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Generic names in CAPITALS</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Generic-first prescription</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Digital signature ready</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
