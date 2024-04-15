def html_template() -> str:
    """
    Get the email template.

    :return: Email template as HTML.
    :rtype: str
    """

    with open('./template/emailTemplate.html', 'r') as template:
        content = template.read()
    return content
