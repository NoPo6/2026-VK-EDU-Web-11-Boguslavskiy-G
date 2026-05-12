from ..models import Tag, Profile


def common_data(request):
    return {
        'tags': Tag.objects.all(),
        'users': Profile.objects.all(),
    }