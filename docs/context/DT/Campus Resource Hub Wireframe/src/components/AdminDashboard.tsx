import { Shield, Users, LayoutDashboard, FileText, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { ApprovalItem, User } from '../types';
import { useState } from 'react';

interface AdminDashboardProps {
  approvals: ApprovalItem[];
  users: User[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export function AdminDashboard({ approvals, users, onApprove, onReject }: AdminDashboardProps) {
  const [activeTab, setActiveTab] = useState<'approvals' | 'users' | 'resources' | 'reports'>('approvals');

  const tabs = [
    { id: 'approvals' as const, label: 'Approvals Queue', icon: Shield },
    { id: 'users' as const, label: 'Users', icon: Users },
    { id: 'resources' as const, label: 'Resources', icon: LayoutDashboard },
    { id: 'reports' as const, label: 'Reports', icon: FileText },
  ];

  const pendingApprovals = approvals.filter(a => a.status === 'Pending');

  // Mock analytics data
  const analytics = [
    { label: 'Total Users', value: '2,847', change: '+12%', icon: Users, color: 'bg-blue-50' },
    { label: 'Total Resources', value: '456', change: '+8%', icon: LayoutDashboard, color: 'bg-green-50' },
    { label: 'Total Bookings', value: '1,293', change: '+23%', icon: FileText, color: 'bg-purple-50' },
    { label: 'Pending Approvals', value: pendingApprovals.length.toString(), change: '-5%', icon: Shield, color: 'bg-orange-50' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Manage platform resources and users</p>
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
                      {tab.id === 'approvals' && pendingApprovals.length > 0 && (
                        <Badge className="ml-auto bg-red-500">
                          {pendingApprovals.length}
                        </Badge>
                      )}
                    </button>
                  );
                })}
              </nav>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Reports / Analytics */}
            {activeTab === 'reports' && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                  {analytics.map((stat) => {
                    const Icon = stat.icon;
                    return (
                      <Card key={stat.label} className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center`}>
                            <Icon className="w-6 h-6 text-gray-700" />
                          </div>
                          <span className={`text-sm ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                            {stat.change}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 mb-1">{stat.label}</div>
                        <div className="text-2xl">{stat.value}</div>
                      </Card>
                    );
                  })}
                </div>

                <Card className="p-6 mb-6">
                  <h2 className="mb-4">Usage Overview</h2>
                  <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500">Chart placeholder</p>
                      <p className="text-sm text-gray-400">Analytics visualization</p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6">
                  <h2 className="mb-4">Top Resources</h2>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Resource Name</TableHead>
                        <TableHead>Category</TableHead>
                        <TableHead>Bookings</TableHead>
                        <TableHead>Rating</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow>
                        <TableCell>Main Library Study Room A</TableCell>
                        <TableCell>Study Rooms</TableCell>
                        <TableCell>156</TableCell>
                        <TableCell>4.8</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Chemistry Research Lab 301</TableCell>
                        <TableCell>Labs</TableCell>
                        <TableCell>124</TableCell>
                        <TableCell>4.9</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>HD Projector & Screen Set</TableCell>
                        <TableCell>Equipment</TableCell>
                        <TableCell>98</TableCell>
                        <TableCell>4.6</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </Card>
              </>
            )}

            {/* Approvals Queue */}
            {activeTab === 'approvals' && (
              <Card className="p-6">
                <h2 className="mb-6">Approvals Queue</h2>

                {pendingApprovals.length === 0 ? (
                  <div className="text-center py-12">
                    <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="mb-2">All caught up!</h3>
                    <p className="text-gray-600">
                      No pending approvals at the moment
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Type</TableHead>
                          <TableHead>Title</TableHead>
                          <TableHead>Submitted By</TableHead>
                          <TableHead>Date</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {approvals.map((approval) => (
                          <TableRow key={approval.id}>
                            <TableCell>
                              <Badge variant="outline">{approval.type}</Badge>
                            </TableCell>
                            <TableCell>{approval.title}</TableCell>
                            <TableCell>{approval.submittedBy}</TableCell>
                            <TableCell className="text-sm text-gray-600">{approval.date}</TableCell>
                            <TableCell>
                              <Badge
                                variant={
                                  approval.status === 'Approved' ? 'default' :
                                  approval.status === 'Rejected' ? 'destructive' : 'outline'
                                }
                              >
                                {approval.status}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-right">
                              {approval.status === 'Pending' ? (
                                <div className="flex gap-2 justify-end">
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => onApprove(approval.id)}
                                  >
                                    <CheckCircle className="w-4 h-4 mr-1 text-green-600" />
                                    Approve
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => onReject(approval.id)}
                                  >
                                    <XCircle className="w-4 h-4 mr-1 text-red-600" />
                                    Reject
                                  </Button>
                                </div>
                              ) : (
                                <span className="text-sm text-gray-500">No actions</span>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </Card>
            )}

            {/* Users Management */}
            {activeTab === 'users' && (
              <Card className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2>Users Management</h2>
                  <Button size="sm">Add User</Button>
                </div>

                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Role</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {users.map((user) => (
                        <TableRow key={user.id}>
                          <TableCell>
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                                <Users className="w-4 h-4 text-gray-600" />
                              </div>
                              {user.name}
                            </div>
                          </TableCell>
                          <TableCell className="text-gray-600">{user.email}</TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                user.role === 'Admin' ? 'default' :
                                user.role === 'Staff' ? 'outline' : 'secondary'
                              }
                            >
                              {user.role}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex gap-2 justify-end">
                              <Button size="sm" variant="outline">Edit</Button>
                              <Button size="sm" variant="outline">Suspend</Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </Card>
            )}

            {/* Resources Management */}
            {activeTab === 'resources' && (
              <Card className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2>Resources Management</h2>
                  <Button size="sm">Add Resource</Button>
                </div>

                <div className="text-center py-12">
                  <LayoutDashboard className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="mb-2">Resource Management</h3>
                  <p className="text-gray-600">
                    Manage all campus resources from this panel
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
