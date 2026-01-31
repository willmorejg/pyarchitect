<!--
 Copyright 2026 James G Willmore
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
     https://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->
# Python-based Architecture Management Application (PyArchitect)

## Overview

This application provides a structured, data‑driven way to model, visualize, and manage software architecture across complex enterprise systems.
It was designed for environments with multiple integrations, event‑driven workflows, cloud‑native components, and legacy system interactions.
The platform supports high‑level modeling (C4 architecture), detailed component definitions, and automated diagram generation.

The application exposes both a **Vue.js front‑end editor** and a **Python FastAPI back‑end** as part of a full architecture management solution.

---

## Key Features

### **1. Architecture as Data (JSON‑based Modeling)**

The core concept of the application is representing architecture as a set of structured entities:

- **Systems** – High‑level domains containing components.
- **Components** – Software, hardware, database, people, or process elements.
- **Properties** – Arbitrary key/value metadata for each component or system.
- **Interactions** – Connections between components or systems.

This flexible design supports everything from microservices to event‑driven workflows, legacy systems, and cloud components.

---

## C4 Model Support

The application is built around the industry‑proven **C4 Model**:

- **Level 1: System Context** – Shows systems, users, and high‑level relationships.
- **Level 2: Container Views** – Shows APIs, databases, queues, functions, services, and front‑end applications.
- **Level 3: Component Views** – Internal modules within services.
- **Level 4: Code (Optional)** – Used for selective deep‑dives.

Architecture definitions can be used to generate diagrams for documentation, design reviews, and communication with stakeholders.

---

## Application Architecture

### **Backend (Python / FastAPI)**

The backend provides:

- REST APIs for systems, components, and interactions
- Pydantic‑based data models for validation and schema consistency
- JSON persistence layer (file‑based or pluggable storage)
- Diagram generation (Mermaid / other rendering integrations)

### **Frontend (Vue.js / Nuxt)**

The frontend provides:

- A visual editor for systems and components
- Search and filtering tools
- Diagram previews
- Graph‑based editors for relationships
- JSON editor for direct architecture editing

---

## Core Data Models

### **System**

Represents a high‑level application or domain.

- uuid
- name
- properties
- component list

### **Component**

Represents an architectural primitive.

- uuid
- name
- type (software, hardware, database, people, process)
- properties

### **Interaction**

Represents communication between architectural elements.

- source component
- target component
- protocol
- description
- properties

---

## Example Use Cases

- Modeling event‑driven architectures involving queues, functions, and external providers
- Tracking legacy modernization from AS400 to cloud services
- Documenting integrations between policy, billing, payment, and agency systems
- Building internal reference documentation automatically
- Generating consistent diagrams for engineering and business audiences

---

## Project Structure (High-Level)

```
root/
  backend/
    models/          # Pydantic models (System, Component, Interaction)
    routes/          # FastAPI routes
    services/        # Business logic
    storage/         # JSON or database persistence
  frontend/
    components/      # Vue.js components
    pages/           # UI pages
    editors/         # Arch editors and JSON editors
  diagrams/
    templates/       # Mermaid templates
    generated/       # output diagrams
```

---

## Getting Started

### **Backend Setup**

```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### **Frontend Setup**

```
cd frontend
npm install
npm run dev
```

---

## Goals of the Application

- Centralize architecture knowledge
- Provide a living, versioned architecture model
- Enable dynamic diagram generation
- Support enterprise documentation workflows
- Reduce manual drawing and outdated PDF diagrams

---

## Roadmap

- Integration with GitHub for architecture versioning
- Export to Confluence / Markdown bundles
- CI-based architecture drift detection
- Diagram diffing (before/after)
- Importers for cloud resources (Azure, AWS)
- Graph-based querying (Cypher, Gremlin)

---

## License

This project is licensed under the MIT License unless otherwise specified.

---

## Contact

For questions or enhancements, contact the architecture owner or submit a request through the project repository.
