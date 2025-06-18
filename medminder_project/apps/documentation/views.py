from django.shortcuts import render

# # Create your views here.
# def overview(request):
#     """
#     Render the overview page for the documentation.
#     """
#     return render(request, 'documentation/overview.html')

def overview(request):
    context = {
        'page_title': 'Overview & Documentation',
        'background_color': "#0F0F14",
        'text_color': "#E2EAF3",
        'left_title': 'Why I Built MedMinder',
        'left_subtitle':'''During my time volunteering at an old age home, I saw firsthand the immense challenges many residents faced in managing their medication schedules. It was clear that staying on top of rigid, timely doses was a significant hurdle, often leading to missed medications or confusion. This experience sparked an idea: what if there was a way to make medication adherence simpler, more engaging, and less of a burden?

That's why I created MedMinder, a medical reminder app designed to transform how people approach their medication routines. My primary goal was to address the critical need for a more effective and user-friendly solution for medication management, particularly for those with complex schedules.''',
        'right_title': 'Key features',
        'body_1': '<p>First section of content with detailed information about the feature set.</p>',
        'body_2': '<p>Second section covering additional functionality and capabilities.</p>'
    }
    return render(request, 'documentation/partials/section_template.html', context)