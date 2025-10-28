import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Hospital, Loader2, MapPin, AlertTriangle } from 'lucide-react';
import api from '../services/api.js'; // 👈 FIXED: Added .js extension to resolve path

// Helper component for loading spinner
const LoadingSpinner = () => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
    style={{ display: 'inline-block' }}
  >
    <Loader2 size={16} />
  </motion.div>
);

export default function HospitalFinder() {
  const [hospitals, setHospitals] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFindHospitals = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setHospitals([]);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          const data = await api.findHospitals(latitude, longitude);
          if (data.hospitals && data.hospitals.length > 0) {
            setHospitals(data.hospitals);
          } else {
            setError('No hospitals found nearby.');
          }
        } catch (err) {
          console.error('Error finding hospitals:', err);
          setError('Failed to fetch hospital data.');
        } finally {
          setIsLoading(false);
        }
      },
      (geoError) => {
        console.error('Geolocation error:', geoError);
        setError('Unable to retrieve your location. Please grant permission.');
        setIsLoading(false);
      }
    );
  };

  return (
    <div
      style={{
        background: 'rgba(255,255,255,0.03)',
        borderRadius: '10px',
        padding: '15px',
        border: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      <button
        onClick={handleFindHospitals}
        disabled={isLoading}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          background: 'rgba(255,255,255,0.08)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '10px',
          padding: '10px 0',
          fontWeight: '600',
          color: '#e5e7eb',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          transition: 'background 0.3s',
          width: '100%',
        }}
        onMouseEnter={(e) => !isLoading && (e.currentTarget.style.background = 'rgba(255,255,255,0.15)')}
        onMouseLeave={(e) => !isLoading && (e.currentTarget.style.background = 'rgba(255,255,255,0.08)')}
      >
        {isLoading ? (
          <>
            Locating... <LoadingSpinner />
          </>
        ) : (
          <>
            <MapPin size={18} />
            Find Nearby Hospitals
          </>
        )}
      </button>

      {/* --- Results Display --- */}
      <div style={{ marginTop: '15px', maxHeight: '200px', overflowY: 'auto' }}>
        {error && (
          <div style={{ color: '#f87171', fontSize: '13px', display: 'flex', gap: '5px' }}>
            <AlertTriangle size={16} /> {error}
          </div>
        )}
        
        {hospitals.length > 0 && (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {hospitals.map((h, i) => (
              <li
                key={i}
                style={{
                  paddingBottom: '10px',
                  borderBottom: '1px solid rgba(255,255,255,0.05)',
                }}
              >
                <div style={{ fontWeight: '600', fontSize: '14px', color: '#f3f4f6', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Hospital size={14} opacity={0.8} /> {h.name}
                </div>
                <div style={{ fontSize: '13px', color: '#9ca3af', marginTop: '4px' }}>
                  {h.address}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

