import { MapPin, Users, Star, ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Resource, Review } from '../types';
import { useState } from 'react';

interface ResourceDetailPageProps {
  resource: Resource;
  reviews: Review[];
  onNavigate: (page: string) => void;
  onBook: () => void;
}

export function ResourceDetailPage({ resource, reviews, onNavigate, onBook }: ResourceDetailPageProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % resource.images.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + resource.images.length) % resource.images.length);
  };

  // Mock calendar data
  const availabilityDays = [
    { date: '12', available: true },
    { date: '13', available: true },
    { date: '14', available: false },
    { date: '15', available: true },
    { date: '16', available: true },
    { date: '17', available: false },
    { date: '18', available: true },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => onNavigate('resources')}
          className="mb-6"
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Back to Resources
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Images and Details */}
          <div className="lg:col-span-2">
            {/* Image Carousel */}
            <div className="bg-white rounded-lg overflow-hidden mb-6">
              <div className="aspect-video bg-gray-200 relative">
                <img
                  src={resource.images[currentImageIndex]}
                  alt={resource.title}
                  className="w-full h-full object-cover"
                />
                {resource.images.length > 1 && (
                  <>
                    <button
                      onClick={prevImage}
                      className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 rounded-full flex items-center justify-center hover:bg-white transition-colors"
                    >
                      <ChevronLeft className="w-5 h-5" />
                    </button>
                    <button
                      onClick={nextImage}
                      className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 rounded-full flex items-center justify-center hover:bg-white transition-colors"
                    >
                      <ChevronRight className="w-5 h-5" />
                    </button>
                    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                      {resource.images.map((_, index) => (
                        <button
                          key={index}
                          onClick={() => setCurrentImageIndex(index)}
                          className={`w-2 h-2 rounded-full transition-colors ${
                            index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                          }`}
                        />
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Resource Details */}
            <Card className="p-6 mb-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <Badge variant="outline" className="mb-2">
                    {resource.category}
                  </Badge>
                  <h1 className="mb-2">{resource.title}</h1>
                  <div className="flex items-center gap-1 mb-3">
                    <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                    <span className="mr-2">{resource.rating}</span>
                    <span className="text-gray-500">({resource.reviewCount} reviews)</span>
                  </div>
                </div>
                {resource.available ? (
                  <Badge className="bg-green-500">Available</Badge>
                ) : (
                  <Badge className="bg-gray-500">Unavailable</Badge>
                )}
              </div>

              <div className="space-y-3 mb-6 pb-6 border-b">
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin className="w-5 h-5" />
                  <span>{resource.location}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Users className="w-5 h-5" />
                  <span>Capacity: {resource.capacity} {resource.capacity === 1 ? 'person' : 'people'}</span>
                </div>
              </div>

              <div>
                <h3 className="mb-3">Description</h3>
                <p className="text-gray-600 leading-relaxed">
                  {resource.description}
                </p>
              </div>

              <div className="mt-6 pt-6 border-t">
                <h3 className="mb-2">Managed by</h3>
                <p className="text-gray-600">{resource.ownerName}</p>
              </div>
            </Card>

            {/* Location Map Placeholder */}
            <Card className="p-6 mb-6">
              <h3 className="mb-4">Location</h3>
              <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">Map placeholder</p>
                  <p className="text-sm text-gray-400">{resource.location}</p>
                </div>
              </div>
            </Card>

            {/* Reviews Section */}
            <Card className="p-6">
              <h2 className="mb-6">Reviews ({reviews.length})</h2>
              
              {reviews.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No reviews yet. Be the first to review!
                </div>
              ) : (
                <div className="space-y-6">
                  {reviews.map((review) => (
                    <div key={review.id} className="pb-6 border-b last:border-0 last:pb-0">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <div className="mb-1">{review.userName}</div>
                          <div className="flex items-center gap-1">
                            {Array.from({ length: 5 }).map((_, i) => (
                              <Star
                                key={i}
                                className={`w-4 h-4 ${
                                  i < review.rating
                                    ? 'fill-yellow-400 text-yellow-400'
                                    : 'text-gray-300'
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                        <span className="text-sm text-gray-500">{review.date}</span>
                      </div>
                      <p className="text-gray-600">{review.comment}</p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* Right Column - Booking Card */}
          <div className="lg:col-span-1">
            <Card className="p-6 sticky top-24">
              <h3 className="mb-4">Book this resource</h3>
              
              {/* Availability Calendar */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <Calendar className="w-5 h-5 text-gray-600" />
                  <span>November 2025</span>
                </div>
                <div className="grid grid-cols-7 gap-2 mb-4">
                  {availabilityDays.map((day, index) => (
                    <button
                      key={index}
                      className={`aspect-square rounded-lg flex items-center justify-center text-sm transition-colors ${
                        day.available
                          ? 'bg-green-50 hover:bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      }`}
                      disabled={!day.available}
                    >
                      {day.date}
                    </button>
                  ))}
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-50 border border-green-200 rounded" />
                    <span className="text-gray-600">Available</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-gray-100 border border-gray-200 rounded" />
                    <span className="text-gray-600">Booked</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="text-sm text-gray-600 mb-2 block">Start Time</label>
                  <input
                    type="datetime-local"
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-600 mb-2 block">End Time</label>
                  <input
                    type="datetime-local"
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
              </div>

              <Button
                className="w-full"
                size="lg"
                onClick={onBook}
                disabled={!resource.available}
              >
                {resource.available ? 'Book Now' : 'Not Available'}
              </Button>

              <p className="text-xs text-gray-500 text-center mt-4">
                You'll receive a confirmation email after booking
              </p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
