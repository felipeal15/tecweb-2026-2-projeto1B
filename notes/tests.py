from django.test import TestCase
from django.urls import reverse

from .models import Note, Tag


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


class TagTests(TestCase):
    def criar(self, titulo, tag):
        return self.client.post(reverse('index'), {'titulo': titulo, 'detalhes': 'texto', 'tag': tag})

    def test_cria_anotacao_com_tag(self):
        self.criar('Miojo', 'comida')
        note = Note.objects.get(title='Miojo')
        self.assertEqual(note.tag.name, 'comida')

    def test_cria_anotacao_sem_tag(self):
        self.criar('Sem tag', '')
        self.assertIsNone(Note.objects.get(title='Sem tag').tag)
        self.assertEqual(Tag.objects.count(), 0)

    def test_nao_duplica_tags(self):
        self.criar('Miojo', 'comida')
        self.criar('Pão doce', '#Comida ')
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.get().notes.count(), 2)

    def test_edita_tag_da_anotacao(self):
        self.criar('Miojo', 'comida')
        note = Note.objects.get()
        response = self.client.get(reverse('update', args=[note.id]))
        self.assertContains(response, 'value="comida"')

        self.client.post(reverse('update', args=[note.id]), {'titulo': 'Miojo', 'detalhes': 'texto', 'tag': 'receita'})
        note.refresh_from_db()
        self.assertEqual(note.tag.name, 'receita')
        # "comida" ficou sem anotações e foi removida
        self.assertFalse(Tag.objects.filter(name='comida').exists())

    def test_remove_tag_da_anotacao(self):
        self.criar('Miojo', 'comida')
        note = Note.objects.get()
        self.client.post(reverse('update', args=[note.id]), {'titulo': 'Miojo', 'detalhes': 'texto', 'tag': ''})
        note.refresh_from_db()
        self.assertIsNone(note.tag)

    def test_apagar_anotacao_nao_apaga_tag_em_uso(self):
        self.criar('Miojo', 'comida')
        self.criar('Pão doce', 'comida')
        self.client.post(reverse('delete', args=[Note.objects.get(title='Miojo').id]))
        self.assertTrue(Tag.objects.filter(name='comida').exists())

    def test_lista_de_tags(self):
        self.criar('Miojo', 'comida')
        self.criar('Simpsons', 'tv')
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '#comida')
        self.assertContains(response, '#tv')
        self.assertContains(response, reverse('tag_detail', args=[Tag.objects.get(name='tv').id]))

    def test_pagina_da_tag_mostra_so_suas_anotacoes(self):
        self.criar('Miojo', 'comida')
        self.criar('Simpsons', 'tv')
        tag = Tag.objects.get(name='comida')
        response = self.client.get(f'/tags/{tag.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Miojo')
        self.assertNotContains(response, 'Simpsons')

    def test_tag_inexistente_da_404(self):
        self.assertEqual(self.client.get('/tags/999/').status_code, 404)

    def test_pagina_inicial_tem_link_para_tags(self):
        self.criar('Miojo', 'comida')
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'href="/tags/"')
        self.assertContains(response, '#comida')
