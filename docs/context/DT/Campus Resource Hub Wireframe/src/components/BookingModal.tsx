import { X, Calendar, Clock, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Textarea } from './ui/textarea';
import { useState } from 'react';

interface BookingModalProps {
  resourceTitle: string;
  onClose: () => void;
  onBook: (booking: any) => void;
}

export function BookingModal({ resourceTitle, onClose, onBook }: BookingModalProps) {
  const [formData, setFormData] = useState({
    startDate: '',
    startTime: '',
    endDate: '',
    endTime: '',
    notes: '',
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.startDate) newErrors.startDate = 'Start date is required';
    if (!formData.startTime) newErrors.startTime = 'Start time is required';
    if (!formData.endDate) newErrors.endDate = 'End date is required';
    if (!formData.endTime) newErrors.endTime = 'End time is required';

    // Check if end is after start
    if (formData.startDate && formData.endDate && formData.startTime && formData.endTime) {
      const start = new Date(`${formData.startDate}T${formData.startTime}`);
      const end = new Date(`${formData.endDate}T${formData.endTime}`);
      
      if (end <= start) {
        newErrors.endTime = 'End time must be after start time';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onBook({
        startTime: `${formData.startDate} ${formData.startTime}`,
        endTime: `${formData.endDate} ${formData.endTime}`,
        notes: formData.notes,
      });
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-lg relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded-full transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="p-6">
          <h2 className="mb-2">Book Resource</h2>
          <p className="text-gray-600 mb-6">{resourceTitle}</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Start Date and Time */}
            <div>
              <label className="block text-sm text-gray-600 mb-3">
                Start Date & Time <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                    <Input
                      type="date"
                      className={`pl-10 ${errors.startDate ? 'border-red-500' : ''}`}
                      value={formData.startDate}
                      onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                    />
                  </div>
                  {errors.startDate && (
                    <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                      <AlertCircle className="w-4 h-4" />
                      <span>{errors.startDate}</span>
                    </div>
                  )}
                </div>
                <div>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                    <Input
                      type="time"
                      className={`pl-10 ${errors.startTime ? 'border-red-500' : ''}`}
                      value={formData.startTime}
                      onChange={(e) => setFormData({ ...formData, startTime: e.target.value })}
                    />
                  </div>
                  {errors.startTime && (
                    <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                      <AlertCircle className="w-4 h-4" />
                      <span>{errors.startTime}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* End Date and Time */}
            <div>
              <label className="block text-sm text-gray-600 mb-3">
                End Date & Time <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                    <Input
                      type="date"
                      className={`pl-10 ${errors.endDate ? 'border-red-500' : ''}`}
                      value={formData.endDate}
                      onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                    />
                  </div>
                  {errors.endDate && (
                    <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                      <AlertCircle className="w-4 h-4" />
                      <span>{errors.endDate}</span>
                    </div>
                  )}
                </div>
                <div>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                    <Input
                      type="time"
                      className={`pl-10 ${errors.endTime ? 'border-red-500' : ''}`}
                      value={formData.endTime}
                      onChange={(e) => setFormData({ ...formData, endTime: e.target.value })}
                    />
                  </div>
                  {errors.endTime && (
                    <div className="flex items-center gap-1 mt-1 text-sm text-red-600">
                      <AlertCircle className="w-4 h-4" />
                      <span>{errors.endTime}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm text-gray-600 mb-2">
                Notes (Optional)
              </label>
              <Textarea
                placeholder="Add any special requirements or notes for this booking..."
                rows={3}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              />
            </div>

            {/* Info Box */}
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-900">
                <strong>Please note:</strong> Your booking request will be reviewed by the resource
                owner. You'll receive a confirmation email once approved.
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={onClose} className="flex-1">
                Cancel
              </Button>
              <Button type="submit" className="flex-1">
                Submit Booking
              </Button>
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
}
