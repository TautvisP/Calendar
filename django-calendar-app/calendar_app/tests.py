from django.test import TestCase
from .models import Client, Note

class ClientModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test Client",
            email="testclient@example.com"
        )

    def test_client_creation(self):
        self.assertEqual(self.client.name, "Test Client")
        self.assertEqual(self.client.email, "testclient@example.com")

class NoteModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test Client",
            email="testclient@example.com"
        )
        self.note = Note.objects.create(
            client=self.client,
            content="This is a test note."
        )

    def test_note_creation(self):
        self.assertEqual(self.note.content, "This is a test note.")
        self.assertEqual(self.note.client, self.client)