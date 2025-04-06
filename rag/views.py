from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect

from rag.models import FileModel, DirectoryModel
from rag.rag import upload_file, ask_question


@login_required
def home(request):
    if request.user.is_superuser:
        return redirect('admin:index')
    return render(request, 'home.html', {'user': request.user})


@login_required
def files(request):
    if request.method == 'GET':
        files = FileModel.objects.filter(directory__owner=request.user)
        directories = DirectoryModel.objects.filter(owner=request.user)
        return render(request, 'files.html', {'files': files, 'directories': directories})

    elif request.method == 'POST':
        data = request.FILES['file']
        directory = request.POST.get('directory', 2)
        path = data.file.file.name
        file = FileModel.objects.create(directory=DirectoryModel.objects.get(id=directory), name=data.name)

        upload_file(data, file, path)

        # if not DirectoryModel.objects.filter(id=directory).filter(owner=request.user).exists():
        #     raise Http404()

        return redirect('files')
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def file_delete(request, file_id):
    try:
        file = FileModel.objects.get(id=file_id)
        if file.directory.owner != request.user:
            return HttpResponseForbidden()
        file.delete()
        return redirect('files')

    except FileModel.DoesNotExist:
        return Http404()


@login_required
def directory_delete(request, directory_id):
    try:
        directory = DirectoryModel.objects.get(id=directory_id)
        if directory.owner != request.user:
            return HttpResponseForbidden()
        directory.delete()
        return redirect('files')

    except DirectoryModel.DoesNotExist:
        return Http404()


@login_required
def directory_create(request):
    DirectoryModel.objects.create(name=request.POST['name'], owner=request.user)
    return redirect('files')


@login_required
def query(request):
    query_ = request.GET.get('query')
    dir_id = request.GET.get('directory')

    if query_:
        corpus = DirectoryModel.objects.get(id=dir_id).corpus
        res = ask_question(query_, corpus)
    else:
        res = "Hello. How can I help you?"

    directories = DirectoryModel.objects.filter(owner=request.user)
    return render(request, "chat.html", {'res': res, 'directories': directories})
