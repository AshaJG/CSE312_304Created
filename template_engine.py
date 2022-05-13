import sys


def render_template(html_filename, data):
    with open(html_filename) as html_file:
        template = html_file.read()
        template = replace_placeholders(template, data)
        template = render_loop(template, data)
        return template


def replace_placeholders(template, data):
    replaced_template = template
    for placeholder in data.keys():
        print(placeholder)
        if isinstance(data[placeholder], str):
            if placeholder != "image_file":
                replaced_template = replaced_template.replace("{{"+placeholder+"}}", data[placeholder])
            else:
                if data[placeholder] != '':
                    replaced_template = replaced_template.replace("{{"+placeholder+"}}", "<img src= image/" + data[placeholder] + " alt= It's a "+ data[placeholder] + " class= my_image sytle= width: 100px; height: 100p;/>")
                else:
                    replaced_template = replaced_template.replace("{{"+placeholder+"}}", "") 
    return replaced_template


def render_loop(template, data):
    if "loop_data" in data:
        loop_start_tag = "{{loop}}"
        loop_end_tag = "{{end_loop}}"

        start_index = template.find(loop_start_tag)
        end_index = template.find(loop_end_tag)
        # everything between the tags
        loop_template = template[start_index + len(loop_start_tag): end_index]

        loop_data = data["loop_data"]

        # replaces HTML with actual info
        loop_content = ""
        print(loop_data)
        for single_piece_of_content in loop_data:
            loop_content += replace_placeholders(loop_template, single_piece_of_content)

        final_content = template[:start_index] + loop_content + template[end_index + len(loop_end_tag):]

        return final_content
    return template
