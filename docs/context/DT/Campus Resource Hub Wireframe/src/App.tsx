import { useState } from 'react';
import { Navigation } from './components/Navigation';
import { HomePage } from './components/HomePage';
import { ResourceListingPage } from './components/ResourceListingPage';
import { ResourceDetailPage } from './components/ResourceDetailPage';
import { UserDashboard } from './components/UserDashboard';
import { AdminDashboard } from './components/AdminDashboard';
import { SignInModal } from './components/SignInModal';
import { CreateResourceModal } from './components/CreateResourceModal';
import { BookingModal } from './components/BookingModal';
import { mockResources, mockBookings, mockReviews, mockMessages, mockApprovals, mockUsers, currentUser } from './data/mockData';
import { UserRole } from './types';

type Page = 'home' | 'resources' | 'detail' | 'dashboard' | 'admin';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [selectedResourceId, setSelectedResourceId] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [showSignInModal, setShowSignInModal] = useState(false);
  const [showCreateResourceModal, setShowCreateResourceModal] = useState(false);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [userRole, setUserRole] = useState<UserRole | undefined>(undefined);

  // Simulate user being logged in for demo purposes - remove this line to start logged out
  // setUserRole('Student'); // Uncomment to auto-login

  const handleNavigate = (page: string, resourceId?: string) => {
    setCurrentPage(page as Page);
    if (resourceId) {
      setSelectedResourceId(resourceId);
    }
    window.scrollTo(0, 0);
  };

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
  };

  const handleSignIn = (email: string, password: string) => {
    // Mock sign in - in real app, this would authenticate
    console.log('Sign in:', email, password);
    setUserRole('Student');
    setShowSignInModal(false);
  };

  const handleCreateResource = (resourceData: any) => {
    console.log('Creating resource:', resourceData);
    // In a real app, this would save to backend
  };

  const handleBookResource = (bookingData: any) => {
    console.log('Booking resource:', bookingData);
    // In a real app, this would save to backend
  };

  const handleApprove = (id: string) => {
    console.log('Approving:', id);
    // In a real app, this would update backend
  };

  const handleReject = (id: string) => {
    console.log('Rejecting:', id);
    // In a real app, this would update backend
  };

  const handleEditResource = (id: string) => {
    console.log('Editing resource:', id);
    // In a real app, this would open edit modal
  };

  const handleDeleteResource = (id: string) => {
    console.log('Deleting resource:', id);
    // In a real app, this would delete from backend
  };

  const selectedResource = selectedResourceId
    ? mockResources.find((r) => r.id === selectedResourceId)
    : null;

  // Filter user's own resources (mock)
  const userResources = mockResources.filter((r) => r.ownerId === 'current');

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation
        currentPage={currentPage}
        onNavigate={handleNavigate}
        onSignIn={() => setShowSignInModal(true)}
        userRole={userRole}
      />

      {currentPage === 'home' && (
        <HomePage
          featuredResources={mockResources}
          onNavigate={handleNavigate}
          onCategorySelect={handleCategorySelect}
        />
      )}

      {currentPage === 'resources' && (
        <ResourceListingPage
          resources={mockResources}
          selectedCategory={selectedCategory}
          onNavigate={handleNavigate}
        />
      )}

      {currentPage === 'detail' && selectedResource && (
        <ResourceDetailPage
          resource={selectedResource}
          reviews={mockReviews}
          onNavigate={handleNavigate}
          onBook={() => setShowBookingModal(true)}
        />
      )}

      {currentPage === 'dashboard' && userRole && (
        <UserDashboard
          user={{ ...currentUser, role: userRole }}
          userResources={userResources}
          userBookings={mockBookings}
          messages={mockMessages}
          onCreateResource={() => setShowCreateResourceModal(true)}
          onEditResource={handleEditResource}
          onDeleteResource={handleDeleteResource}
        />
      )}

      {currentPage === 'admin' && userRole === 'Admin' && (
        <AdminDashboard
          approvals={mockApprovals}
          users={mockUsers}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}

      {/* Modals */}
      {showSignInModal && (
        <SignInModal
          onClose={() => setShowSignInModal(false)}
          onSignIn={handleSignIn}
        />
      )}

      {showCreateResourceModal && (
        <CreateResourceModal
          onClose={() => setShowCreateResourceModal(false)}
          onCreate={handleCreateResource}
        />
      )}

      {showBookingModal && selectedResource && (
        <BookingModal
          resourceTitle={selectedResource.title}
          onClose={() => setShowBookingModal(false)}
          onBook={handleBookResource}
        />
      )}
    </div>
  );
}
