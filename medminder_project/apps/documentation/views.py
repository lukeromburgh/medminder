from django.shortcuts import render

# # Create your views here.
# def overview(request):
#     """
#     Render the overview page for the documentation.
#     """
#     return render(request, 'documentation/overview.html')

def the_why(request):
    context = {
        'page_title': 'MedMinder Documentation',
        'background_color': "#FFFFFF",
        'text_color': "#171717",
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