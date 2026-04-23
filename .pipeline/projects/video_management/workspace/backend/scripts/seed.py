"""Seed script to populate the database with sample video data."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Video, VideoStatus, TableMetadata, TableField, FieldTypeId

VIDEO_TITLES = [
    "How to Build a SaaS in 30 Days",
    "React vs Vue in 2024",
    "Docker for Beginners",
    "The Future of AI in Web Development",
    "10 Python Tips You Need to Know",
    "Building a Full-Stack App with FastAPI",
    "CSS Grid vs Flexbox — When to Use What",
    "Git Workflow for Teams",
    "TypeScript Best Practices",
    "Web Performance Optimization",
    "Introduction to Machine Learning",
    "Kubernetes Explained Simply",
    "REST API Design Patterns",
    "GraphQL vs REST — The Definitive Guide",
    "Microservices Architecture Deep Dive",
    "Serverless Computing with AWS Lambda",
    "Database Indexing Strategies",
    "Authentication with JWT and OAuth2",
    "CI/CD Pipeline Setup Guide",
    "Testing Strategies for Web Apps",
    "Responsive Design Masterclass",
    "Web Accessibility Essentials",
    "Progressive Web Apps Explained",
    "WebSockets Real-Time Communication",
    "Redis Caching Patterns",
    "PostgreSQL Advanced Queries",
    "MongoDB vs PostgreSQL",
    "Elasticsearch for Search",
    "Message Queues with RabbitMQ",
    "Event-Driven Architecture",
    "Domain-Driven Design Basics",
    "Clean Code Principles",
    "Design Patterns in Python",
    "SOLID Principles Explained",
    "Agile Development Methodology",
    "Scrum Master Guide",
    "Product Management for Developers",
    "Freelancing as a Developer",
    "Open Source Contribution Guide",
    "Tech Interview Preparation",
    "Building a Developer Portfolio",
    "GitHub Actions Tutorial",
    "Terraform Infrastructure as Code",
    "Ansible Automation Guide",
    "Nginx Configuration Tips",
    "HTTPS and SSL Certificates",
    "CDN Setup and Optimization",
    "Web Analytics with Google Tag Manager",
    "SEO for Developers",
    "Content Strategy for Tech Channels",
    "Video Editing Tips for Creators",
    "YouTube Algorithm Explained",
    "Monetizing Your Tech Channel",
    "Building a Personal Brand Online",
    "Networking for Developers",
    "Remote Work Productivity Tips",
    "Time Management for Engineers",
    "Learning to Code in 2024",
    "Bootcamp vs Self-Taught Developer",
    "CS Degree vs Coding Bootcamp",
    "Top Programming Languages to Learn",
    "Web Development Roadmap 2024",
    "Backend Developer Career Path",
    "Frontend Developer Career Path",
    "Full-Stack Developer Roadmap",
    "DevOps Engineer Career Path",
    "Data Engineer Career Path",
    "Cloud Engineer Career Path",
    "Security Engineer Career Path",
    "Mobile Development with Flutter",
    "iOS Development with Swift",
    "Android Development with Kotlin",
    "Cross-Platform Mobile Apps",
    "Game Development with Unity",
    "Blockchain Development Basics",
    "Web3 and Decentralized Apps",
    "Rust Programming Language",
    "Go Programming for Web Services",
    "Node.js Performance Tips",
    "Express.js Best Practices",
    "Next.js Full-Stack Framework",
    "Svelte — The Future of Web?",
    "Tailwind CSS Utility-First Design",
    "Material UI Component Library",
    "Ant Design Enterprise UI",
    "Chakra UI Accessible Components",
    "Radix UI Headless Components",
    "Framer Motion Animations",
    "Three.js 3D Web Graphics",
    "WebGL Shaders for Beginners",
    "Canvas API Drawing Tutorial",
    "WebRTC Video Conferencing",
    "Stripe Payment Integration",
    "Twilio SMS API Tutorial",
    "SendGrid Email API Guide",
    "Cloudinary Media Management",
    "Firebase Realtime Database",
    "Supabase Open Source Firebase",
    "Prisma ORM Tutorial",
    "Drizzle ORM vs Prisma",
    "SQLAlchemy Advanced Patterns",
    "Django REST Framework Guide",
    "FastAPI vs Django Performance",
    "Flask Microframework Tutorial",
    "FastAPI Background Tasks",
    "FastAPI Dependency Injection",
    "FastAPI Middleware Deep Dive",
    "FastAPI Testing Strategies",
    "FastAPI Deployment with Docker",
    "FastAPI on AWS Lambda",
    "FastAPI on Google Cloud Run",
    "FastAPI on Railway",
    "FastAPI on Render",
    "FastAPI on Fly.io",
    "FastAPI on DigitalOcean",
    "FastAPI on Vercel",
    "FastAPI on Heroku",
    "FastAPI on Netlify",
    "FastAPI on Cloudflare Workers",
]

DESCRIPTIONS = [
    "A comprehensive guide covering all the essentials you need to know.",
    "Learn the fundamentals and advanced techniques in this detailed tutorial.",
    "Step-by-step walkthrough with practical examples and best practices.",
    "Deep dive into the topic with real-world use cases and code samples.",
    "Everything you need to know about this technology, explained clearly.",
    "Practical tutorial with hands-on exercises and project-based learning.",
    "Expert tips and tricks to level up your skills in this area.",
    "Complete overview from basics to advanced concepts with examples.",
]

TAGS_POOL = [
    "python", "javascript", "react", "typescript", "docker", "kubernetes",
    "aws", "ai", "machine-learning", "web-dev", "backend", "frontend",
    "devops", "database", "api", "security", "performance", "css",
    "git", "testing", "career", "tutorial", "beginner", "advanced",
    "fastapi", "nodejs", "graphql", "rest", "microservices", "serverless",
    "mongodb", "postgresql", "redis", "nginx", "terraform", "ansible",
    "vue", "svelte", "flutter", "swift", "kotlin", "rust", "go",
]

STATUSES = [VideoStatus.DRAFT, VideoStatus.SCHEDULED, VideoStatus.PUBLISHED, VideoStatus.FAILED]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create default table
    table = db.query(TableMetadata).filter(TableMetadata.name == "Videos").first()
    if not table:
        table = TableMetadata(name="Videos", description="Default video library")
        db.add(table)
        db.commit()
        db.refresh(table)
    else:
        db.commit()

    # Check if already seeded
    count = db.query(Video).filter(Video.table_id == table.id).count()
    if count > 0:
        print(f"Database already has {count} videos. Skipping seed.")
        db.close()
        return

    # Create default fields
    default_field_names = {
        "title": FieldTypeId.TEXT,
        "description": FieldTypeId.TEXT,
        "status": FieldTypeId.SELECT,
        "tags": FieldTypeId.TAGS,
        "publish_date": FieldTypeId.DATE,
        "thumbnail_url": FieldTypeId.URL,
        "youtube_video_id": FieldTypeId.TEXT,
        "custom_fields": FieldTypeId.TEXT,
        "created_at": FieldTypeId.DATE,
        "updated_at": FieldTypeId.DATE,
    }
    for name, ftype in default_field_names.items():
        field = TableField(
            table_id=table.id,
            name=name,
            field_type=ftype,
            is_required=(name in ("title",)),
        )
        db.add(field)
    db.commit()

    # Create videos
    now = datetime.utcnow()
    videos = []
    for i, title in enumerate(VIDEO_TITLES):
        num_tags = 2 + (i % 4)
        video_tags = TAGS_POOL[i : i + num_tags]
        status = STATUSES[i % len(STATUSES)]
        pub_date = now + timedelta(days=(i % 30) - 15) if status in (VideoStatus.SCHEDULED, VideoStatus.DRAFT) else None

        video = Video(
            table_id=table.id,
            title=title,
            description=DESCRIPTIONS[i % len(DESCRIPTIONS)],
            status=status,
            tags=video_tags,
            publish_date=pub_date,
            thumbnail_url=f"https://example.com/thumbnails/video_{i}.jpg",
            youtube_video_id=f"vID_{i:04d}" if status == VideoStatus.PUBLISHED else None,
            custom_fields={
                "episode_number": i + 1,
                "estimated_duration": f"{10 + (i % 50)} min",
                "audience_level": ["beginner", "intermediate", "advanced"][i % 3],
            },
        )
        videos.append(video)

    db.add_all(videos)
    db.commit()
    print(f"Seeded {len(videos)} videos into the database.")
    db.close()


if __name__ == "__main__":
    seed()
