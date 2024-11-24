# ENGINUS Database Schema Diagram

```mermaid
erDiagram
    Users ||--o{ Projects : manages
    Users {
        int user_id PK
        string username
        string email
        string password_hash
        string role
        datetime created_at
        datetime last_login
    }

    Projects ||--o{ Documents : contains
    Projects {
        int project_id PK
        string name
        string description
        datetime created_at
        datetime updated_at
        string status
    }

    Documents ||--o{ Versions : has
    Documents {
        int document_id PK
        int project_id FK
        string name
        string type
        string path
        datetime created_at
        string status
    }

    Versions {
        int version_id PK
        int document_id FK
        string version_number
        string path
        datetime created_at
        int created_by FK
    }

    ProjectUsers ||--o{ Projects : accesses
    ProjectUsers {
        int project_id FK
        int user_id FK
        string role
        datetime assigned_at
    }

    Reports {
        int report_id PK
        int project_id FK
        string type
        string parameters
        datetime generated_at
        int generated_by FK
    }

    ActivityLogs {
        int log_id PK
        int user_id FK
        int project_id FK
        string action_type
        string details
        datetime timestamp
    }

    Notifications {
        int notification_id PK
        int user_id FK
        string type
        string message
        datetime created_at
        boolean read_status
    }
```

## Database Schema Description

### Core Tables

1. Users
   - Stores user account information
   - Manages authentication data
   - Tracks user activity

2. Projects
   - Contains project metadata
   - Manages project lifecycle
   - Links to related documents

3. Documents
   - Stores document information
   - Manages file metadata
   - Links to physical files

### Relationship Tables

1. ProjectUsers
   - Maps users to projects
   - Manages project roles
   - Controls access levels

2. Versions
   - Tracks document versions
   - Maintains version history
   - Links to document files

### Tracking Tables

1. Reports
   - Stores report configurations
   - Tracks report generation
   - Manages report parameters

2. ActivityLogs
   - Records user actions
   - Maintains audit trail
   - Tracks system events

3. Notifications
   - Manages user notifications
   - Tracks notification status
   - Handles message delivery

### Key Relationships

1. User-Project Relationship
   - Many-to-many through ProjectUsers
   - Role-based access control
   - Project membership tracking

2. Project-Document Relationship
   - One-to-many relationship
   - Document organization
   - Project content management

3. Document-Version Relationship
   - One-to-many relationship
   - Version control
   - Change tracking
