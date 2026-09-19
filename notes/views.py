from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from .models import Note, Tag

ERRO_CAMPOS_VAZIOS = 'Escreva um título e um conteúdo para salvar a anotação.'


def index(request):
    """GET  /  -> mural com todas as anotações.
       POST /  -> cria uma anotação nova."""
    if request.method == 'POST':
        title, content, tag_name = _campos_do_formulario(request)

        if not title or not content:
            return _pagina_inicial(request, ERRO_CAMPOS_VAZIOS, title, content, tag_name)

        Note.objects.create(title=title, content=content, tag=_busca_ou_cria_tag(tag_name))
        return redirect('index')

    return _pagina_inicial(request)


def update(request, note_id):
    """GET  /update/<id>  -> formulário preenchido com a anotação.
       POST /update/<id>  -> salva as alterações e volta para o mural."""
    note = get_object_or_404(Note, id=note_id)

    if request.method == 'POST':
        title, content, tag_name = _campos_do_formulario(request)

        if not title or not content:
            return _pagina_edicao(request, note, ERRO_CAMPOS_VAZIOS, title, content, tag_name)

        tag_antiga = note.tag
        note.title = title
        note.content = content
        note.tag = _busca_ou_cria_tag(tag_name)
        note.save()
        _apaga_tag_se_vazia(tag_antiga)
        return redirect('index')

    tag_name = note.tag.name if note.tag else ''
    return _pagina_edicao(request, note, '', note.title, note.content, tag_name)


def delete(request, note_id):
    """POST /delete/<id> -> apaga a anotação e volta para o mural."""
    note = get_object_or_404(Note, id=note_id)

    # Só apaga via POST (botão do card), assim um simples acesso à URL
    # não remove nada por acidente.
    if request.method == 'POST':
        tag = note.tag
        note.delete()
        _apaga_tag_se_vazia(tag)
    return redirect('index')


def tags(request):
    """GET /tags/ -> lista com todas as tags."""
    all_tags = Tag.objects.annotate(total=Count('notes')).order_by('name')
    return render(request, 'notes/tags.html', {'tags': all_tags})


def tag_detail(request, tag_id):
    """GET /tags/<id>/ -> anotações de uma tag específica."""
    tag = get_object_or_404(Tag, id=tag_id)
    return render(request, 'notes/tag_detail.html', {
        'tag': tag,
        'notes': tag.notes.select_related('tag'),
    })


def _pagina_inicial(request, erro='', titulo='', detalhes='', tag=''):
    all_notes = Note.objects.select_related('tag')
    return render(request, 'notes/index.html', {
        'notes': all_notes,
        'erro': erro,
        'titulo': titulo,
        'detalhes': detalhes,
        'tag': tag,
    })


def _pagina_edicao(request, note, erro='', titulo='', detalhes='', tag=''):
    return render(request, 'notes/edit.html', {
        'note': note,
        'erro': erro,
        'titulo': titulo,
        'detalhes': detalhes or '',
        'tag': tag,
    })


def _campos_do_formulario(request):
    title = request.POST.get('titulo', '').strip()
    content = request.POST.get('detalhes', '').strip()
    # "#Comida " e "comida" são a mesma tag
    tag_name = request.POST.get('tag', '').strip().lstrip('#').strip().lower()
    return title, content, tag_name


def _busca_ou_cria_tag(tag_name):
    """Devolve a tag com esse nome, criando-a se ainda não existir.
       Sem nome, a anotação fica sem tag."""
    if not tag_name:
        return None
    tag, _ = Tag.objects.get_or_create(name=tag_name)
    return tag


def _apaga_tag_se_vazia(tag):
    """Remove a tag quando nenhuma anotação usa mais ela."""
    if tag is not None and not tag.notes.exists():
        tag.delete()
