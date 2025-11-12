export type UserRole = 'Student' | 'Staff' | 'Admin';

export type ResourceCategory = 'Study Rooms' | 'Equipment' | 'Labs' | 'Events' | 'Tutoring';

export type BookingStatus = 'Upcoming' | 'Completed' | 'Cancelled' | 'Pending';

export type ApprovalStatus = 'Pending' | 'Approved' | 'Rejected';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
}

export interface Resource {
  id: string;
  title: string;
  description: string;
  category: ResourceCategory;
  location: string;
  capacity: number;
  rating: number;
  reviewCount: number;
  images: string[];
  available: boolean;
  ownerId: string;
  ownerName: string;
}

export interface Booking {
  id: string;
  resourceId: string;
  resourceTitle: string;
  resourceImage: string;
  startTime: string;
  endTime: string;
  status: BookingStatus;
  notes?: string;
}

export interface Review {
  id: string;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  date: string;
}

export interface Message {
  id: string;
  senderId: string;
  senderName: string;
  subject: string;
  preview: string;
  date: string;
  read: boolean;
}

export interface ApprovalItem {
  id: string;
  type: 'Resource' | 'Booking';
  title: string;
  submittedBy: string;
  date: string;
  status: ApprovalStatus;
}
