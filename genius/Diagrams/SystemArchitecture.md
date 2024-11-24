# ENGINUS System Architecture Diagram

```mermaid
graph TB
    subgraph Client Layer
        UI[Web Interface]
        Mobile[Mobile Interface]
    end

    subgraph API Gateway
        Gateway[API Gateway]
        Auth[Authentication]
        LoadBalancer[Load Balancer]
    end

    subgraph Application Services
        UserService[User Service]
        DocService[Document Service]
        ReportService[Report Service]
        NotificationService[Notification Service]
    end

    subgraph Storage Layer
        CloudStorage[(Cloud Storage)]
        Database[(Main Database)]
        Cache[(Redis Cache)]
    end

    UI --> Gateway
    Mobile --> Gateway
    Gateway --> Auth
    Gateway --> LoadBalancer
    LoadBalancer --> UserService
    LoadBalancer --> DocService
    LoadBalancer --> ReportService
    LoadBalancer --> NotificationService
    
    UserService --> Database
    DocService --> CloudStorage
    DocService --> Database
    ReportService --> Database
    NotificationService --> Cache

    subgraph Monitoring
        Logging[Logging Service]
        Metrics[Metrics Collection]
    end

    Application Services --> Logging
    Application Services --> Metrics
