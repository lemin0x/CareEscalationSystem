import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PatientForm } from '../components/PatientForm';
import { apiService, PatientResponse, ReferralResponse } from '../services/api';
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
  const [recentPatient, setRecentPatient] = useState<PatientResponse | null>(null);
  const [referrals, setReferrals] = useState<ReferralResponse[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    // Load referrals
    loadReferrals();

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
        loadReferrals();
      }
    });

    return () => {
      unsubscribe();
    };
  }, [user, navigate]);

  const loadReferrals = async () => {
    try {
      setIsLoading(true);
      const data = await apiService.getReferrals();
      setReferrals(data);
    } catch (error) {
      console.error('Failed to load referrals:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePatientCreated = async (patientId: number) => {
    try {
      // Assess triage
      const patient = await apiService.assessTriage(patientId);
      setRecentPatient(patient);
      addNotification({
        id: Date.now(),
        message: `Patient registered. Triage: ${patient.triage_level || 'N/A'}`,
        type: 'success',
      });
      // Reload referrals in case a new one was created
      setTimeout(() => loadReferrals(), 1000);
    } catch (error) {
      addNotification({
        id: Date.now(),
        message: 'Failed to assess triage',
        type: 'error',
      });
    }
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

          {/* Recent Patient Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Patient</h2>
            {recentPatient ? (
              <div className="space-y-3">
                <div>
                  <span className="font-medium">Name:</span>{' '}
                  {recentPatient.first_name} {recentPatient.last_name}
                </div>
                <div>
                  <span className="font-medium">Age:</span> {recentPatient.age}
                </div>
                <div>
                  <span className="font-medium">Triage Level:</span>{' '}
                  <span
                    className={`${getUrgencyColor(
                      recentPatient.triage_level
                    )} text-white px-3 py-1 rounded-full text-xs font-medium inline-block`}
                  >
                    {recentPatient.triage_level || 'N/A'}
                  </span>
                </div>
                {recentPatient.chief_complaint && (
                  <div>
                    <span className="font-medium">Complaint:</span>{' '}
                    {recentPatient.chief_complaint}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500">No patient registered yet</p>
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

