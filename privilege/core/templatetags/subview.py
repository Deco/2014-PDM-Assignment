from django import template

def card(item):
    template = 'null'

    context = {
            #Dictionary of things to pass back

    }
    #if statements that choose what 'template' should be
    if item == 5:
        template = 'item5.html'
    else:
        template = 'default.html'

    #render the template
    return render_to_string(template, context)
