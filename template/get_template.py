def html_template(is_sparcs=True):
    template_file = 'emailTemplate.html' if is_sparcs else 'nonSparcsEmailTemplate.html'
    template_path = f'./template/{template_file}'
    with open(template_path, 'r') as template:
        content = template.read()
    return content
