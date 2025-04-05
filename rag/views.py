from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect

from rag.models import FileModel, DirectoryModel
from rag.rag import do, upload_file_to_gcs


def home(request):
    if request.user.is_superuser:
        return redirect('admin:index')
    return render(request, 'home.html', {'user': request.user})


@login_required
def files(request):
    if request.method == 'GET':
        files = FileModel.objects.filter(directory__owner=request.user)
        return render(request, 'files.html', {'files': files})
    elif request.method == 'POST':
        file = request.FILES['file']
        directory = request.POST.get('directory', 1)
        url = upload_file_to_gcs(file)
        do(url)

        # if not DirectoryModel.objects.filter(id=directory).filter(owner=request.user).exists():
        #     raise Http404()

        FileModel.objects.create(directory=directory, name=file.name)
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
