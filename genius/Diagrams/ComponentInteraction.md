# ENGINUS Component Interaction Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant AG as API Gateway
    participant AS as Auth Service
    participant DS as Doc Service
    participant CS as Cloud Storage
    participant DB as Database
    participant NS as Notification Service

    U->>FE: Login Request
    FE->>AG: Forward Auth Request
    AG->>AS: Validate Credentials
    AS->>DB: Check User Data
    DB-->>AS: User Data
    AS-->>FE: Auth Token

    U->>FE: Upload Document
    FE->>AG: Send Document
    AG->>DS: Process Document
    DS->>CS: Store Document
    DS->>DB: Store Metadata
    DS->>NS: Trigger Notification
    NS-->>U: Send Notification

    U->>FE: Generate Report
    FE->>AG: Report Request
    AG->>DS: Fetch Data
    DS->>DB: Query Data
    DS->>CS: Get Documents
    DS-->>FE: Report Data
    FE-->>U: Display Report
```

## Component Interaction Description

### Authentication Flow
1. User initiates login
2. Frontend forwards request through API Gateway
3. Auth Service validates credentials
4. Database confirms user data
5. Auth token returned to user

### Document Upload Flow
1. User uploads document
2. Request routed through API Gateway
3. Document Service processes upload
4. Document stored in Cloud Storage
5. Metadata saved to Database
6. Notification Service alerts relevant users

### Report Generation Flow
1. User requests report
2. API Gateway routes request
3. Document Service aggregates data
4. Data fetched from Database and Cloud Storage
5. Report generated and displayed to user

### Key Components

1. Frontend (FE)
   - User interface
   - Initial request handling
   - Response rendering

2. API Gateway (AG)
   - Request routing
   - Load balancing
   - Rate limiting

3. Auth Service (AS)
   - Credential validation
   - Token management
   - Session handling

4. Document Service (DS)
   - File processing
   - Version control
   - Metadata management

5. Cloud Storage (CS)
   - File storage
   - Data redundancy
   - Backup management

6. Database (DB)
   - Data persistence
   - Query handling
   - Transaction management

7. Notification Service (NS)
   - Event handling
   - Message queuing
   - Notification delivery
