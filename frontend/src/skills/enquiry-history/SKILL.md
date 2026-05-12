---
name: enquiry-history
description: Use when rendering the sidebar list of past processed enquiries
---

# Enquiry History

## Overview
Sidebar component listing all previously processed enquiries from the backend. Clicking an item loads its result into the main view.

## Props
| Prop | Type | Description |
|------|------|-------------|
| `onSelect` | (result: EnquiryResponse) => void | Called when user clicks a history item |
