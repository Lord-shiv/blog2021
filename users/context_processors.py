from . forms import RegistrationForm


def modal_register(request):
    '''form can be access from any page'''
    return {
        'register_form': RegistrationForm(),
    }
