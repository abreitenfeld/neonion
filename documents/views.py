from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse, HttpResponseForbidden
from documents.models import Document, File
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404


@login_required
@require_POST
def upload_file(request):
    document_properties = {}
    document_fields = ["title", "creator", "type", "contributor", "coverage", "description", "format", "identifier",
                       "language", "publisher", "relation", "rights", "source", "subject"]

    for m in document_fields:
        document_properties[m] = request.POST.get(m, None)  # fetches value or provides default if it does not exist

    for upload_field in request.FILES:
        for f in request.FILES.getlist(upload_field):
            document = Document.objects.create_document_from_file(f, **document_properties)
            document.save()
 
            if document is not None:
                # import document into workspace
                request.user.owned_documents.add(document)

    return redirect('/')


@login_required
@require_GET
def viewer(request, pk):
    f = get_object_or_404(File, pk=pk)
    if f.origin_url is None or len(f.origin_url) == 0:
        # return raw data
        return HttpResponse(str(f.raw_data), content_type=f.content_type + '; charset=utf-8')
    else:
        return redirect(f.origin_url)


@login_required()
@require_GET
def gmpg_open(request):
    if 'url' in request.GET:
        url = request.GET['url']

        document = Document.objects.get_from_url(url)
        if document is None:
            # create new document
            document_properties = {}
            document_fields = ["title", "creator", "type", "contributor", "coverage", "description", "format",
                               "identifier", "language", "publisher", "relation", "rights", "source", "subject"]

            # fetches value or provides default if it does not exist
            for m in document_fields:
                document_properties[m] = request.GET.get(m, None)
            document = Document.objects.create_from_url(url, 'application/pdf', **document_properties)

            # import document into workspace
            request.user.owned_documents.add(document)

        # redirect to annotator
        return redirect('neonion.views.render_annotator', group_pk=request.user.email, document_pk=document.pk)

    return HttpResponseForbidden()
