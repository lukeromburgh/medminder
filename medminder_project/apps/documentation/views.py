from django.shortcuts import render

# # Create your views here.
# def overview(request):
#     """
#     Render the overview page for the documentation.
#     """
#     return render(request, 'documentation/overview.html')

def home(request):
    """
    Render the home page for the documentation.
    """
    context = {
        'page_title': 'MedMinder Documentation',
        'background_color': "#FFFFFF",
        'text_color': "#171717",
    }
    return render(request, 'base_documentation.html', context)

def the_why(request):
    context = {
        'page_title': 'MedMinder Documentation',
        'background_color': "#FFFFFF",
        'text_color': "#171717",
        'banner_url': '/static/images/documentation/readme-header.png',  # Adjust the path as needed
        'left_title': 'Why I Built MedMinder',
        'left_subtitle': """
<ul class="list-disc pl-6 space-y-2">
  <li>
    <b>Real-World Inspiration:</b>
    <span>
      During my time volunteering at an old age home, I saw firsthand the immense challenges many residents faced in managing their medication schedules. Staying on top of rigid, timely doses was a significant hurdle, often leading to missed medications or confusion.
    </span>
  </li>
  <li>
    <b>The Spark:</b>
    <span>
      This experience sparked an idea: what if there was a way to make medication adherence simpler, more engaging, and less of a burden?
    </span>
  </li>
  <li>
    <b>The Solution:</b>
    <span>
      That's why I created MedMinder—a medical reminder app designed to transform how people approach their medication routines. My primary goal was to address the critical need for a more effective and user-friendly solution for medication management, particularly for those with complex schedules.
    </span>
  </li>
</ul>
""",
        'right_title': 'Beyond the Obvious: Gamification for Broader Appeal',
        'body_1': """
<ul class="list-disc pl-6 space-y-2">
  <li>
    <b>Broader Impact:</b>
    <span>
      While the initial inspiration came from the elderly, I quickly realized the potential for MedMinder to benefit a much wider audience.
    </span>
  </li>
  <li>
    <b>Gamification:</b>
    <span>
      By incorporating gamification elements, MedMinder isn't just a reminder app; it's an interactive experience. This innovative approach makes managing medication not only easier but also more engaging and even enjoyable.
    </span>
  </li>
  <li>
    <b>Universal Relevance:</b>
    <span>
      The gamified aspect allows MedMinder to resonate with a younger demographic as well. In today's fast-paced world, individuals of all ages can struggle with consistency. MedMinder's rewarding system and progress tracking help foster better habits and promote long-term adherence, transforming a routine task into an achievable goal.
    </span>
  </li>
</ul>
""",
        'body_2': ""  # Optionally add more here
    }
    return render(request, 'documentation/partials/section_template.html', context)

def overview(request):
    context = {
        'page_title': 'MedMinder Documentation',
        'background_color': "#FFFFFF",
        'text_color': "#171717",
        'left_title': 'Project Overview',
        'left_subtitle': (
            "MedMinder is a modern, gamified medication management platform built with Django. "
            "It empowers users to take control of their health by providing smart reminders, adherence tracking, "
            "and a beautiful calendar view—all tailored to each user’s timezone and schedule."
        ),
        'right_title': 'Key Features',
        'body_1': """
<ul class="list-disc pl-6 space-y-2">
  <li><b>Smart Medication Reminders:</b> Set up complex schedules (daily, weekly, monthly, or custom), receive reminders via email or SMS, and never miss a dose.</li>
  <li><b>Gamified Adherence:</b> Earn points, streaks, badges, and ranks for consistent medication adherence, making health management engaging and rewarding.</li>
  <li><b>Premium Calendar View:</b> Visualize upcoming and past doses, plan ahead, and see your progress at a glance (premium users only).</li>
  <li><b>Family & Accountability (Coming Soon):</b> Invite family or caregivers to view your progress and provide encouragement.</li>
  <li><b>Personalized Analytics:</b> Get insights and statistics to understand your adherence patterns and improve your routines.</li>
  <li><b>Timezone Awareness:</b> All reminders and logs are timezone-aware, ensuring accuracy for users anywhere in the world.</li>
  <li><b>Secure & Scalable:</b> Built on Django with robust authentication and secure data handling.</li>
</ul>
""",
        'body_2': """
        <br>
<h3 class="text-lg font-semibold mb-2">Technical Highlights</h3>
<ul class="list-disc pl-6 space-y-1 mb-4">
  <li><b>Django Backend:</b> Modular app structure (<code>accounts</code>, <code>reminders</code>, <code>payments</code>, <code>core</code>, etc.) for clean separation of concerns.</li>
  <li><b>Stripe Integration:</b> Handles premium subscriptions and paywall logic for advanced features.</li>
  <li><b>Custom Cron Jobs:</b> Automated background tasks for sending reminders, updating stats, and more.</li>
  <li><b>Responsive UI:</b> Modern, mobile-friendly templates using Tailwind CSS and Alpine.js.</li>
  <li><b>Extensible:</b> Easily add new features, integrations, or notification channels.</li>
</ul>
""",
    }
    return render(request, 'documentation/partials/section_template.html', context)

def under_the_hood(request):
    context = {
        'page_title': 'Under the Hood',
        'background_color': "#FFFFFF",
        'text_color': "#1A202C",
        'left_title': 'Under the Hood',
        'left_subtitle': 'A technical deep dive into how MedMinder works behind the scenes.',
        'right_title': 'Architecture & Key Components',
        'body_1': """
<p>MedMinder is built with a modular Django architecture, separating concerns into distinct apps such as <code>accounts</code>, <code>reminders</code>, <code>payments</code>, and <code>core</code>. This ensures maintainability and scalability.</p>
<pre>
medminder_project/
├── apps/
│   ├── accounts/
│   ├── reminders/
│   ├── payments/
│   └── documentation/
├── templates/
├── static/
└── manage.py
</pre>
<p>Each app encapsulates its own models, views, and logic. For example, <code>reminders</code> handles all scheduling, adherence tracking, and calendar logic, while <code>payments</code> manages Stripe integration and premium access.</p>
""",
        'body_2': """
<h3 class="text-lg font-semibold mb-2">Key Technologies & Patterns</h3>
<ul class="list-disc pl-6 mb-4">
  <li><b>Django ORM:</b> For robust, relational data modeling and queries.</li>
  <li><b>Stripe API:</b> Handles subscriptions, webhooks, and premium gating.</li>
  <li><b>Cron Jobs & Management Commands:</b> For sending reminders and updating stats in the background.</li>
  <li><b>Tailwind CSS & Alpine.js:</b> For a modern, responsive UI and interactive docs.</li>
  <li><b>Logging & Monitoring:</b> All critical events (webhooks, payments, reminders) are logged for debugging and analytics.</li>
</ul>
<pre>
# Example: Creating a reminder (simplified)
reminder = Reminder.objects.create(
    user=request.user,
    medication="Aspirin",
    schedule=Schedule.objects.create(
        repeat_type="daily",
        start_date=date.today(),
        time_of_day=time(8, 0)
    )
)
</pre>
<p>MedMinder’s backend is designed for extensibility, allowing new features (like SMS, analytics, or integrations) to be added with minimal friction.</p>
""",
    }
    return render(request, 'documentation/partials/section_template.html', context)


# --------------------------------------------------------------------------------#

def strategy_plane(request):
    context = {
        'page_title': 'Strategy Plane',
        'background_color': "#F7FAFC",
        'text_color': "#2D3748",
        'left_title': 'Strategy Plane',
        'left_subtitle': 'Defining the foundation of MedMinder’s purpose and direction.',
        'right_title': 'User Needs & Business Objectives',
        'body_1': f"""
<p>The Strategy Plane is the foundation of MedMinder, aligning every decision with a clear understanding of our users' needs and our core business objectives. It ensures we are building the right product for the right people, creating a sustainable and impactful business.</p>
<br>
<h3 class="text-xl font-semibold mb-2">1.1 User Needs: The "Why"</h3>
<p><strong>Core Problem:</strong><br>
Non-adherence to medication is a critical and widespread health issue. The consequences range from decreased quality of life and preventable hospitalisations to significant emotional and financial strain for individuals and their families. This problem is exacerbated by forgetfulness, complex multi-dose schedules, lack of motivation, and poor understanding of treatment regimens.</p>
<br>
<p><strong>Primary User Needs:</strong></p>
<ul class="list-disc pl-6 mb-4">
  <li><strong>Reliability & Simplicity:</strong> Users need a completely dependable system that is intuitive and removes complexity from their daily routine.</li>
  <li><strong>Motivation & Engagement:</strong> Users need encouragement to stay consistent. Positive reinforcement transforms a chore into a rewarding habit.</li>
  <li><strong>Information & Insight:</strong> Clear, accessible data helps users and caregivers feel in control and informed.</li>
  <li><strong>Support & Connection:</strong> Users benefit from feeling supported through shared progress and community connection.</li>
  <li><strong>Discretion & Trust:</strong> Absolute confidence in data privacy and security is essential.</li>
</ul>

<br>
<hr>
<br>

<h3 class="text-lg font-semibold mb-2">User Personas</h3>

<p><strong>Persona 1: "The Busy Professional" (Elena, 34)</strong><br>
<strong>Scenario:</strong> Manages a demanding career while taking daily medication for a chronic condition.<br>
<strong>Needs:</strong> Discrete, efficient reminders; values privacy.<br>
<strong>Pain Points:</strong> Misses doses due to a hectic schedule; logging feels tedious.<br>
<strong>MedMinder's Role:</strong> Persistent reminders and quick-logging features.</p>

<br>

<p><strong>Persona 2: "The Sandwich Carer" (David, 52)</strong><br>
<strong>Scenario:</strong> Cares for his elderly mother with complex medication needs.<br>
<strong>Needs:</strong> Centralized dashboard, refill alerts, report sharing.<br>
<strong>Pain Points:</strong> Confusion over schedules; lack of adherence visibility.<br>
<strong>MedMinder's Role:</strong> Multi-user caregiver accounts, shareable analytics, refill reminders.</p>

<br>

<p><strong>Persona 3: "The Newly Diagnosed Teen" (Leo, 16)</strong><br>
<strong>Scenario:</strong> Adjusting to life with Type 1 Diabetes.<br>
<strong>Needs:</strong> Engaging system, gamification, educational support.<br>
<strong>Pain Points:</strong> Dislikes routine, finds it disruptive.<br>
<strong>MedMinder's Role:</strong> Gamified experience with achievements, educational insights.</p>
<br>

""",
        'body_2': f"""
        <br>
<hr>
<br>

<h3 class="text-lg font-semibold mb-2">1.2 Business Objectives: The "How"</h3>

<p><strong>Value Proposition:</strong><br>
For individuals and caregivers struggling with medication management, MedMinder is an engaging and reliable adherence partner. Unlike simple alarm apps, we provide intelligent reminders, motivational feedback, and insightful analytics to empower users, improve health outcomes, and provide peace of mind.</p>

<br>

<p><strong>Business Model:</strong><br>
MedMinder operates on a freemium subscription model, offering essential features for free while monetizing advanced capabilities through a premium tier.</p>

<br>

<ul class="list-disc pl-6 mb-4">
  <li><strong>Free Tier:</strong>
    <ul class="list-disc pl-6">
      <li>Core medication reminders</li>
      <li>Basic adherence tracking</li>
      <li>Limited medication history</li>
    </ul>
  </li>
  <br>
  <li><strong>Premium Tier (Monthly/Annual):</strong>
    <ul class="list-disc pl-6">
      <li>Advanced analytics & reporting (PDFs)</li>
      <li>Calendar integration (Google, iCal)</li>
      <li>Caregiver accounts</li>
      <li>Refill reminders</li>
      <li>Advanced gamification & customization</li>
      <li>Pill ID & drug interaction info</li>
    </ul>
  </li>
</ul>
""",
    }
    return render(request, 'documentation/partials/section_template.html', context)
