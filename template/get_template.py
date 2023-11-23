def html_template():
    with open('./template/emailTemplate.html', 'r') as template:
        content = template.read()
    return content
