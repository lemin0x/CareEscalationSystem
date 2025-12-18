import React from 'react';
import { ReferralResponse } from '../services/api';

interface ReferralCardProps {
  referral: ReferralResponse;
  onAccept?: (referralId: number) => void;
  showAcceptButton?: boolean;
  isAccepting?: boolean;
}

export const ReferralCard: React.FC<ReferralCardProps> = ({
  referral,
  onAccept,
  showAcceptButton = false,
  isAccepting = false,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'CREATED':
        return 'bg-gray-500';
      case 'SENT':
        return 'bg-yellow-500';
      case 'ACCEPTED':
        return 'bg-green-500';
      case 'TRANSFERRED':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-semibold text-lg">Referral #{referral.id}</h3>
          <p className="text-sm text-gray-600">Patient ID: {referral.patient_id}</p>
        </div>
        <span
          className={`${getStatusColor(referral.status)} text-white px-3 py-1 rounded-full text-xs font-medium`}
        >
          {referral.status}
        </span>
      </div>

      <div className="space-y-2 text-sm">
        <div>
          <span className="font-medium">Priority:</span> {referral.priority}
        </div>
        {referral.reason && (
          <div>
            <span className="font-medium">Reason:</span> {referral.reason}
          </div>
        )}
        {referral.clinical_notes && (
          <div>
            <span className="font-medium">Clinical Notes:</span> {referral.clinical_notes}
          </div>
        )}
        <div>
          <span className="font-medium">Created:</span> {formatDate(referral.created_at)}
        </div>
        {referral.accepted_at && (
          <div>
            <span className="font-medium">Accepted:</span> {formatDate(referral.accepted_at)}
          </div>
        )}
      </div>

      {showAcceptButton && (referral.status === 'SENT' || referral.status === 'CREATED') && onAccept && (
        <button
          onClick={() => onAccept(referral.id)}
          disabled={isAccepting}
          className="mt-4 w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          {isAccepting ? 'Accepting...' : 'Accept Referral'}
        </button>
      )}
    </div>
  );
};

