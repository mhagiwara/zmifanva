from pyramid.view import view_config
from web import translate


@view_config(route_name='home', renderer='templates/home.pt')
def home_view(request):
    if not ('src' in request.params and 'dir' in request.params
            and request.params['dir'] in ['jb2en', 'en2jb']
            and len(request.params['src']) > 0):
        # Home page
        return {'dir': '',
                'src': '',
                'tgt': ''}
    else:
        # Translate
        tgt = translate(request.params['src'], request.params['dir'])

        return {'dir': request.params['dir'],
                'src': request.params['src'],
                'tgt': tgt}
