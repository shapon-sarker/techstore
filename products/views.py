from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
import logging
from .models import Category, Brand, Product
from .forms import CategoryForm, BrandForm, ProductForm, ProductImageForm

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('products:category_list')
    else:
        form = CategoryForm()
    return render(request, 'products/category_form.html', {'form': form})

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('products:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'products/category_form.html', {'form': form})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Category deleted successfully!')
        except:
            messages.error(request, 'Cannot delete category. It has associated products.')
        return redirect('products:category_list')
    return render(request, 'products/category_confirm_delete.html', {'category': category})

@login_required
def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'products/brand_list.html', {'brands': brands})

@login_required
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand created successfully!')
            return redirect('products:brand_list')
    else:
        form = BrandForm()
    return render(request, 'products/brand_form.html', {'form': form})

@login_required
def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated successfully!')
            return redirect('products:brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'products/brand_form.html', {'form': form})

@login_required
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        try:
            brand.delete()
            messages.success(request, 'Brand deleted successfully!')
        except:
            messages.error(request, 'Cannot delete brand. It has associated products.')
        return redirect('products:brand_list')
    return render(request, 'products/brand_confirm_delete.html', {'brand': brand})

@login_required
def product_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if category:
        products = products.filter(category_id=category)
    
    if brand:
        products = products.filter(brand_id=brand)
    
    context = {
        'products': products,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'products/product_list.html', context)

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
def product_create(request):
    if request.method == 'POST':
        logger.info("Received POST request for product creation")
        logger.info(f"Files in request: {request.FILES}")
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            logger.info(f"Product created successfully. Image path: {product.image.path if product.image else 'No image'}")
            messages.success(request, 'Product created successfully!')
            return redirect('products:list')
        else:
            logger.error(f"Form errors: {form.errors}")
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        logger.info("Received POST request for product edit")
        logger.info(f"Files in request: {request.FILES}")
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            logger.info(f"Product updated successfully. Image path: {product.image.path if product.image else 'No image'}")
            messages.success(request, 'Product updated successfully!')
            return redirect('products:detail', pk=pk)
        else:
            logger.error(f"Form errors: {form.errors}")
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Product deleted successfully!')
        except:
            messages.error(request, 'Cannot delete product. It has associated records.')
        return redirect('products:list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def product_image_upload(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product image updated successfully!')
            return redirect('products:detail', pk=pk)
    else:
        form = ProductImageForm(instance=product)
    return render(request, 'products/product_image_form.html', {'form': form, 'product': product})

@login_required
def product_image_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        if product.image:
            product.image.delete()
            product.save()
            messages.success(request, 'Product image deleted successfully!')
        return redirect('products:detail', pk=pk)
    return render(request, 'products/product_image_confirm_delete.html', {'product': product})
