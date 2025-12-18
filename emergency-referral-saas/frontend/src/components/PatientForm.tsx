import React, { useState } from 'react';
import { apiService, PatientCreate } from '../services/api';

interface PatientFormProps {
  healthCenterId: number;
  onPatientCreated: (patientId: number) => void;
}

export const PatientForm: React.FC<PatientFormProps> = ({
  healthCenterId,
  onPatientCreated,
}) => {
  const [formData, setFormData] = useState<PatientCreate>({
    first_name: '',
    last_name: '',
    age: 0,
    gender: 'M',
    health_center_id: healthCenterId,
    oxygen_saturation: undefined,
    heart_rate: undefined,
    blood_pressure_systolic: undefined,
    blood_pressure_diastolic: undefined,
    temperature: undefined,
    chest_pain: false,
    chief_complaint: '',
    notes: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else if (type === 'number') {
      setFormData((prev) => ({
        ...prev,
        [name]: value === '' ? undefined : parseFloat(value),
      }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const patient = await apiService.createPatient(formData);
      onPatientCreated(patient.id);
      // Reset form
      setFormData({
        first_name: '',
        last_name: '',
        age: 0,
        gender: 'M',
        health_center_id: healthCenterId,
        oxygen_saturation: undefined,
        heart_rate: undefined,
        blood_pressure_systolic: undefined,
        blood_pressure_diastolic: undefined,
        temperature: undefined,
        chest_pain: false,
        chief_complaint: '',
        notes: '',
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create patient');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">First Name</label>
          <input
            type="text"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Last Name</label>
          <input
            type="text"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Age</label>
          <input
            type="number"
            name="age"
            value={formData.age || ''}
            onChange={handleChange}
            required
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Gender</label>
          <select
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="M">Male</option>
            <option value="F">Female</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Chief Complaint</label>
        <input
          type="text"
          name="chief_complaint"
          value={formData.chief_complaint}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Oxygen Saturation (%)</label>
          <input
            type="number"
            name="oxygen_saturation"
            value={formData.oxygen_saturation || ''}
            onChange={handleChange}
            min="0"
            max="100"
            step="0.1"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Heart Rate (bpm)</label>
          <input
            type="number"
            name="heart_rate"
            value={formData.heart_rate || ''}
            onChange={handleChange}
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Blood Pressure (Systolic)</label>
          <input
            type="number"
            name="blood_pressure_systolic"
            value={formData.blood_pressure_systolic || ''}
            onChange={handleChange}
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Blood Pressure (Diastolic)</label>
          <input
            type="number"
            name="blood_pressure_diastolic"
            value={formData.blood_pressure_diastolic || ''}
            onChange={handleChange}
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Temperature (°C)</label>
        <input
          type="number"
          name="temperature"
          value={formData.temperature || ''}
          onChange={handleChange}
          min="0"
          step="0.1"
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          name="chest_pain"
          checked={formData.chest_pain}
          onChange={handleChange}
          className="mr-2"
        />
        <label className="text-sm font-medium">Chest Pain</label>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Notes</label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {isSubmitting ? 'Registering...' : 'Register Patient'}
      </button>
    </form>
  );
};

