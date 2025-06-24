![alt text](readme-header.png)

# MedMinder

Medminder is a gamified medical reminder app with timezone specificty and a calendar view 📆


## Table of Contents

[Overview](#-project-overview)

[Design](#medminder-design-overview)
  - [The 5 Planes](#-strategy-plane)
    - [Strategy Plane](#-strategy-plane)
    - [Scope Plane](#-scope-plane)
    - [Structure Plane](#-structure-plane)

[User Stories](#medminder-application-user-stories)
  - [Persona 1: The Busy Professional (Elena, 34)](#persona-1-the-busy-professional-elena-34)
  - [Persona 2: The Sandwich Carer (David, 52)](#persona-2-the-sandwich-carer-david-52)
  - [Persona 3: The Newly Diagnosed Teen (Leo, 16)](#persona-3-the-newly-diagnosed-teen-leo-16)
  - [Universal User Stories](#universal-user-stories-applicable-to-all-personas)


# MedMinder: A Gamified Medication Management Platform

## 🚀 Project Overview

MedMinder is a modern, gamified medication management platform built with Django. It empowers users to take control of their health by providing smart reminders, adherence tracking, and a beautiful calendar view—all tailored to each user’s timezone and schedule.

---

## ✨ Key Features

* **Smart Medication Reminders:** Set up complex schedules (daily, weekly, monthly, or custom), receive reminders via email or SMS, and never miss a dose.
* **Gamified Adherence:** Earn points, streaks, badges, and ranks for consistent medication adherence, making health management engaging and rewarding.
* **Premium Calendar View:** Visualize upcoming and past doses, plan ahead, and see your progress at a glance (premium users only).
* **Family & Accountability (Coming Soon):** Invite family or caregivers to view your progress and provide encouragement.
* **Personalized Analytics:** Get insights and statistics to understand your adherence patterns and improve your routines.
* **Timezone Awareness:** All reminders and logs are timezone-aware, ensuring accuracy for users anywhere in the world.
* **Secure & Scalable:** Built on Django with robust authentication and secure data handling.

---

## 🛠️ Technical Highlights

* **Django Backend:** Modular app structure (`accounts`, `reminders`, `payments`, `core`, etc.) for clean separation of concerns.
* **Stripe Integration:** Handles premium subscriptions and paywall logic for advanced features.
* **Custom Cron Jobs:** Automated background tasks for sending reminders, updating stats, and more.
* **Responsive UI:** Modern, mobile-friendly templates using Tailwind CSS and Alpine.js.
* **Extensible:** Easily add new features, integrations, or notification channels.


---

# MedMinder Design Overview

## Design Philosophy

MedMinder’s design is grounded in user needs and business goals:

- **Strategy**: Understanding users and aligning with business objectives.
- **Scope**: Delivering clear features and content.
- **Structure**: Organizing for intuitive use.
- **Skeleton**: Presenting with clarity and ease.
- **Surface**: Wrapping it all in a modern, engaging interface.

## 🧠 User-Centric Design Principles

At MedMinder, design isn't just about looks—it's about crafting seamless, intuitive experiences that empower users to take control of their health. Our philosophy focuses on:

- Understanding user needs  
- Simplifying complex tasks  
- Making medication management engaging and rewarding

## 🌟 Key Design Principles

- **Empathy-Driven**  
  We start with a deep understanding of our users' challenges and motivations, ensuring every feature addresses real needs.

- **Simplicity & Clarity**  
  A clean, uncluttered interface makes navigation easy and intuitive.

- **Engagement & Motivation**  
  Gamification transforms medication adherence from a chore into a rewarding experience.

- **Accessibility & Inclusivity**  
  Designed for users of all ages and abilities.

- **Feedback & Iteration**  
  Continuous user feedback drives our iterative design process.

## 🎨 Visual Design & Branding

MedMinder's visual design reflects clarity, trust, and engagement:

- **Color Palette**  
  Light, calming tones with vibrant accents for interactivity.

- **Typography**  
  Clear, legible fonts for readability and accessibility.

- **Iconography**  
  Intuitive icons that guide users through the app.

- **Responsive Design**  
  Mobile-first and fully responsive for all device sizes.

## 🧭 User Experience (UX) Flow

Our UX flow is designed to be intuitive and engaging across all user journeys:

- **Onboarding**  
  Guided setup to add medications and set reminders easily.

- **Daily Use**  
  Timely reminders, quick logging, and a visual dashboard for adherence tracking.

- **Gamification**  
  Points, badges, and streaks encourage consistency with visual progress feedback.

- **Settings & Customization**  
  Easy management of profiles, notifications, and subscriptions.

---

By focusing on these core design principles and user experiences, **MedMinder** delivers a medication management app that’s not only functional but also enjoyable—ultimately improving health outcomes for our users.

---

# The five planes of design

## 🧭 Strategy Plane

Defining the foundation of MedMinder’s purpose and direction.

### 🎯 User Needs & Business Objectives

The Strategy Plane forms the bedrock of MedMinder—aligning every decision with a clear understanding of our users' needs and our core business objectives. This ensures we are building the right product for the right people, creating a sustainable and impactful business.

---

### 1.1 🧩 User Needs: The "Why"

**Core Problem:**  
Non-adherence to medication is a critical and widespread health issue. The consequences include:

- Decreased quality of life  
- Preventable hospitalizations  
- Emotional and financial strain on users and their families  

Contributing factors: forgetfulness, complex multi-dose schedules, lack of motivation, and poor understanding of treatments.

#### 📌 Primary User Needs

- **Reliability & Simplicity**  
  A dependable, intuitive system that reduces complexity.

- **Motivation & Engagement**  
  Encouragement through positive reinforcement makes habits stick.

- **Information & Insight**  
  Clear, actionable data empowers users and caregivers.

- **Support & Connection**  
  Shared progress and community enhance emotional support.

- **Discretion & Trust**  
  Confidence in privacy and data security is non-negotiable.

---

### 👤 User Personas

#### Persona 1: *"The Busy Professional"* – Elena, 34  
- **Scenario**: Manages a demanding job while taking daily medication for a chronic condition.  
- **Needs**: Discrete, efficient reminders; strong privacy.  
- **Pain Points**: Misses doses due to schedule; finds logging tedious.  
- **MedMinder’s Role**: Persistent reminders and one-tap logging.

---

#### Persona 2: *"The Sandwich Carer"* – David, 52  
- **Scenario**: Cares for his elderly mother with complex medication needs.  
- **Needs**: Centralized dashboard, refill alerts, report sharing.  
- **Pain Points**: Struggles with medication schedules; no adherence visibility.  
- **MedMinder’s Role**: Caregiver accounts, refill alerts, and shareable reports.

---

#### Persona 3: *"The Newly Diagnosed Teen"* – Leo, 16  
- **Scenario**: Adjusting to life with Type 1 Diabetes.  
- **Needs**: Gamification, educational guidance.  
- **Pain Points**: Resistant to routine; finds it disruptive.  
- **MedMinder’s Role**: Engaging experience with achievements and learning support.

---

### 1.2 💼 Business Objectives: The "How"

#### 🧾 Value Proposition

For individuals and caregivers managing medications, **MedMinder** is an **engaging and reliable adherence partner**. Unlike basic alarm apps, we offer:

- Intelligent reminders  
- Motivational feedback  
- Insightful analytics  

Our goal: **Empower users**, improve **health outcomes**, and offer **peace of mind**.

#### 💸 Business Model

MedMinder uses a **freemium subscription model**, balancing accessibility with premium feature monetization.

---

#### 🆓 Free Tier

- Core medication reminders  
- Basic adherence tracking  
- Limited medication history

#### 💎 Premium Tier (Monthly/Annual)

- Advanced analytics & downloadable reports (PDFs)  
- Calendar integration (Google, iCal)  
- Caregiver accounts  
- Refill reminders  
- Advanced gamification & customization  
- Pill ID and drug interaction data

---

This strategic foundation allows MedMinder to serve diverse users with empathy, clarity, and business sustainability.


## 📐 Scope Plane

Defining the functional and content requirements that drive development.

---

### 🧱 Requirements & Structure

The Scope Plane translates our **strategic goals** into a concrete set of **functional** and **content** requirements. It serves as a detailed blueprint guiding MedMinder’s development process.

---

### 2.1 ⚙️ Functional Requirements

Features and interactions defined as **epics**, each with user stories and acceptance criteria.

---

#### 🧑‍💼 Epic 1: User Account & Profile Management  
**Description**: Provides users with a secure and personalized space to manage their information and preferences.

**User Stories**:
- Registration: *"As a new user, I want to sign up easily using my email and a password."*
- Authentication: *"As a returning user, I want to log in securely and have a 'Forgot Password' option."*
- Profile Management: *"As a user, I want to edit my profile information."*

**Acceptance Criteria**:
- Passwords hashed using Argon2 or equivalent
- Email verification required
- Secure session handling
- GDPR compliance

---

#### 💊 Epic 2: Core Medication & Scheduling  
**Description**: Enables users to input medication details and define complex reminder schedules.

**User Stories**:
- Add Medication: *"As a user, I want to add a new medication and specify its dosage."*
- Set Schedule: *"As a user, I want to create various schedule types."*
- Multiple Timings: *"As a user, I want to set multiple reminder times per day."*
- Log Doses: *"As a user, I want to mark a dose as 'Taken' or 'Skipped'."*

**Acceptance Criteria**:
- Support for flexible schedule types
- Time zone localization
- Relational schema for medication-schedule-log

---

#### 🔔 Epic 3: Smart Reminders & Notifications  
**Description**: Sends timely and reliable reminders through various channels.

**User Stories**:
- Push Notifications: *"As a user, I want to receive reminders on time."*
- Snooze Functionality: *"As a user, I want to snooze reminders briefly."*
- Escalation: *"As a user, I want backup notifications if I miss one."*

**Acceptance Criteria**:
- Reliable push delivery
- Celery with Redis for scheduling
- SMS integration via Twilio

---

#### 🏅 Epic 4: Gamification & Engagement  
**Description**: Motivates users with feedback loops and achievements.

**User Stories**:
- Streaks: *"See a 'streak' counter for perfect adherence."*
- Points & Levels: *"Earn points for taking medication on time."*
- Badges: *"Unlock badges for milestones."*

**Acceptance Criteria**:
- Server-side logic for rewards
- Real-time updates
- Custom badge assets

---

#### 💎 Epic 5: Premium Features & Subscription Management  
**Description**: Adds premium functionality for paying users.

**User Stories**:
- Subscription: *"Easily upgrade from within the app."*
- Payment: *"Securely enter payment information."*
- Calendar View: *"See full medication history on a calendar."*
- Management: *"View billing history and cancel anytime."*

**Acceptance Criteria**:
- Full Stripe integration
- Secure key handling and webhooks
- Feature access based on subscription

---

#### 🧑‍🤝‍🧑 Epic 6: Caregiver & Family View *(Planned for v2.0)*  
**Description**: Enables caregivers to monitor user adherence with permission.

**User Stories**:
- Invitation: *"Invite family via email to view adherence data."*
- Caregiver Dashboard: *"Simple view of schedule and history."*
- Missed Dose Alerts: *"Get notified of missed critical doses."*

**Acceptance Criteria**:
- Revocable invitation-based access
- Read-only caregiver roles
- Explicit consent with data privacy compliance

---

### 2.2 🧾 Content Requirements

Defines the types of information to be created and maintained to support a smooth, informative user experience.

---

#### 📘 Onboarding & User Guides
- **Content**: Multi-step tutorial, FAQs
- **Format**: In-app modals and Help section

#### 📊 Adherence Statistics & Visualizations
- **Content**: Charts and logs
- **Format**: Graphs and tables in dashboard

#### 💊 Medication Information *(v1.5 Feature)*
- **Content**: Basic drug data (e.g., side effects)
- **Format**: Pulled from third-party API

#### 📜 Legal & Support Documentation
- **Content**: Privacy policy, terms, support contacts
- **Format**: Static content in Settings and on website

#### 🏆 Gamification Content
- **Content**: Badge names, descriptions, triggers
- **Format**: Text strings and image assets

---

This comprehensive scope ensures that MedMinder delivers **functionality** aligned with **user needs**, **technical feasibility**, and **business objectives**.


## 🧱 Structure Plane

**Information Architecture and Interaction Design of the MedMinder App**

The Structure Plane defines the app’s backbone—how content is organized and how users interact with it. This phase focuses on a logical **Information Architecture (IA)** and intentional **Interaction Design (IxD)** to ensure seamless, goal-driven user experiences.

---

### 3.1 🗺️ Information Architecture (IA)

The IA outlines how MedMinder's content and features are structured. The goal: minimize cognitive load, maximize discoverability, and ensure a consistent, intuitive experience.

#### 🧭 App Sitemap & Hierarchy

The app uses a **primary tab bar navigation**, with logical secondary views branching from each section.

<pre>
/ (Root)
├── Login / Registration Flow (Unauthenticated Users)
├── Onboarding Flow (First-time Users)
├── 1.0 Dashboard (Primary Tab)
│ ├── 1.1 Today's Schedule View
│ ├── 1.2 Adherence Snapshot
│ └── 1.3 Quick Actions
├── 2.0 Reminders (Primary Tab)
│ ├── 2.1 Medication List
│ ├── 2.2 Medication Detail View
│ └── 2.3 Add/Edit Medication Flow
├── 3.0 Calendar (Premium - Primary Tab)
│ ├── 3.1 Monthly View
│ └── 3.2 Daily Detail View
├── 4.0 Analytics (Future Enhancement)
│ ├── 4.1 Adherence Reports
│ ├── 4.2 Streak & Gamification History
│ └── 4.3 Export Functionality
└── 5.0 Settings (Accessed via Account Tab)
├── 5.1 Profile Management
├── 5.2 Notification Preferences
├── 5.3 Subscription Management
├── 5.4 Documentation/Help Center
├── 5.5 Legal
└── 5.6 Logout
</pre>


---

### 3.2 🧩 Interaction Design (IxD)

**Interaction Design** governs how users engage with features, emphasizing clarity, feedback, and frictionless workflows.

---

#### 🔄 Key User Flows

##### ➕ Flow: Adding a New Medication
- **Trigger**: Tap "Add Medication"
- **Step 1**: Enter medication name
- **Step 2**: Choose schedule type and timing (e.g., "Every Day", "Specific Days", "Interval")
- **Step 3**: Set dosage
- **Step 4**: Confirm details
- **Feedback**: Confirmation toast/snackbar (“‘Aspirin’ has been added”), visible update in Reminders list

---

##### ⏰ Flow: Logging a Dose from a Notification
- **Trigger**: Push notification received
- **Action**: Tap "Take Now" directly from notification
- **Feedback**: 
  - Server records dose in background  
  - App icon badge updates  
  - Dashboard immediately reflects status  
- **Principle**: Task completion possible without opening the app

---

##### 💳 Flow: Upgrading to Premium
- **Trigger**: User taps "Upgrade" or accesses a locked feature
- **Step 1**: View paywall screen with benefits and pricing
- **Step 2**: Tap "Upgrade Now" → Stripe Checkout (in-app or web view)
- **Step 3**: See success modal ("Welcome to Premium!")
- **Feedback**: 
  - Features instantly unlocked  
  - "Upgrade" CTAs disappear  

---

#### 🎯 Core Interaction Patterns & Principles

##### ✨ Feedback & Microinteractions
- **State Changes**: Button hover/pressed animations
- **Confirmation Dialogs**: Shown for destructive actions (e.g., delete)
- **Loading Indicators**: Spinners for async operations *(future enhancement)*

##### 🏅 Gamification
- **Streak Counter**: Animated on dashboard
- **Badge Unlocks**: Subtle overlays for achievements; easy to dismiss

##### 🧠 Reducing Cognitive Load
- **Progressive Disclosure**: Show advanced options only when relevant (e.g., interval timing)
- **Clear CTAs**: One primary action per screen (e.g., “Save Reminder”, “Upgrade Now”)
- **Design Consistency**: Consistent use of type, icons, colors, and buttons throughout the UI

---

This structure ensures that **users can achieve their goals quickly and confidently**, while reinforcing MedMinder’s mission to make medication adherence simple, engaging, and effective.



--------


# MedMinder Application: User Stories

This section details the functional requirements of the MedMinder application, presented as user stories from the perspective of key personas. Each story outlines a user's role, their desired action, and the specific benefit derived from that action.

---

## Persona 1: The Busy Professional (Elena, 34)
> Elena requires efficient and private medication management to fit her demanding schedule.

### Account Management & Privacy
* **Sign-Up & Login:** As Elena, I want to securely sign up and log in, so that my personal health data is protected.
* **Notification Control:** As Elena, I want to customize my notification preferences (email, SMS, push), so that reminders integrate seamlessly into my busy day.
* **Secure Logout:** As Elena, I want to quickly log out from any device, so that my privacy is always maintained.

### Medication & Reminder Management
* **Medication Scheduling:** As Elena, I want to easily add medications and set up recurring schedules, so that I consistently take my doses.
* **Discrete Reminders:** As Elena, I want to receive unobtrusive reminders at my chosen times, so that my daily routine is not disrupted.
* **Quick Reminder Actions:** As Elena, I want to snooze or dismiss reminders with a single tap, so that I can manage them efficiently on the go.
* **Effortless Logging:** As Elena, I want to mark a dose as "Taken" or "Skipped" with one click, so that logging my adherence is quick and simple.
* **Dose Overview:** As Elena, I want to view my upcoming and past doses in a calendar format, so that I can effectively plan my medication schedule.

### Motivation & Progress Tracking
* **Adherence Rewards:** As Elena, I want to earn points and badges for consistent medication adherence, so that I feel motivated to maintain my routine.
* **Progress Visualization:** As Elena, I want to track my adherence streak and rank, so that I can easily monitor my long-term progress.

### Data & Insights
* **Simple Analytics:** As Elena, I want to view clear analytics about my medication adherence, so that I can identify patterns and improve my habits.
* **Report Export:** As Elena, I want to download or email my adherence reports, so that I can share them during doctor's appointments.

---

## Persona 2: The Sandwich Carer (David, 52)
> David needs comprehensive tools to manage medication for multiple family members while coordinating care.

### Multi-User & Caregiver Management
* **Dependent Management:** As David, I want to create and manage medication schedules for my mother, so that I can ensure her adherence.
* **Family Coordination:** As David, I want to invite family members to join MedMinder, so that we can collaboratively coordinate care.
* **Centralized Overview:** As David, I want to view all family members’ medication plans and adherence from a central dashboard, so that I have complete visibility of their care.
* **Refill Alerts:** As David, I want to receive notifications when my mother’s medication is low, so that I can reorder in a timely manner.
* **Missed Dose Alerts:** As David, I want to be notified if my mother misses a dose, so that I can follow up with her.
* **Provider Sharing:** As David, I want to share adherence reports with healthcare providers, so that everyone involved in care is well-informed.

### Advanced Reminders & Scheduling
* **Complex Scheduling:** As David, I want to set up intricate medication schedules (e.g., alternating days, multiple times daily), so that my mother’s specific needs are met.
* **Visual Calendar:** As David, I want to see a color-coded calendar for all medications, so that I can quickly identify any scheduling conflicts or gaps.

### Communication & Support
* **In-App Communication:** As David, I want to send encouraging messages or reminders to my mother directly through the app, so that I can provide support.
* **Caregiver Resources:** As David, I want to access educational content about medication management for caregivers, so that I can enhance my caregiving knowledge.

---

## Persona 3: The Newly Diagnosed Teen (Leo, 16)
> Leo seeks an engaging, easy-to-use, and supportive platform to manage his new diagnosis and medication routine.

### Onboarding & Education
* **Intuitive Onboarding:** As Leo, I want a clear, step-by-step onboarding process, so that I can easily understand how to use MedMinder.
* **Accessible Education:** As Leo, I want to access relevant educational content about my condition and medication adherence, so that I feel informed and empowered.

### Gamification & Engagement
* **Rewarding Adherence:** As Leo, I want to earn points, badges, and achievements for taking my medication on time, so that the process feels like a fun game.
* **Visible Progress:** As Leo, I want to see my progress visually (e.g., streaks, levels, leaderboards), so that I stay motivated to continue.
* **Positive Reinforcement:** As Leo, I want to receive positive feedback and encouragement when I reach milestones, so that I feel recognized for my efforts.

### Reminders & Logging
* **Engaging Reminders:** As Leo, I want reminders that are engaging and not intrusive, so that I don't feel annoyed by the routine.
* **Quick Logging:** As Leo, I want to log my doses rapidly, potentially with emojis or quick actions, so that it doesn't feel like a chore.

### Community & Sharing (Optional)
* **Optional Sharing:** As Leo, I want to optionally share my achievements with friends or family, so that I can receive additional encouragement.
* **Group Challenges:** As Leo, I want to participate in challenges or group goals, so that I can experience extra motivation through competition or collaboration.

---

## Universal User Stories (Applicable to All Personas)
> These stories cover core functionalities beneficial to every MedMinder user.

### Calendar & Scheduling
* **Comprehensive Calendar:** As a user, I want to view all my medications and reminders within a calendar, so that I can efficiently plan my week or month.
* **Calendar Filtering:** As a user, I want to filter the calendar by medication, status, or family member, so that I can easily focus on relevant information.
* **Flexible Schedule Management:** As a user, I want to easily edit or delete reminders, so that I can adapt to changes in my schedule.

### Notifications
* **Customizable Delivery:** As a user, I want to choose my preferred reminder delivery method (email, SMS, push) and set quiet hours, so that notifications are received appropriately.
* **Escalation Alerts:** As a user, I want to receive escalation notifications if a dose is missed (e.g., a secondary reminder or alert to a caregiver), so that missed doses are addressed promptly.

### Gamification
* **Dashboard Visibility:** As a user, I want to see my current points, badges, streaks, and rank on my personalized dashboard, so that my progress is always visible.
* **Achievement Unlocks:** As a user, I want to unlock new achievements for consistent adherence, personal improvement, or contributing positively to others, so that I remain engaged.

### Analytics & Reports
* **Adherence Trends:** As a user, I want to view clear trends in my medication adherence over time, so that I can understand my patterns.
* **Data Export:** As a user, I want to easily export or share my adherence data, so that I can communicate my progress with healthcare providers or family members.

### Premium Features
* **Premium Access:** As a user, I want to upgrade to a premium subscription, so that I can access advanced analytics, calendar integrations, and priority support.
* **Subscription Management:** As a user, I want to easily manage my subscription and payment details, so that I have full control over my premium features.