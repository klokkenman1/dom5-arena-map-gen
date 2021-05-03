import sys

from django.core.management.base import BaseCommand

from apps.domdata.parser import parse_units


class Command(BaseCommand):
    help = "Parse data inside the DB"

    def handle(self, *args, **options):
        sys.stdout.write("Start parsing \n")
        parse_units()
        sys.stdout.write("Parsing finished \n")
