from django.test import TestCase
from django.urls import reverse

from .models import Note


class CrudTests(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title='Receita de miojo', content='Bata com um martelo')

    def test_index_lista_anotacoes(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receita de miojo')
        self.assertContains(response, 'notes/css/getit.css')

    def test_cria_anotacao(self):
        response = self.client.post(reverse('index'), {'titulo': 'Pão doce', 'detalhes': 'Abra o pão'})
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(Note.objects.filter(title='Pão doce', content='Abra o pão').exists())

    def test_nao_cria_anotacao_vazia(self):
        response = self.client.post(reverse('index'), {'titulo': '', 'detalhes': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 1)

    def test_pagina_de_edicao_vem_preenchida(self):
        response = self.client.get(reverse('update', args=[self.note.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Receita de miojo"')
        self.assertContains(response, 'Bata com um martelo')

    def test_edita_anotacao(self):
        response = self.client.post(
            reverse('update', args=[self.note.id]),
            {'titulo': 'Miojo EDITADO', 'detalhes': 'Novo conteúdo'},
        )
        self.assertRedirects(response, reverse('index'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Miojo EDITADO')
        self.assertEqual(self.note.content, 'Novo conteúdo')

    def test_apaga_anotacao(self):
        response = self.client.post(reverse('delete', args=[self.note.id]))
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_get_em_delete_nao_apaga(self):
        self.client.get(reverse('delete', args=[self.note.id]))
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())

    def test_anotacao_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse('update', args=[999])).status_code, 404)
        self.assertEqual(self.client.post(reverse('delete', args=[999])).status_code, 404)
