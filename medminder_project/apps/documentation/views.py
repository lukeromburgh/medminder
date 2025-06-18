from django.shortcuts import render

# # Create your views here.
# def overview(request):
#     """
#     Render the overview page for the documentation.
#     """
#     return render(request, 'documentation/overview.html')

def overview(request):
    context = {
        'page_title': 'My Documentation',
        'background_color': "#54bbff",  # Light blue
        'left_title': 'apps.reminders',
        'left_subtitle': 'A comprehensive reminder system for managing tasks and notifications.',
        'right_title': 'Key features',
        'body_1': '<p>First section of content with detailed information about the feature set.</p>',
        'body_2': '<p>Second section covering additional functionality and capabilities.</p>'
    }
    return render(request, 'documentation/partials/section_template.html', context)