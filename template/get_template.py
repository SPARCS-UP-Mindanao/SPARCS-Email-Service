def html_template():
    content = ""
    with open('./template/emailTemplate.html', 'r') as template:
        content = template.read()
    return content