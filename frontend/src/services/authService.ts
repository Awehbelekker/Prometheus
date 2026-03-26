import {
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  OAuthProvider,
  User,
  UserCredential,
  updateProfile
} from 'firebase/auth';
import {
  doc,
  setDoc,
  getDoc,
  updateDoc,
  collection,
  query,
  where,
  getDocs
} from 'firebase/firestore';
import { auth, db } from '../config/firebase';
import { apiCall } from '../config/api';


export interface UserProfile {
  uid: string;
  email: string;
  displayName?: string;
  photoURL?: string;
  role: 'admin' | 'investor' | 'beta_user' | 'developer';
  is_active: boolean;
  is_approved: boolean;
  kyc_status: 'pending' | 'approved' | 'rejected';
  tenant_id: string;
  permissions: string[];
  created_at: Date;
  updated_at: Date;
  trading_accounts?: string[];
  api_keys?: string[];
}

export interface AuthState {
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
}

class AuthService {
  private currentUser: UserProfile | null = null;
  private authStateListeners: ((state: AuthState) => void)[] = [];

  constructor() {
    this.initializeAuthStateListener();
  }

  private async initializeAuthStateListener() {
    if (!auth) {
      console.log('Firebase auth not available, skipping auth state listener');
      return;
    }

    onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          const userProfile = await this.getUserProfile(firebaseUser.uid);
          this.currentUser = userProfile;
          this.notifyListeners({ user: userProfile, loading: false, error: null });
        } catch (error) {
          console.error('Error loading user profile:', error);
          this.notifyListeners({ user: null, loading: false, error: 'Failed to load user profile' });
        }
      } else {
        this.currentUser = null;
        this.notifyListeners({ user: null, loading: false, error: null });
      }
    });
  }

  private notifyListeners(state: AuthState) {
    this.authStateListeners.forEach(listener => listener(state));
  }

  public onAuthStateChanged(listener: (state: AuthState) => void) {
    this.authStateListeners.push(listener);
    return () => {
      const index = this.authStateListeners.indexOf(listener);
      if (index > -1) {
        this.authStateListeners.splice(index, 1);
      }
    };
  }

  public async signInWithGoogle(): Promise<UserProfile> {
    try {
      if (!auth) {
        throw new Error('Firebase authentication is not available');
      }

      const provider = new GoogleAuthProvider();
      provider.addScope('email');
      provider.addScope('profile');

      const result: UserCredential = await signInWithPopup(auth, provider);
      const userProfile = await this.createOrUpdateUserProfile(result.user, 'google');

      // Send token to backend for validation
      await this.validateTokenWithBackend(result.user);

      return userProfile;
    } catch (error: any) {
      console.error('Google sign-in error:', error);
      throw new Error(error.message || 'Google sign-in failed');
    }
  }

  public async signInWithApple(): Promise<UserProfile> {
    try {
      if (!auth) {
        throw new Error('Firebase authentication is not available');
      }

      const provider = new OAuthProvider('apple.com');
      provider.addScope('email');
      provider.addScope('name');

      const result: UserCredential = await signInWithPopup(auth, provider);
      const userProfile = await this.createOrUpdateUserProfile(result.user, 'apple');

      await this.validateTokenWithBackend(result.user);

      return userProfile;
    } catch (error: any) {
      console.error('Apple sign-in error:', error);
      throw new Error(error.message || 'Apple sign-in failed');
    }
  }

  public async signInWithMicrosoft(): Promise<UserProfile> {
    try {
      if (!auth) {
        throw new Error('Firebase authentication is not available');
      }

      const provider = new OAuthProvider('microsoft.com');
      provider.addScope('email');
      provider.addScope('profile');

      const result: UserCredential = await signInWithPopup(auth, provider);
      const userProfile = await this.createOrUpdateUserProfile(result.user, 'microsoft');

      await this.validateTokenWithBackend(result.user);

      return userProfile;
    } catch (error: any) {
      console.error('Microsoft sign-in error:', error);
      throw new Error(error.message || 'Microsoft sign-in failed');
    }
  }

  public async signInWithEmail(email: string, password: string): Promise<UserProfile> {
    try {
      if (!auth) {
        throw new Error('Firebase authentication is not available');
      }

      const result: UserCredential = await signInWithEmailAndPassword(auth, email, password);
      const userProfile = await this.getUserProfile(result.user.uid);

      await this.validateTokenWithBackend(result.user);

      return userProfile;
    } catch (error: any) {
      console.error('Email sign-in error:', error);
      throw new Error(error.message || 'Email sign-in failed');
    }
  }

  public async signUpWithEmail(email: string, password: string, displayName: string): Promise<UserProfile> {
    try {
      if (!auth) {
        throw new Error('Firebase authentication is not available');
      }

      const result: UserCredential = await createUserWithEmailAndPassword(auth, email, password);

      // Update display name using updateProfile function
      if (result.user) {
        await updateProfile(result.user, { displayName });
      }

      const userProfile = await this.createOrUpdateUserProfile(result.user, 'email');

      await this.validateTokenWithBackend(result.user);

      return userProfile;
    } catch (error: any) {
      console.error('Email sign-up error:', error);
      throw new Error(error.message || 'Email sign-up failed');
    }
  }

  public async signOut(): Promise<void> {
    try {
      if (!auth) {
        throw new Error('Firebase authentication is not available');
      }

      await signOut(auth);
      this.currentUser = null;
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    } catch (error: any) {
      console.error('Sign-out error:', error);
      throw new Error(error.message || 'Sign-out failed');
    }
  }

  private async createOrUpdateUserProfile(firebaseUser: User, provider: string): Promise<UserProfile> {
    if (!db) {
      throw new Error('Firebase Firestore is not available');
    }

    const userRef = doc(db, 'users', firebaseUser.uid);
    const userSnap = await getDoc(userRef);

    if (userSnap.exists()) {
      // Update existing user
      const updateData = {
        email: firebaseUser.email,
        displayName: firebaseUser.displayName || userSnap.data().displayName,
        photoURL: firebaseUser.photoURL || userSnap.data().photoURL,
        updated_at: new Date()
      };

      await updateDoc(userRef, updateData);
      return { ...userSnap.data(), ...updateData } as UserProfile;
    } else {
      // Create new user
      const newUser: UserProfile = {
        uid: firebaseUser.uid,
        email: firebaseUser.email!,
        displayName: firebaseUser.displayName || '',
        photoURL: firebaseUser.photoURL || '',
        role: 'beta_user',
        is_active: true,
        is_approved: false,
        kyc_status: 'pending',
        tenant_id: 'default',
        permissions: ['basic_access'],
        created_at: new Date(),
        updated_at: new Date(),
        trading_accounts: [],
        api_keys: []
      };

      await setDoc(userRef, newUser);
      return newUser;
    }
  }

  private async getUserProfile(uid: string): Promise<UserProfile> {
    if (!db) {
      throw new Error('Firebase Firestore is not available');
    }

    const userRef = doc(db, 'users', uid);
    const userSnap = await getDoc(userRef);

    if (!userSnap.exists()) {
      throw new Error('User profile not found');
    }

    return userSnap.data() as UserProfile;
  }

  private async validateTokenWithBackend(firebaseUser: User): Promise<void> {
    try {
      const token = await firebaseUser.getIdToken();
      await apiCall('/api/auth/validate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          displayName: firebaseUser.displayName,
          photoURL: firebaseUser.photoURL
        })
      });
      localStorage.setItem('auth_token', token);
    } catch (error) {
      console.error('Backend validation error:', error);
      throw error;
    }
  }

  public async updateUserProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    if (!this.currentUser) {
      throw new Error('No authenticated user');
    }

    if (!db) {
      throw new Error('Firebase Firestore is not available');
    }

    try {
      const userRef = doc(db, 'users', this.currentUser.uid);
      const updateData = {
        ...updates,
        updated_at: new Date()
      };

      await updateDoc(userRef, updateData);

      this.currentUser = { ...this.currentUser, ...updateData };
      this.notifyListeners({ user: this.currentUser, loading: false, error: null });

      return this.currentUser;
    } catch (error: any) {
      console.error('Profile update error:', error);
      throw new Error(error.message || 'Profile update failed');
    }
  }

  public async getUserPermissions(): Promise<string[]> {
    if (!this.currentUser) {
      return [];
    }
    return this.currentUser.permissions || [];
  }

  public hasPermission(permission: string): boolean {
    if (!this.currentUser) {
      return false;
    }
    return this.currentUser.permissions?.includes(permission) || false;
  }

  public isAdmin(): boolean {
    return this.currentUser?.role === 'admin';
  }

  public isInvestor(): boolean {
    return this.currentUser?.role === 'investor';
  }

  public getCurrentUser(): UserProfile | null {
    return this.currentUser;
  }

  public async refreshToken(): Promise<string> {
    if (!auth) {
      throw new Error('Firebase authentication is not available');
    }

    if (!auth.currentUser) {
      throw new Error('No authenticated user');
    }

    const token = await auth.currentUser.getIdToken(true);
    localStorage.setItem('auth_token', token);
    return token;
  }
}

export const authService = new AuthService();
export default authService;