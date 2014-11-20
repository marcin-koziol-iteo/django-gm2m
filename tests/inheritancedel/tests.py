import django
from django.utils.unittest import skipIf

from mock_django.signals import mock_signal_receiver

from gm2m.signals import deleting

from .models import Task, Subtask, Milestone
from .models import Links

from ..base import TestCase


@skipIf(django.VERSION < (1, 6), 'No deletion customisation for Django < 1.6')
class InheritanceDeletionTests(TestCase):

    def setUp(self):
        self.subtask = Subtask.objects.create()
        self.milestone = Milestone.objects.create()
        self.links = Links.objects.create()

    def test_delete_src(self):
        self.links.related_objects = [self.subtask, self.milestone]

        # cascade delete on the src side
        with mock_signal_receiver(deleting) as on_delete:
            self.links.delete()
            self.assertEqual(on_delete.call_count, 0)

        # no more Links instances
        self.assertEqual(Links.objects.count(), 0)
        # the through model instances have been deleted
        self.assertEqual(self.subtask.links_set.through.objects.count(), 0)

    def test_delete_tgt(self):
        self.links.related_objects = [self.subtask, self.milestone]

        with mock_signal_receiver(deleting) as on_delete:
            self.subtask.delete()
            self.assertEqual(on_delete.call_count, 1)

        # only one Task instance left (the Milestone instance)
        self.assertEqual(Task.objects.count(), 1)
        # and the through model instances have not been deleted
        self.assertEqual(self.links.related_objects.through.objects.count(), 2)