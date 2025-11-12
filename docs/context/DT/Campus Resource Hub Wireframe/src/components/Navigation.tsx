import { Search, User, Menu, X } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useState } from 'react';

interface NavigationProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  onSignIn: () => void;
  userRole?: 'Student' | 'Staff' | 'Admin';
}

export function Navigation({ currentPage, onNavigate, onSignIn, userRole }: NavigationProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="border-b bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <button 
            onClick={() => onNavigate('home')}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <div className="w-8 h-8 bg-gray-800 rounded flex items-center justify-center">
              <span className="text-white">CR</span>
            </div>
            <span className="hidden sm:block">Campus Resource Hub</span>
          </button>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <button
              onClick={() => onNavigate('home')}
              className={currentPage === 'home' ? 'underline' : 'hover:underline'}
            >
              Home
            </button>
            <button
              onClick={() => onNavigate('resources')}
              className={currentPage === 'resources' ? 'underline' : 'hover:underline'}
            >
              Browse Resources
            </button>
            {userRole && (
              <button
                onClick={() => onNavigate('dashboard')}
                className={currentPage === 'dashboard' ? 'underline' : 'hover:underline'}
              >
                My Dashboard
              </button>
            )}
            {userRole === 'Admin' && (
              <button
                onClick={() => onNavigate('admin')}
                className={currentPage === 'admin' ? 'underline' : 'hover:underline'}
              >
                Admin
              </button>
            )}
          </div>

          {/* User Actions */}
          <div className="hidden md:flex items-center gap-3">
            {userRole ? (
              <Button variant="outline" size="sm">
                <User className="w-4 h-4 mr-2" />
                Profile
              </Button>
            ) : (
              <Button onClick={onSignIn} size="sm">
                Sign In
              </Button>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t">
            <div className="flex flex-col gap-3">
              <button
                onClick={() => {
                  onNavigate('home');
                  setMobileMenuOpen(false);
                }}
                className="text-left py-2 hover:bg-gray-50 px-2 rounded"
              >
                Home
              </button>
              <button
                onClick={() => {
                  onNavigate('resources');
                  setMobileMenuOpen(false);
                }}
                className="text-left py-2 hover:bg-gray-50 px-2 rounded"
              >
                Browse Resources
              </button>
              {userRole && (
                <button
                  onClick={() => {
                    onNavigate('dashboard');
                    setMobileMenuOpen(false);
                  }}
                  className="text-left py-2 hover:bg-gray-50 px-2 rounded"
                >
                  My Dashboard
                </button>
              )}
              {userRole === 'Admin' && (
                <button
                  onClick={() => {
                    onNavigate('admin');
                    setMobileMenuOpen(false);
                  }}
                  className="text-left py-2 hover:bg-gray-50 px-2 rounded"
                >
                  Admin
                </button>
              )}
              <div className="pt-2 border-t">
                {userRole ? (
                  <Button variant="outline" size="sm" className="w-full">
                    <User className="w-4 h-4 mr-2" />
                    Profile
                  </Button>
                ) : (
                  <Button onClick={onSignIn} size="sm" className="w-full">
                    Sign In
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
