from django.core.cache import cache
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Clear the cache."

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 1))
        cache.clear()
        if verbosity >= 1:
            print "Cache cleared."

