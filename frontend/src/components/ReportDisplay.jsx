import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, HelpCircle } from 'lucide-react';

// This is a "dumb" component. It just receives the report data and displays it.
// The `report` prop will look like: { diseases: ["..."], questions: ["..."] }
export default function ReportDisplay({ report }) {
  const { diseases, questions } = report;

  // Common style for list items
  const listItemStyle = {
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '8px',
    padding: '10px 14px',
    marginBottom: '8px',
    fontSize: '14px',
    color: '#e0e0e0',
  };

  // Common style for section headers
  const headerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#10a37f', // Green accent
    marginBottom: '10px',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        background: 'rgba(16, 163, 127, 0.05)', // Faint green background
        border: '1px solid #10a37f',
        borderRadius: '14px',
        padding: '20px',
        marginTop: '10px',
        color: '#f9fafb',
      }}
    >
      {/* This layout stacks the two lists vertically */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        {/* Section 1: Possible Conditions */}
        <div>
          <h3 style={headerStyle}>
            <AlertTriangle size={18} />
            Possible Conditions
          </h3>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {diseases.map((disease, i) => (
              <li key={i} style={listItemStyle}>
                {disease}
              </li>
            ))}
          </ul>
        </div>

        {/* Section 2: Questions for Your Doctor */}
        <div>
          <h3 style={headerStyle}>
            <HelpCircle size={18} />
            Questions for Your Doctor
          </h3>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {questions.map((q, i) => (
              <li key={i} style={listItemStyle}>
                {q}
              </li>
            ))}
          </ul>
        </div>

      </div>
    </motion.div>
  );
}
