# ENGINUS User Flow Diagram

```mermaid
graph TD
    Start((Start)) --> Login[Login]
    Login --> Auth{Authenticated?}
    Auth -->|No| Login
    Auth -->|Yes| Dashboard[Dashboard]
    
    Dashboard --> Projects[Project List]
    Dashboard --> Reports[Reports]
    Dashboard --> Documents[Documents]
    
    Projects --> SelectProject[Select Project]
    SelectProject --> ProjectDashboard[Project Dashboard]
    
    ProjectDashboard --> ViewDocs[View Documents]
    ProjectDashboard --> UploadDoc[Upload Document]
    ProjectDashboard --> GenerateReport[Generate Report]
    
    ViewDocs --> DocActions{Document Actions}
    DocActions -->|Download| Download[Download Document]
    DocActions -->|Update| Update[Update Document]
    DocActions -->|Delete| Delete[Delete Document]
    
    UploadDoc --> Validation{Validate}
    Validation -->|Success| Store[Store Document]
    Validation -->|Fail| ShowError[Show Error]
    
    GenerateReport --> SelectType[Select Report Type]
    SelectType --> CustomizeReport[Customize Report]
    CustomizeReport --> GenerateOutput[Generate Output]
    
    Store --> UpdateLog[Update Log]
    UpdateLog --> Notify[Notify Stakeholders]
```

## User Flow Description

### Authentication Flow
1. User starts at login page
2. Enters credentials
3. If authentication fails, returns to login
4. If successful, proceeds to dashboard

### Project Management Flow
1. View list of accessible projects
2. Select specific project
3. Access project dashboard
4. View project documents and reports

### Document Management Flow
1. View document list
2. Upload new documents
3. Perform actions on existing documents
   - Download
   - Update
   - Delete
4. System logs actions
5. Stakeholders receive notifications

### Report Generation Flow
1. Select report type
2. Customize report parameters
3. Generate and view report
4. Export or share as needed
