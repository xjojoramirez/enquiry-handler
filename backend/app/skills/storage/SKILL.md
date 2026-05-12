---
name: storage
description: Use when persisting or retrieving enquiry records from PostgreSQL
---

# Storage

## Overview
Manages the asyncpg connection pool, runs table migrations, and provides CRUD operations for `EnquiryResponse` records.

## When to Use
- Saving a new enquiry after classification
- Listing all processed enquiries
- Fetching a single enquiry by ID
- Exporting all enquiries

## Quick Reference

| Function | Description |
|----------|-------------|
| `get_pool()` | Get or create asyncpg connection pool |
| `close_pool()` | Close the connection pool on shutdown |
| `run_migrations(pool)` | Create enquiries table and indexes |
| `EnquiryStore.save(enquiry)` | Insert record |
| `EnquiryStore.get(id)` | Fetch by UUID |
| `EnquiryStore.list_all()` | Fetch all, newest first |

## Dependencies
- PostgreSQL 16
- `app.config.settings` — DATABASE_URL
