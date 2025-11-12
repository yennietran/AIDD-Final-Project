import { X, Mail, Lock, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { useState } from 'react';

interface SignInModalProps {
  onClose: () => void;
  onSignIn: (email: string, password: string) => void;
}

export function SignInModal({ onClose, onSignIn }: SignInModalProps) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (isSignUp) {
      if (!name) {
        newErrors.name = 'Name is required';
      }
      if (password !== confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSignIn(email, password);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded-full transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="p-6">
          <div className="text-center mb-6">
            <div className="w-12 h-12 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-white">CR</span>
            </div>
            <h2 className="mb-2">{isSignUp ? 'Create Account' : 'Welcome Back'}</h2>
            <p className="text-gray-600">
              {isSignUp
                ? 'Sign up to start booking campus resources'
                : 'Sign in to access your account'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignUp && (
              <div>
                <label className="block text-sm text-gray-600 mb-2">Full Name</label>
                <Input
                  type="text"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={errors.name ? 'border-red-500' : ''}
                />
                {errors.name && (
                  <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.name}</span>
                  </div>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm text-gray-600 mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  type="email"
                  placeholder="you@university.edu"
                  className={`pl-10 ${errors.email ? 'border-red-500' : ''}`}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              {errors.email && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle className="w-4 h-4" />
                  <span>{errors.email}</span>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  type="password"
                  placeholder="••••••••"
                  className={`pl-10 ${errors.password ? 'border-red-500' : ''}`}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              {errors.password && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle className="w-4 h-4" />
                  <span>{errors.password}</span>
                </div>
              )}
            </div>

            {isSignUp && (
              <div>
                <label className="block text-sm text-gray-600 mb-2">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    type="password"
                    placeholder="••••••••"
                    className={`pl-10 ${errors.confirmPassword ? 'border-red-500' : ''}`}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </div>
                {errors.confirmPassword && (
                  <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.confirmPassword}</span>
                  </div>
                )}
              </div>
            )}

            {!isSignUp && (
              <div className="flex justify-end">
                <button type="button" className="text-sm text-gray-600 hover:underline">
                  Forgot password?
                </button>
              </div>
            )}

            <Button type="submit" className="w-full" size="lg">
              {isSignUp ? 'Sign Up' : 'Sign In'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <span className="text-gray-600">
              {isSignUp ? 'Already have an account?' : "Don't have an account?"}
            </span>
            <button
              onClick={() => {
                setIsSignUp(!isSignUp);
                setErrors({});
              }}
              className="ml-2 text-gray-900 hover:underline"
            >
              {isSignUp ? 'Sign In' : 'Sign Up'}
            </button>
          </div>

          {isSignUp && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-xs text-blue-900">
                <strong>Note:</strong> Use your university email address to register. Your account
                will be verified before activation.
              </p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
