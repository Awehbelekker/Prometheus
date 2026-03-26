import { initializeApp, FirebaseApp } from 'firebase/app';
import { getAuth, connectAuthEmulator, Auth } from 'firebase/auth';
import { getFirestore, connectFirestoreEmulator, Firestore } from 'firebase/firestore';
import { getStorage, connectStorageEmulator, FirebaseStorage } from 'firebase/storage';
import { getFunctions, connectFunctionsEmulator, Functions } from 'firebase/functions';

// Development mode - bypass Firebase for local testing
const isDevelopment = process.env.NODE_ENV === 'development' || process.env.REACT_APP_DEV_MODE === 'true';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "ai-mass-trading.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "ai-mass-trading",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "ai-mass-trading.appspot.com",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "1046048153364",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:1046048153364:web:XXXXXXXXXXXXXXXXXXXX"
};

// Initialize Firebase only if not in development mode
let app: FirebaseApp | undefined;
let auth: Auth | null = null;
let db: Firestore | null = null;
let storage: FirebaseStorage | null = null;
let functions: Functions | null = null;

if (!isDevelopment) {
  try {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);
    storage = getStorage(app);
    functions = getFunctions(app);
  } catch (error) {
    console.error('Failed to initialize Firebase:', error);
    // Set to null if initialization fails
    auth = null;
    db = null;
    storage = null;
    functions = null;
  }
} else {
  // Mock Firebase services for development
  console.log('Firebase disabled for local development');
  auth = null;
  db = null;
  storage = null;
  functions = null;
}

// Connect to emulators in development
if (isDevelopment && auth && db && storage && functions) {
  try {
    connectAuthEmulator(auth, 'http://localhost:9099');
    connectFirestoreEmulator(db, 'localhost', 8080);
    connectStorageEmulator(storage, 'localhost', 9199);
    connectFunctionsEmulator(functions, 'localhost', 5001);
  } catch (error) {
    console.log('Firebase emulators already connected or not available');
  }
}

export { auth, db, storage, functions };
export default app; 