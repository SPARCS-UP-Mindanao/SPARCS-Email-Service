def html_template(is_durian_py=True):
    template_file = 'durianPyEmailTemplate.html' if is_durian_py else 'nonDurianPyEmailTemplate.html'
    template_path = f'./template/{template_file}'
    with open(template_path, 'r') as template:
        content = template.read()
    return content
