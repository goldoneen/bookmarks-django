from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse

from .forms import ImageCreateForm
from .models import Image

# Create your views here.
@login_required
def image_create(request):
  if request.method == 'POST':
    # form is sent
    form = ImageCreateForm(data=request.POST)
    if form.is_valid():
      # from data is valid
      cd = form.cleaned_data
      new_image = form.save(commit=False)
      # assign current user to the item
      new_image.user = request.user
      new_image.save()
      messages.success(request, 'Image added successfully')
      # redirect to new created item detail view
      return redirect(new_image.get_absolut_url())
  else:
    # build form with data provided by the bookmarklet via GET
    form = ImageCreateForm(data=request.GET)
  return render(
    request,
    'images/image/create.html',
    {'section': 'images', 'form': form}
  )

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(
        request,
        'images/image/detail.html',
        {'section': 'images', 'image': image},
    )

@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
          # If AJAX request and page out of range
          # return an empty page
          return HttpResponse('')
        # If page out of range return last page of results
        images = paginator.page(paginator.num_pages)
    
    if images_only:
      return render(
        request,
        'images/image/list_images.html',
        {'section': 'images', 'images': images}
      )
    
    return render(
      request,
      'images/image/list.html',
      {'section': 'images', 'images': images}
    )
  



