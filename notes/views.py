from django.shortcuts import render, redirect, get_object_or_404
from .models import Note

ERRO_CAMPOS_VAZIOS = 'Escreva um título e um conteúdo para salvar a anotação.'


def index(request):
    """GET  /  -> mural com todas as anotações.
       POST /  -> cria uma anotação nova."""
    if request.method == 'POST':
        title = request.POST.get('titulo', '').strip()
        content = request.POST.get('detalhes', '').strip()

        if not title or not content:
            return _pagina_inicial(request, ERRO_CAMPOS_VAZIOS, title, content)

        Note.objects.create(title=title, content=content)
        return redirect('index')

    return _pagina_inicial(request)


def update(request, note_id):
    """GET  /update/<id>  -> formulário preenchido com a anotação.
       POST /update/<id>  -> salva as alterações e volta para o mural."""
    note = get_object_or_404(Note, id=note_id)

    if request.method == 'POST':
        title = request.POST.get('titulo', '').strip()
        content = request.POST.get('detalhes', '').strip()

        if not title or not content:
            return _pagina_edicao(request, note, ERRO_CAMPOS_VAZIOS, title, content)

        note.title = title
        note.content = content
        note.save()
        return redirect('index')

    return _pagina_edicao(request, note, '', note.title, note.content)


def delete(request, note_id):
    """POST /delete/<id> -> apaga a anotação e volta para o mural."""
    note = get_object_or_404(Note, id=note_id)

    # Só apaga via POST (botão do card), assim um simples acesso à URL
    # não remove nada por acidente.
    if request.method == 'POST':
        note.delete()
    return redirect('index')


def _pagina_inicial(request, erro='', titulo='', detalhes=''):
    all_notes = Note.objects.all()
    return render(request, 'notes/index.html', {
        'notes': all_notes,
        'erro': erro,
        'titulo': titulo,
        'detalhes': detalhes,
    })


def _pagina_edicao(request, note, erro='', titulo='', detalhes=''):
    return render(request, 'notes/edit.html', {
        'note': note,
        'erro': erro,
        'titulo': titulo,
        'detalhes': detalhes or '',
    })
