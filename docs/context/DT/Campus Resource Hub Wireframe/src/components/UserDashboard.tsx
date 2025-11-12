import { LayoutDashboard, BookOpen, MessageSquare, User as UserIcon, Plus, Edit, Trash2, Clock, CheckCircle, XCircle, Mail } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Resource, Booking, Message, User } from '../types';
import { useState } from 'react';

interface UserDashboardProps {
  user: User;
  userResources: Resource[];
  userBookings: Booking[];
  messages: Message[];
  onCreateResource: () => void;
  onEditResource: (id: string) => void;
  onDeleteResource: (id: string) => void;
}

export function UserDashboard({
  user,
  userResources,
  userBookings,
  messages,
  onCreateResource,
  onEditResource,
  onDeleteResource,
}: UserDashboardProps) {
  const [activeTab, setActiveTab] = useState<'listings' | 'bookings' | 'messages' | 'profile'>('bookings');

  const tabs = [
    { id: 'bookings' as const, label: 'My Bookings', icon: BookOpen },
    { id: 'listings' as const, label: 'My Listings', icon: LayoutDashboard },
    { id: 'messages' as const, label: 'Messages', icon: MessageSquare },
    { id: 'profile' as const, label: 'Profile', icon: UserIcon },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Upcoming':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'Completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'Cancelled':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="mb-2">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user.name}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <Card className="p-4">
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                        activeTab === tab.id
                          ? 'bg-gray-900 text-white'
                          : 'hover:bg-gray-100 text-gray-700'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{tab.label}</span>
                      {tab.id === 'messages' && messages.filter(m => !m.read).length > 0 && (
                        <Badge className="ml-auto bg-red-500">
                          {messages.filter(m => !m.read).length}
                        </Badge>
                      )}
                    </button>
                  );
                })}
              </nav>

              <div className="mt-6 pt-6 border-t">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                    <UserIcon className="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <div className="text-sm">{user.name}</div>
                    <Badge variant="outline" className="text-xs">
                      {user.role}
                    </Badge>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* My Bookings */}
            {activeTab === 'bookings' && (
              <Card className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2>My Bookings</h2>
                </div>

                {userBookings.length === 0 ? (
                  <div className="text-center py-12">
                    <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="mb-2">No bookings yet</h3>
                    <p className="text-gray-600 mb-4">
                      Start by browsing available resources
                    </p>
                    <Button>Browse Resources</Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {userBookings.map((booking) => (
                      <Card key={booking.id} className="p-4">
                        <div className="flex flex-col sm:flex-row gap-4">
                          <div className="w-full sm:w-32 h-24 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                            <img
                              src={booking.resourceImage}
                              alt={booking.resourceTitle}
                              className="w-full h-full object-cover"
                            />
                          </div>
                          <div className="flex-1">
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <h3 className="mb-1">{booking.resourceTitle}</h3>
                                <div className="flex items-center gap-2">
                                  {getStatusIcon(booking.status)}
                                  <Badge variant={
                                    booking.status === 'Upcoming' ? 'default' :
                                    booking.status === 'Completed' ? 'outline' : 'destructive'
                                  }>
                                    {booking.status}
                                  </Badge>
                                </div>
                              </div>
                              <div className="flex gap-2">
                                {booking.status === 'Upcoming' && (
                                  <>
                                    <Button variant="outline" size="sm">Edit</Button>
                                    <Button variant="outline" size="sm">Cancel</Button>
                                  </>
                                )}
                              </div>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">
                              {booking.startTime} - {booking.endTime}
                            </p>
                            {booking.notes && (
                              <p className="text-sm text-gray-500">
                                Note: {booking.notes}
                              </p>
                            )}
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </Card>
            )}

            {/* My Listings */}
            {activeTab === 'listings' && (
              <Card className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2>My Listings</h2>
                  <Button onClick={onCreateResource}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Resource
                  </Button>
                </div>

                {userResources.length === 0 ? (
                  <div className="text-center py-12">
                    <LayoutDashboard className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="mb-2">No listings yet</h3>
                    <p className="text-gray-600 mb-4">
                      Share your resources with the campus community
                    </p>
                    <Button onClick={onCreateResource}>
                      <Plus className="w-4 h-4 mr-2" />
                      Create Your First Listing
                    </Button>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Resource</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead>Location</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Rating</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {userResources.map((resource) => (
                          <TableRow key={resource.id}>
                            <TableCell>
                              <div className="flex items-center gap-3">
                                <div className="w-12 h-12 bg-gray-200 rounded overflow-hidden flex-shrink-0">
                                  <img
                                    src={resource.images[0]}
                                    alt={resource.title}
                                    className="w-full h-full object-cover"
                                  />
                                </div>
                                <span>{resource.title}</span>
                              </div>
                            </TableCell>
                            <TableCell>{resource.category}</TableCell>
                            <TableCell className="text-sm text-gray-600">
                              {resource.location}
                            </TableCell>
                            <TableCell>
                              {resource.available ? (
                                <Badge className="bg-green-500">Available</Badge>
                              ) : (
                                <Badge className="bg-gray-500">Unavailable</Badge>
                              )}
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-1">
                                <span>{resource.rating}</span>
                                <span className="text-sm text-gray-500">
                                  ({resource.reviewCount})
                                </span>
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex gap-2 justify-end">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => onEditResource(resource.id)}
                                >
                                  <Edit className="w-4 h-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => onDeleteResource(resource.id)}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </Card>
            )}

            {/* Messages */}
            {activeTab === 'messages' && (
              <Card className="p-6">
                <h2 className="mb-6">Messages</h2>

                {messages.length === 0 ? (
                  <div className="text-center py-12">
                    <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="mb-2">No messages</h3>
                    <p className="text-gray-600">
                      Your inbox is empty
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {messages.map((message) => (
                      <Card
                        key={message.id}
                        className={`p-4 cursor-pointer hover:shadow-md transition-shadow ${
                          !message.read ? 'bg-blue-50' : ''
                        }`}
                      >
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                            <Mail className="w-5 h-5 text-gray-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex justify-between items-start mb-1">
                              <span className={!message.read ? '' : 'text-gray-600'}>
                                {message.senderName}
                              </span>
                              <span className="text-sm text-gray-500">{message.date}</span>
                            </div>
                            <div className={!message.read ? '' : 'text-gray-600'}>
                              {message.subject}
                            </div>
                            <p className="text-sm text-gray-500 line-clamp-1 mt-1">
                              {message.preview}
                            </p>
                          </div>
                          {!message.read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-2" />
                          )}
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </Card>
            )}

            {/* Profile */}
            {activeTab === 'profile' && (
              <Card className="p-6">
                <h2 className="mb-6">Profile Settings</h2>

                <div className="max-w-2xl">
                  <div className="flex items-center gap-4 mb-8">
                    <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center">
                      <UserIcon className="w-10 h-10 text-gray-600" />
                    </div>
                    <div>
                      <Button variant="outline" size="sm">Change Photo</Button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-2">Full Name</label>
                      <input
                        type="text"
                        defaultValue={user.name}
                        className="w-full px-3 py-2 border rounded-lg"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-gray-600 mb-2">Email</label>
                      <input
                        type="email"
                        defaultValue={user.email}
                        className="w-full px-3 py-2 border rounded-lg"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-gray-600 mb-2">Role</label>
                      <input
                        type="text"
                        value={user.role}
                        disabled
                        className="w-full px-3 py-2 border rounded-lg bg-gray-50 text-gray-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-gray-600 mb-2">Phone Number</label>
                      <input
                        type="tel"
                        placeholder="(555) 123-4567"
                        className="w-full px-3 py-2 border rounded-lg"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-gray-600 mb-2">Department</label>
                      <input
                        type="text"
                        placeholder="e.g., Computer Science"
                        className="w-full px-3 py-2 border rounded-lg"
                      />
                    </div>

                    <div className="pt-4">
                      <Button>Save Changes</Button>
                    </div>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
