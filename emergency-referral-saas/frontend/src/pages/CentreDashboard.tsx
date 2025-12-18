import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PatientForm } from '../components/PatientForm';
import { apiService, PatientResponse, ReferralResponse, HealthCenter, ReferralCreate } from '../services/api';
import { websocketService, WebSocketMessage } from '../services/websocket';
import { NotificationToast } from '../components/NotificationToast';

interface Notification {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

export const CentreDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [patients, setPatients] = useState<PatientResponse[]>([]);
  const [referrals, setReferrals] = useState<ReferralResponse[]>([]);
  const [healthCenters, setHealthCenters] = useState<HealthCenter[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showReferralModal, setShowReferralModal] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<PatientResponse | null>(null);
  const [referralForm, setReferralForm] = useState<ReferralCreate>({
    patient_id: 0,
    to_center_id: 0,
    reason: '',
    clinical_notes: '',
  });

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    // Load data
    loadPatients();
    loadReferrals();
    loadHealthCenters();

    // Connect to WebSocket
    websocketService.connect();
    const unsubscribe = websocketService.subscribe((message: WebSocketMessage) => {
      if (message.event === 'new_referral' || message.event === 'referral_accepted') {
        addNotification({
          id: Date.now(),
          message:
            message.event === 'new_referral'
              ? 'New referral created'
              : 'Referral accepted',
          type: 'info',
        });
        loadPatients();
        loadReferrals();
      }
    });

    return () => {
      unsubscribe();
    };
  }, [user, navigate]);

  const loadPatients = async () => {
    try {
      setIsLoading(true);
      const data = await apiService.getPatients();
      setPatients(data);
    } catch (error) {
      console.error('Failed to load patients:', error);
      addNotification({
        id: Date.now(),
        message: 'Failed to load patients',
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadReferrals = async () => {
    try {
      const data = await apiService.getReferrals();
      setReferrals(data);
    } catch (error) {
      console.error('Failed to load referrals:', error);
    }
  };

  const loadHealthCenters = async () => {
    try {
      const data = await apiService.getHealthCenters();
      // Filter to only show CHU centers
      const chuCenters = data.filter(hc => hc.center_type === 'CHU');
      setHealthCenters(chuCenters);
    } catch (error) {
      console.error('Failed to load health centers:', error);
    }
  };

  const handlePatientCreated = async (patientId: number) => {
    try {
      addNotification({
        id: Date.now(),
        message: 'Patient registered successfully',
        type: 'success',
      });
      // Reload patients and referrals (referral may be auto-created)
      setTimeout(() => {
        loadPatients();
        loadReferrals();
      }, 500);
    } catch (error) {
      addNotification({
        id: Date.now(),
        message: 'Failed to register patient',
        type: 'error',
      });
    }
  };

  const handleReferPatient = (patient: PatientResponse) => {
    setSelectedPatient(patient);
    setReferralForm({
      patient_id: patient.id,
      to_center_id: healthCenters[0]?.id || 0,
      reason: '',
      clinical_notes: '',
    });
    setShowReferralModal(true);
  };

  const handleCreateReferral = async () => {
    if (!referralForm.to_center_id) {
      addNotification({
        id: Date.now(),
        message: 'Please select a CHU',
        type: 'error',
      });
      return;
    }

    try {
      await apiService.createReferral(referralForm);
      addNotification({
        id: Date.now(),
        message: 'Referral created successfully',
        type: 'success',
      });
      setShowReferralModal(false);
      loadReferrals();
    } catch (error) {
      addNotification({
        id: Date.now(),
        message: error instanceof Error ? error.message : 'Failed to create referral',
        type: 'error',
      });
    }
  };

  const getPatientReferralStatus = (patientId: number): string | null => {
    const referral = referrals.find(r => r.patient_id === patientId);
    return referral ? referral.status : null;
  };

  const hasActiveReferral = (patientId: number): boolean => {
    const referral = referrals.find(r => r.patient_id === patientId);
    return referral ? ['CREATED', 'SENT', 'ACCEPTED'].includes(referral.status) : false;
  };

  const addNotification = (notification: Notification) => {
    setNotifications((prev) => [...prev, notification]);
  };

  const removeNotification = (id: number) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const getUrgencyColor = (triageLevel?: string) => {
    switch (triageLevel) {
      case 'CRITICAL':
        return 'bg-red-500';
      case 'HIGH':
        return 'bg-orange-500';
      case 'MEDIUM':
        return 'bg-yellow-500';
      case 'LOW':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Centre de Santé Dashboard</h1>
            <p className="text-sm text-gray-600">Welcome, {user.full_name}</p>
          </div>
          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            className="text-red-600 hover:text-red-700"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Patient Registration Form */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Patient Registration</h2>
            <PatientForm
              healthCenterId={user.health_center_id || 1}
              onPatientCreated={handlePatientCreated}
            />
          </div>

          {/* Patient List */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Patients</h2>
            {isLoading ? (
              <p className="text-gray-500">Loading patients...</p>
            ) : patients.length === 0 ? (
              <p className="text-gray-500">No patients registered yet</p>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {patients.map((patient) => (
                  <div
                    key={patient.id}
                    className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="font-medium">
                          {patient.first_name} {patient.last_name}
                        </div>
                        <div className="text-sm text-gray-600">
                          Age: {patient.age} | {patient.gender}
                        </div>
                        {patient.triage_level && (
                          <span
                            className={`${getUrgencyColor(
                              patient.triage_level
                            )} text-white px-2 py-1 rounded text-xs font-medium inline-block mt-1`}
                          >
                            {patient.triage_level}
                          </span>
                        )}
                        {getPatientReferralStatus(patient.id) && (
                          <div className="text-xs text-gray-500 mt-1">
                            Referral: {getPatientReferralStatus(patient.id)}
                          </div>
                        )}
                      </div>
                      {!hasActiveReferral(patient.id) && (
                        <button
                          onClick={() => handleReferPatient(patient)}
                          className="ml-2 px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                        >
                          Refer
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Referrals Section */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Referrals</h2>
          {isLoading ? (
            <p>Loading referrals...</p>
          ) : referrals.length === 0 ? (
            <p className="text-gray-500">No referrals yet</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {referrals.map((referral) => (
                <div
                  key={referral.id}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-semibold">Referral #{referral.id}</span>
                    <span
                      className={`${
                        referral.status === 'ACCEPTED'
                          ? 'bg-green-500'
                          : referral.status === 'SENT'
                          ? 'bg-yellow-500'
                          : 'bg-gray-500'
                      } text-white px-2 py-1 rounded text-xs`}
                    >
                      {referral.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    Patient ID: {referral.patient_id}
                  </div>
                  <div className="text-sm text-gray-600">
                    Priority: {referral.priority}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Referral Modal */}
      {showReferralModal && selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold mb-4">
              Refer Patient: {selectedPatient.first_name} {selectedPatient.last_name}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Select CHU</label>
                <select
                  value={referralForm.to_center_id}
                  onChange={(e) =>
                    setReferralForm({ ...referralForm, to_center_id: parseInt(e.target.value) })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value={0}>Select a CHU</option>
                  {healthCenters.map((hc) => (
                    <option key={hc.id} value={hc.id}>
                      {hc.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Reason</label>
                <textarea
                  value={referralForm.reason}
                  onChange={(e) =>
                    setReferralForm({ ...referralForm, reason: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Clinical Notes</label>
                <textarea
                  value={referralForm.clinical_notes}
                  onChange={(e) =>
                    setReferralForm({ ...referralForm, clinical_notes: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows={3}
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleCreateReferral}
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                >
                  Create Referral
                </button>
                <button
                  onClick={() => setShowReferralModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Notifications */}
      {notifications.map((notification) => (
        <NotificationToast
          key={notification.id}
          message={notification.message}
          type={notification.type}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
};

