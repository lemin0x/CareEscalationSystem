import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ReferralCard } from '../components/ReferralCard';
import { apiService, ReferralResponse } from '../services/api';
import { websocketService, WebSocketMessage } from '../services/websocket';
import { NotificationToast } from '../components/NotificationToast';

interface Notification {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

export const CHUDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [referrals, setReferrals] = useState<ReferralResponse[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [acceptingId, setAcceptingId] = useState<number | null>(null);

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
      if (message.event === 'new_referral') {
        addNotification({
          id: Date.now(),
          message: 'New referral received!',
          type: 'info',
        });
        loadReferrals();
      } else if (message.event === 'referral_accepted') {
        addNotification({
          id: Date.now(),
          message: 'Referral accepted',
          type: 'success',
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
      // Load referrals with status SENT or CREATED (incoming referrals)
      const allReferrals = await apiService.getReferrals();
      // Filter for incoming referrals (status SENT or CREATED)
      const incomingReferrals = allReferrals.filter(
        (r) => r.status === 'SENT' || r.status === 'CREATED'
      );
      setReferrals(incomingReferrals);
    } catch (error) {
      console.error('Failed to load referrals:', error);
      addNotification({
        id: Date.now(),
        message: 'Failed to load referrals',
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAcceptReferral = async (referralId: number) => {
    try {
      setAcceptingId(referralId);
      await apiService.acceptReferral(referralId);
      addNotification({
        id: Date.now(),
        message: 'Referral accepted successfully',
        type: 'success',
      });
      loadReferrals();
    } catch (error) {
      addNotification({
        id: Date.now(),
        message: 'Failed to accept referral',
        type: 'error',
      });
    } finally {
      setAcceptingId(null);
    }
  };

  const addNotification = (notification: Notification) => {
    setNotifications((prev) => [...prev, notification]);
  };

  const removeNotification = (id: number) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">CHU Dashboard</h1>
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
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Incoming Referrals</h2>
          <p className="text-sm text-gray-600">
            Real-time updates via WebSocket. New referrals appear automatically.
          </p>
        </div>

        {isLoading ? (
          <div className="text-center py-8">
            <p className="text-gray-500">Loading referrals...</p>
          </div>
        ) : referrals.length === 0 ? (
          <div className="text-center py-8 bg-white rounded-lg shadow">
            <p className="text-gray-500">No incoming referrals at this time</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {referrals.map((referral) => (
              <ReferralCard
                key={referral.id}
                referral={referral}
                onAccept={handleAcceptReferral}
                showAcceptButton={user.role === 'doctor'}
                isAccepting={acceptingId === referral.id}
              />
            ))}
          </div>
        )}
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

