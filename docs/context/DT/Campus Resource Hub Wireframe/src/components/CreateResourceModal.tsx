import { X, Upload, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useState } from 'react';

interface CreateResourceModalProps {
  onClose: () => void;
  onCreate: (resource: any) => void;
}

export function CreateResourceModal({ onClose, onCreate }: CreateResourceModalProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    location: '',
    capacity: '',
    availability: 'available',
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.title) newErrors.title = 'Title is required';
    if (!formData.description) newErrors.description = 'Description is required';
    if (!formData.category) newErrors.category = 'Category is required';
    if (!formData.location) newErrors.location = 'Location is required';
    if (!formData.capacity) {
      newErrors.capacity = 'Capacity is required';
    } else if (parseInt(formData.capacity) < 1) {
      newErrors.capacity = 'Capacity must be at least 1';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onCreate(formData);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <Card className="w-full max-w-2xl relative my-8">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded-full transition-colors z-10"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="p-6">
          <h2 className="mb-2">Create New Resource</h2>
          <p className="text-gray-600 mb-6">
            Share your resource with the campus community
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title */}
            <div>
              <label className="block text-sm text-gray-600 mb-2">
                Resource Title <span className="text-red-500">*</span>
              </label>
              <Input
                type="text"
                placeholder="e.g., Study Room 301, HD Projector, Chemistry Lab"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className={errors.title ? 'border-red-500' : ''}
              />
              {errors.title && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle className="w-4 h-4" />
                  <span>{errors.title}</span>
                </div>
              )}
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm text-gray-600 mb-2">
                Description <span className="text-red-500">*</span>
              </label>
              <Textarea
                placeholder="Provide detailed information about the resource, its features, and any special requirements..."
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className={errors.description ? 'border-red-500' : ''}
              />
              {errors.description && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle className="w-4 h-4" />
                  <span>{errors.description}</span>
                </div>
              )}
            </div>

            {/* Category and Capacity */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-2">
                  Category <span className="text-red-500">*</span>
                </label>
                <Select
                  value={formData.category}
                  onValueChange={(value) => setFormData({ ...formData, category: value })}
                >
                  <SelectTrigger className={errors.category ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Study Rooms">Study Rooms</SelectItem>
                    <SelectItem value="Equipment">Equipment</SelectItem>
                    <SelectItem value="Labs">Labs</SelectItem>
                    <SelectItem value="Events">Events</SelectItem>
                    <SelectItem value="Tutoring">Tutoring</SelectItem>
                  </SelectContent>
                </Select>
                {errors.category && (
                  <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.category}</span>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-2">
                  Capacity <span className="text-red-500">*</span>
                </label>
                <Input
                  type="number"
                  min="1"
                  placeholder="e.g., 6"
                  value={formData.capacity}
                  onChange={(e) => setFormData({ ...formData, capacity: e.target.value })}
                  className={errors.capacity ? 'border-red-500' : ''}
                />
                {errors.capacity && (
                  <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.capacity}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm text-gray-600 mb-2">
                Location <span className="text-red-500">*</span>
              </label>
              <Input
                type="text"
                placeholder="e.g., Library Building, Floor 2, Room 201"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className={errors.location ? 'border-red-500' : ''}
              />
              {errors.location && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                  <AlertCircle className="w-4 h-4" />
                  <span>{errors.location}</span>
                </div>
              )}
            </div>

            {/* Image Upload */}
            <div>
              <label className="block text-sm text-gray-600 mb-2">Images</label>
              <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer">
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600 mb-1">
                  Click to upload or drag and drop
                </p>
                <p className="text-xs text-gray-500">
                  PNG, JPG up to 10MB (recommended: 1200x800px)
                </p>
              </div>
            </div>

            {/* Availability */}
            <div>
              <label className="block text-sm text-gray-600 mb-2">Availability</label>
              <Select
                value={formData.availability}
                onValueChange={(value) => setFormData({ ...formData, availability: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">Available Now</SelectItem>
                  <SelectItem value="unavailable">Temporarily Unavailable</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={onClose} className="flex-1">
                Cancel
              </Button>
              <Button type="submit" className="flex-1">
                Create Resource
              </Button>
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
}
