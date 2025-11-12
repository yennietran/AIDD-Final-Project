import { Search, SlidersHorizontal, Grid3x3, List, Star, MapPin, Users } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Resource } from '../types';
import { useState } from 'react';

interface ResourceListingPageProps {
  resources: Resource[];
  selectedCategory?: string;
  onNavigate: (page: string, resourceId?: string) => void;
}

export function ResourceListingPage({ resources, selectedCategory, onNavigate }: ResourceListingPageProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState(selectedCategory || 'all');
  const [sortBy, setSortBy] = useState('rating');

  const filteredResources = resources.filter((resource) => {
    const matchesSearch = resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = category === 'all' || resource.category === category;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="mb-2">Browse Resources</h1>
          <p className="text-gray-600">
            {filteredResources.length} resources available
          </p>
        </div>

        {/* Filter Bar */}
        <div className="bg-white rounded-lg border p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            {/* Search */}
            <div className="md:col-span-4 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search resources..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Category Filter */}
            <div className="md:col-span-3">
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="Study Rooms">Study Rooms</SelectItem>
                  <SelectItem value="Equipment">Equipment</SelectItem>
                  <SelectItem value="Labs">Labs</SelectItem>
                  <SelectItem value="Events">Events</SelectItem>
                  <SelectItem value="Tutoring">Tutoring</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Date Picker Placeholder */}
            <div className="md:col-span-2">
              <Input type="date" placeholder="Date" />
            </div>

            {/* Capacity Filter */}
            <div className="md:col-span-2">
              <Select defaultValue="any">
                <SelectTrigger>
                  <SelectValue placeholder="Capacity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="any">Any Capacity</SelectItem>
                  <SelectItem value="1-5">1-5 people</SelectItem>
                  <SelectItem value="6-20">6-20 people</SelectItem>
                  <SelectItem value="20+">20+ people</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Advanced Filters */}
            <div className="md:col-span-1">
              <Button variant="outline" className="w-full">
                <SlidersHorizontal className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Sort and View Controls */}
          <div className="flex justify-between items-center mt-4 pt-4 border-t">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Sort by:</span>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="rating">Top Rated</SelectItem>
                  <SelectItem value="recent">Most Recent</SelectItem>
                  <SelectItem value="availability">Availability</SelectItem>
                  <SelectItem value="capacity">Capacity</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex gap-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid3x3 className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Results */}
        {filteredResources.length === 0 ? (
          <div className="bg-white rounded-lg border p-16 text-center">
            <div className="max-w-md mx-auto">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="mb-2">No resources found</h3>
              <p className="text-gray-600">
                Try adjusting your filters or search terms
              </p>
            </div>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredResources.map((resource) => (
              <Card key={resource.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-video bg-gray-200 relative overflow-hidden">
                  <img
                    src={resource.images[0]}
                    alt={resource.title}
                    className="w-full h-full object-cover"
                  />
                  {resource.available ? (
                    <Badge className="absolute top-3 right-3 bg-green-500">Available</Badge>
                  ) : (
                    <Badge className="absolute top-3 right-3 bg-gray-500">Unavailable</Badge>
                  )}
                </div>
                <div className="p-4">
                  <Badge variant="outline" className="mb-2">
                    {resource.category}
                  </Badge>
                  <h3 className="mb-2 line-clamp-1">{resource.title}</h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {resource.description}
                  </p>
                  <div className="flex items-center gap-1 text-sm text-gray-600 mb-2">
                    <MapPin className="w-4 h-4" />
                    <span className="line-clamp-1">{resource.location}</span>
                  </div>
                  <div className="flex items-center gap-1 mb-2">
                    <Users className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600">Capacity: {resource.capacity}</span>
                  </div>
                  <div className="flex items-center gap-1 mb-4">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm">{resource.rating}</span>
                    <span className="text-sm text-gray-500">({resource.reviewCount} reviews)</span>
                  </div>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => onNavigate('detail', resource.id)}
                  >
                    View Details
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredResources.map((resource) => (
              <Card key={resource.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="flex flex-col sm:flex-row">
                  <div className="w-full sm:w-64 h-48 sm:h-auto bg-gray-200 relative overflow-hidden">
                    <img
                      src={resource.images[0]}
                      alt={resource.title}
                      className="w-full h-full object-cover"
                    />
                    {resource.available ? (
                      <Badge className="absolute top-3 right-3 bg-green-500">Available</Badge>
                    ) : (
                      <Badge className="absolute top-3 right-3 bg-gray-500">Unavailable</Badge>
                    )}
                  </div>
                  <div className="flex-1 p-6">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <Badge variant="outline" className="mb-2">
                          {resource.category}
                        </Badge>
                        <h3 className="mb-2">{resource.title}</h3>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => onNavigate('detail', resource.id)}
                      >
                        View Details
                      </Button>
                    </div>
                    <p className="text-gray-600 mb-4 line-clamp-2">
                      {resource.description}
                    </p>
                    <div className="flex flex-wrap gap-4">
                      <div className="flex items-center gap-1 text-sm text-gray-600">
                        <MapPin className="w-4 h-4" />
                        <span>{resource.location}</span>
                      </div>
                      <div className="flex items-center gap-1 text-sm text-gray-600">
                        <Users className="w-4 h-4" />
                        <span>Capacity: {resource.capacity}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        <span className="text-sm">{resource.rating}</span>
                        <span className="text-sm text-gray-500">({resource.reviewCount})</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
