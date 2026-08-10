"""Application layer — Use Cases (business orchestration).

Each Use Case is a class with a single ``execute()`` async method.
This layer:
  - Contains ALL business logic
  - Depends ONLY on domain protocols (never on infrastructure concretions)
  - Has ZERO FastAPI / HTTP imports
  - Is fully unit-testable with mock repositories
"""
