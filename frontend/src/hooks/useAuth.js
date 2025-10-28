// frontend/src/hooks/useAuth.js

import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

// Create and export the custom hook
export const useAuth = () => useContext(AuthContext);
