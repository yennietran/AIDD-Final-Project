import { Search, BookOpen, Laptop, FlaskConical, Calendar, GraduationCap, Star, MapPin, ChevronRight } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Resource } from '../types';
import { useState } from 'react';

interface HomePageProps {
  featuredResources: Resource[];
  onNavigate: (page: string, resourceId?: string) => void;
  onCategorySelect: (category: string) => void;
}

export function HomePage({ featuredResources, onNavigate, onCategorySelect }: HomePageProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    { name: 'Study Rooms', icon: BookOpen, color: 'bg-blue-50 hover:bg-blue-100' },
    { name: 'Equipment', icon: Laptop, color: 'bg-purple-50 hover:bg-purple-100' },
    { name: 'Labs', icon: FlaskConical, color: 'bg-green-50 hover:bg-green-100' },
    { name: 'Events', icon: Calendar, color: 'bg-orange-50 hover:bg-orange-100' },
    { name: 'Tutoring', icon: GraduationCap, color: 'bg-pink-50 hover:bg-pink-100' },
  ];

  const quickFilters = [
    { label: 'Available Today', active: true },
    { label: 'Top Rated', active: false },
    { label: 'Near Me', active: false },
  ];

  const handleSearch = () => {
    onNavigate('resources');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="mb-6">Discover Campus Resources</h1>
            <p className="text-gray-600 mb-8">
              Book study rooms, reserve equipment, access labs, and find tutoring — all in one place
            </p>
            
            {/* Search Box */}
            <div className="flex gap-2 max-w-2xl mx-auto">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                  placeholder="Search for study rooms, equipment, labs..."
                  className="pl-10 h-12"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
              <Button onClick={handleSearch} className="h-12 px-8">
                Search
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 className="mb-6">Browse by Category</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {categories.map((category) => {
            const Icon = category.icon;
            return (
              <button
                key={category.name}
                onClick={() => {
                  onCategorySelect(category.name);
                  onNavigate('resources');
                }}
                className={`${category.color} rounded-lg p-6 transition-colors text-center flex flex-col items-center gap-3`}
              >
                <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center">
                  <Icon className="w-6 h-6 text-gray-700" />
                </div>
                <span className="text-gray-800">{category.name}</span>
              </button>
            );
          })}
        </div>
      </section>

      {/* Quick Filters */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-wrap gap-3">
          <span className="text-gray-600">Quick filters:</span>
          {quickFilters.map((filter) => (
            <Badge
              key={filter.label}
              variant={filter.active ? 'default' : 'outline'}
              className="cursor-pointer hover:bg-gray-100"
            >
              {filter.label}
            </Badge>
          ))}
        </div>
      </section>

      {/* Featured Resources Carousel */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-6">
          <h2>Featured Resources</h2>
          <Button variant="ghost" onClick={() => onNavigate('resources')}>
            View All <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredResources.slice(0, 4).map((resource) => (
            <Card key={resource.id} className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
              <div className="aspect-video bg-gray-200 relative overflow-hidden">
                <img
                  src={resource.images[0]}
                  alt={resource.title}
                  className="w-full h-full object-cover"
                />
                {resource.available && (
                  <Badge className="absolute top-2 right-2 bg-green-500">Available</Badge>
                )}
              </div>
              <div className="p-4">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="line-clamp-1">{resource.title}</h3>
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-600 mb-2">
                  <MapPin className="w-4 h-4" />
                  <span className="line-clamp-1">{resource.location}</span>
                </div>
                <div className="flex items-center gap-1 mb-3">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm">{resource.rating}</span>
                  <span className="text-sm text-gray-500">({resource.reviewCount})</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => onNavigate('detail', resource.id)}
                >
                  View Details
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="mb-4">Have a resource to share?</h2>
            <p className="text-gray-600 mb-6">
              List your study space, equipment, or tutoring services to help other students
            </p>
            <Button size="lg" onClick={() => onNavigate('dashboard')}>
              Add Your Resource
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
