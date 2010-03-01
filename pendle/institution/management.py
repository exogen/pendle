from django.db import transaction
from django.db.models import signals
from django.contrib.auth.models import User

from pendle.institution import models
from pendle.institution.models import Profile


@transaction.commit_on_success
def create_profiles(sender, app, created_models, verbosity, **kwargs):
    if Profile in created_models:
        if verbosity >= 1:
            print "Creating profiles for all users"
        users = User.objects.all()
        for user in users:
            if verbosity >= 2:
                "Creating profile for %s" % user
            profile, created = Profile.objects.get_or_create(user=user)

signals.post_syncdb.connect(create_profiles, sender=models)
