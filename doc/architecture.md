# Saskatoon Architecture

## Current Architecture

As any software, Saskatoon is situated in a historical context and has been through many hands. The current architecture reflects these conditions and is not ideal. This section only describes how Saskatoon is implemented right now and helps new developers navigate.

Saskatoon is based on the [Django](https://www.djangoproject.com/) web framework. It consists of 3 apps:
   - **harvest**: harvest related models and functionalities
     - harvest, harvest yield, property, tree type, participation request, equipment
     - auto email notification
   - **member**: personnel and permission related models and functionalities
     - pick-leader registration & onboarding
     - personnel and organization
     - login and password
     - permission and access control
   - **sitebase**: most frontend dashboard related stuff
     - all html templates and static files (e.g. font, css, images)
     - harvest calendar
     - terms & conditions, privacy policy, resources (e.g. volunteer waiver form pdf, equipment points pdf)

Multi-locale is handled via the **django-rosetta** package.