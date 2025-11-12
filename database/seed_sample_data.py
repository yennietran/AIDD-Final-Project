"""
Seed sample data for Campus Resource Hub
Creates sample users and resources for testing and demonstration
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from src.models.models import db
from src.data_access.user_dal import UserDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.review_dal import ReviewDAL
from src.data_access.booking_dal import BookingDAL
from datetime import datetime, timedelta


def seed_data():
    """Seed the database with sample data"""
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Seeding sample data...")
        
        # Create sample users
        print("Creating sample users...")
        
        # Admin user
        admin = UserDAL.get_by_email("admin@campus.edu")
        if not admin:
            admin = UserDAL.create(
                name="Admin User",
                email="admin@campus.edu",
                password="admin123",
                role="admin",
                department="Administration"
            )
            print(f"Created admin user: {admin.email}")
        else:
            print(f"Admin user already exists: {admin.email}")
        
        # Staff users
        staff1 = UserDAL.get_by_email("library.staff@campus.edu")
        if not staff1:
            staff1 = UserDAL.create(
                name="Library Staff",
                email="library.staff@campus.edu",
                password="staff123",
                role="staff",
                department="Library Services"
            )
            print(f"Created staff user: {staff1.email}")
        
        staff2 = UserDAL.get_by_email("av.staff@campus.edu")
        if not staff2:
            staff2 = UserDAL.create(
                name="AV Equipment Manager",
                email="av.staff@campus.edu",
                password="staff123",
                role="staff",
                department="IT Services"
            )
            print(f"Created staff user: {staff2.email}")
        
        staff3 = UserDAL.get_by_email("science.staff@campus.edu")
        if not staff3:
            staff3 = UserDAL.create(
                name="Science Lab Coordinator",
                email="science.staff@campus.edu",
                password="staff123",
                role="staff",
                department="Science Department"
            )
            print(f"Created staff user: {staff3.email}")
        
        staff4 = UserDAL.get_by_email("events.staff@campus.edu")
        if not staff4:
            staff4 = UserDAL.create(
                name="Events Coordinator",
                email="events.staff@campus.edu",
                password="staff123",
                role="staff",
                department="Student Affairs"
            )
            print(f"Created staff user: {staff4.email}")
        
        staff5 = UserDAL.get_by_email("tutoring.staff@campus.edu")
        if not staff5:
            staff5 = UserDAL.create(
                name="Tutoring Center Director",
                email="tutoring.staff@campus.edu",
                password="staff123",
                role="staff",
                department="Academic Support"
            )
            print(f"Created staff user: {staff5.email}")
        
        # Student users (for reviews)
        student1 = UserDAL.get_by_email("student1@campus.edu")
        if not student1:
            student1 = UserDAL.create(
                name="Alex Johnson",
                email="student1@campus.edu",
                password="student123",
                role="student",
                department="Computer Science"
            )
        
        student2 = UserDAL.get_by_email("student2@campus.edu")
        if not student2:
            student2 = UserDAL.create(
                name="Sarah Chen",
                email="student2@campus.edu",
                password="student123",
                role="student",
                department="Biology"
            )
        
        student3 = UserDAL.get_by_email("student3@campus.edu")
        if not student3:
            student3 = UserDAL.create(
                name="Michael Brown",
                email="student3@campus.edu",
                password="student123",
                role="student",
                department="Business"
            )
        
        # Sample resources
        print("\nCreating sample resources...")
        
        resources_data = [
            # Study Rooms
            {
                "owner_id": staff1.user_id,
                "title": "Main Library Study Room A",
                "description": "Spacious study room with large windows, whiteboard, and comfortable seating. Perfect for group study sessions. Includes power outlets and WiFi.",
                "category": "Study Rooms",
                "location": "Library Building, Floor 2",
                "capacity": 6,
                "images": ["https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=800"],
                "availability_rules": {
                    "monday": "8:00-22:00",
                    "tuesday": "8:00-22:00",
                    "wednesday": "8:00-22:00",
                    "thursday": "8:00-22:00",
                    "friday": "8:00-20:00",
                    "saturday": "10:00-18:00",
                    "sunday": "10:00-18:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff1.user_id,
                "title": "Quiet Study Room B",
                "description": "Smaller, quiet study room ideal for individual study. Soundproofed walls and ergonomic furniture.",
                "category": "Study Rooms",
                "location": "Library Building, Floor 2",
                "capacity": 2,
                "images": ["https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800"],
                "availability_rules": {
                    "monday": "8:00-22:00",
                    "tuesday": "8:00-22:00",
                    "wednesday": "8:00-22:00",
                    "thursday": "8:00-22:00",
                    "friday": "8:00-20:00",
                    "saturday": "10:00-18:00",
                    "sunday": "10:00-18:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff1.user_id,
                "title": "Group Study Room C",
                "description": "Large study room with conference table, projector, and whiteboard. Perfect for team projects and presentations.",
                "category": "Study Rooms",
                "location": "Library Building, Floor 3",
                "capacity": 8,
                "images": ["https://images.unsplash.com/photo-1497366216548-37526070297c?w=800"],
                "availability_rules": {
                    "monday": "8:00-22:00",
                    "tuesday": "8:00-22:00",
                    "wednesday": "8:00-22:00",
                    "thursday": "8:00-22:00",
                    "friday": "8:00-20:00",
                    "saturday": "10:00-18:00",
                    "sunday": "10:00-18:00"
                },
                "status": "published"
            },
            
            # Equipment
            {
                "owner_id": staff2.user_id,
                "title": "HD Projector & Screen Set",
                "description": "High-definition projector with 120-inch screen. Includes HDMI cables, remote control, and carrying case. Perfect for presentations and events.",
                "category": "Equipment",
                "location": "AV Equipment Center",
                "capacity": None,
                "images": ["https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=800"],
                "availability_rules": {
                    "monday": "9:00-17:00",
                    "tuesday": "9:00-17:00",
                    "wednesday": "9:00-17:00",
                    "thursday": "9:00-17:00",
                    "friday": "9:00-17:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff2.user_id,
                "title": "Laptop & Charger Set",
                "description": "High-performance laptops available for checkout. Includes charger and carrying case. Pre-installed with essential software.",
                "category": "Equipment",
                "location": "IT Services, Room 101",
                "capacity": None,
                "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800"],
                "availability_rules": {
                    "monday": "8:00-18:00",
                    "tuesday": "8:00-18:00",
                    "wednesday": "8:00-18:00",
                    "thursday": "8:00-18:00",
                    "friday": "8:00-18:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff2.user_id,
                "title": "Camera & Tripod Kit",
                "description": "Professional DSLR camera with tripod, extra batteries, and memory cards. Ideal for photography projects and events.",
                "category": "Equipment",
                "location": "AV Equipment Center",
                "capacity": None,
                "images": ["https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=800"],
                "availability_rules": {
                    "monday": "9:00-17:00",
                    "tuesday": "9:00-17:00",
                    "wednesday": "9:00-17:00",
                    "thursday": "9:00-17:00",
                    "friday": "9:00-17:00"
                },
                "status": "published"
            },
            
            # Labs
            {
                "owner_id": staff3.user_id,
                "title": "Chemistry Research Lab 301",
                "description": "Fully equipped chemistry research laboratory with fume hoods, analytical instruments, and safety equipment. Requires safety certification.",
                "category": "Labs",
                "location": "Science Building, Floor 3",
                "capacity": 12,
                "images": ["https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=800"],
                "availability_rules": {
                    "monday": "9:00-17:00",
                    "tuesday": "9:00-17:00",
                    "wednesday": "9:00-17:00",
                    "thursday": "9:00-17:00",
                    "friday": "9:00-17:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff3.user_id,
                "title": "Biology Lab 205",
                "description": "Modern biology laboratory with microscopes, incubators, and specimen storage. Perfect for research and coursework.",
                "category": "Labs",
                "location": "Science Building, Floor 2",
                "capacity": 20,
                "images": ["https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=800"],
                "availability_rules": {
                    "monday": "8:00-18:00",
                    "tuesday": "8:00-18:00",
                    "wednesday": "8:00-18:00",
                    "thursday": "8:00-18:00",
                    "friday": "8:00-18:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff3.user_id,
                "title": "Computer Lab 101",
                "description": "Computer lab with 30 workstations, high-speed internet, and specialized software. Open for general use and classes.",
                "category": "Labs",
                "location": "Technology Building, Floor 1",
                "capacity": 30,
                "images": ["https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800"],
                "availability_rules": {
                    "monday": "7:00-22:00",
                    "tuesday": "7:00-22:00",
                    "wednesday": "7:00-22:00",
                    "thursday": "7:00-22:00",
                    "friday": "7:00-20:00",
                    "saturday": "9:00-17:00",
                    "sunday": "9:00-17:00"
                },
                "status": "published"
            },
            
            # Events
            {
                "owner_id": staff4.user_id,
                "title": "Grand Conference Hall",
                "description": "Spacious conference hall with state-of-the-art AV equipment, stage, and seating for up to 200 people. Perfect for large events, presentations, and ceremonies.",
                "category": "Events",
                "location": "Student Union Building",
                "capacity": 200,
                "images": ["https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800"],
                "availability_rules": {
                    "monday": "8:00-22:00",
                    "tuesday": "8:00-22:00",
                    "wednesday": "8:00-22:00",
                    "thursday": "8:00-22:00",
                    "friday": "8:00-22:00",
                    "saturday": "9:00-22:00",
                    "sunday": "9:00-22:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff4.user_id,
                "title": "Small Meeting Room",
                "description": "Intimate meeting room for small groups. Includes whiteboard, projector, and video conferencing equipment.",
                "category": "Events",
                "location": "Student Union Building, Room 201",
                "capacity": 15,
                "images": ["https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800"],
                "availability_rules": {
                    "monday": "8:00-20:00",
                    "tuesday": "8:00-20:00",
                    "wednesday": "8:00-20:00",
                    "thursday": "8:00-20:00",
                    "friday": "8:00-20:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff4.user_id,
                "title": "Outdoor Event Space",
                "description": "Beautiful outdoor courtyard perfect for events, gatherings, and activities. Includes covered areas and power outlets.",
                "category": "Events",
                "location": "Main Quad",
                "capacity": 100,
                "images": ["https://images.unsplash.com/photo-1511578314322-379afb476865?w=800"],
                "availability_rules": {
                    "monday": "7:00-20:00",
                    "tuesday": "7:00-20:00",
                    "wednesday": "7:00-20:00",
                    "thursday": "7:00-20:00",
                    "friday": "7:00-20:00",
                    "saturday": "8:00-20:00",
                    "sunday": "8:00-20:00"
                },
                "status": "published"
            },
            
            # Tutoring
            {
                "owner_id": staff5.user_id,
                "title": "Math Tutoring Session",
                "description": "One-on-one or small group math tutoring. Covers algebra, calculus, statistics, and more. Flexible scheduling available.",
                "category": "Tutoring",
                "location": "Academic Support Center, Room 105",
                "capacity": 4,
                "images": ["https://images.unsplash.com/photo-1509228468518-180dd4864904?w=800"],
                "availability_rules": {
                    "monday": "10:00-18:00",
                    "tuesday": "10:00-18:00",
                    "wednesday": "10:00-18:00",
                    "thursday": "10:00-18:00",
                    "friday": "10:00-16:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff5.user_id,
                "title": "Writing Center Consultation",
                "description": "Get help with essays, research papers, and writing assignments. Experienced tutors available for all writing levels.",
                "category": "Tutoring",
                "location": "Academic Support Center, Room 106",
                "capacity": 2,
                "images": ["https://images.unsplash.com/photo-1455390582262-044cdead277a?w=800"],
                "availability_rules": {
                    "monday": "9:00-17:00",
                    "tuesday": "9:00-17:00",
                    "wednesday": "9:00-17:00",
                    "thursday": "9:00-17:00",
                    "friday": "9:00-15:00"
                },
                "status": "published"
            },
            {
                "owner_id": staff5.user_id,
                "title": "Science Study Group",
                "description": "Group tutoring sessions for chemistry, biology, and physics. Collaborative learning environment with peer support.",
                "category": "Tutoring",
                "location": "Academic Support Center, Room 107",
                "capacity": 8,
                "images": ["https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800"],
                "availability_rules": {
                    "monday": "14:00-18:00",
                    "tuesday": "14:00-18:00",
                    "wednesday": "14:00-18:00",
                    "thursday": "14:00-18:00"
                },
                "status": "published"
            }
        ]
        
        created_resources = []
        for resource_data in resources_data:
            # Check if resource already exists
            existing = ResourceDAL.get_all(owner_id=resource_data["owner_id"], limit=100)
            exists = any(r.title == resource_data["title"] for r in existing)
            
            if not exists:
                resource = ResourceDAL.create(**resource_data)
                created_resources.append(resource)
                print(f"  Created: {resource.title}")
            else:
                print(f"  Already exists: {resource_data['title']}")
        
        # Create sample reviews for some resources
        print("\nCreating sample reviews...")
        
        if created_resources:
            # Reviews for Main Library Study Room A
            room_a = next((r for r in created_resources if "Main Library Study Room A" in r.title), None)
            if room_a:
                try:
                    ReviewDAL.create(room_a.resource_id, student1.user_id, 5, "Excellent study space! Very quiet and well-maintained.")
                    ReviewDAL.create(room_a.resource_id, student2.user_id, 5, "Perfect for group projects. The whiteboard is great!")
                    ReviewDAL.create(room_a.resource_id, student3.user_id, 4, "Good space, but can get crowded during exam season.")
                    print(f"  Added reviews for {room_a.title}")
                except:
                    pass
            
            # Reviews for HD Projector
            projector = next((r for r in created_resources if "HD Projector" in r.title), None)
            if projector:
                try:
                    ReviewDAL.create(projector.resource_id, student1.user_id, 5, "Great quality projector, easy to set up.")
                    ReviewDAL.create(projector.resource_id, student2.user_id, 4, "Works well, but the screen could be larger.")
                    ReviewDAL.create(projector.resource_id, student3.user_id, 5, "Perfect for presentations!")
                    print(f"  Added reviews for {projector.title}")
                except:
                    pass
            
            # Reviews for Chemistry Lab
            chem_lab = next((r for r in created_resources if "Chemistry Research Lab" in r.title), None)
            if chem_lab:
                try:
                    ReviewDAL.create(chem_lab.resource_id, student2.user_id, 5, "Well-equipped lab with all necessary equipment.")
                    ReviewDAL.create(chem_lab.resource_id, student3.user_id, 5, "Excellent facilities for research work.")
                    print(f"  Added reviews for {chem_lab.title}")
                except:
                    pass
            
            # Reviews for Conference Hall
            conference = next((r for r in created_resources if "Grand Conference Hall" in r.title), None)
            if conference:
                try:
                    ReviewDAL.create(conference.resource_id, student1.user_id, 5, "Amazing venue for large events!")
                    ReviewDAL.create(conference.resource_id, student2.user_id, 4, "Great space, good AV setup.")
                    ReviewDAL.create(conference.resource_id, student3.user_id, 5, "Perfect for our graduation ceremony.")
                    print(f"  Added reviews for {conference.title}")
                except:
                    pass
        
        print("\n[SUCCESS] Sample data seeding completed!")
        print(f"\nCreated {len(created_resources)} new resources")
        print("\nSample login credentials:")
        print("  Admin: admin@campus.edu / admin123")
        print("  Staff: library.staff@campus.edu / staff123")
        print("  Student: student1@campus.edu / student123")


if __name__ == "__main__":
    seed_data()
