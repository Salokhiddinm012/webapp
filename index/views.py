from itertools import product, count
from lib2to3.fixes.fix_input import context
from re import search

import telebot
from django.shortcuts import render , redirect
from django.template.context_processors import request
from telebot.util import update_types

from .models  import  Product, Category,Cart
from .forms import SearchForm,RegisterForm
from django.contrib.auth.models import User
from django.views import View
from django.views.generic import ListView
from django.contrib.auth import logout, login

bot = telebot.TeleBot('6882039068:AAHVFdsxzYU92eUMsJ6IhMbwfIg5CexR-Bg')
admin_id = 7116206892



def home_page(request) :
    all_Product = Product.objects.all()
    all_Categories= Category.objects.all()
    search=SearchForm()
    context={'Products': all_Product ,'categories': all_Categories ,'form': search}
    return render (request, 'home.html', context)

def category_page(request,pk):
    category=Category.objects.get(id=pk)
    exact_products=Product.objects.filter(pr_category=category)
    context={'products':exact_products}
    return render(request,'category.html',context)

def product_page(request,pk):
    product = Product.objects.filter(id=pk)
    context = {'products': product}
    return render(request,'product.html', context)


def search_product(request):
   if request.method == 'POST':
       get_product=request.POST.get ('search_product')

   if get_product:
       product= Product.objects.get(pr_name__icontains=get_product)
       return redirect(f'/product/{product.id}')
   else:
       return redirect('/')

class Search(ListView):

    template_name = 'result.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(pr_name__icontains=self.request.GET.get('search_product'))
    def get_context_data(self, *, object_list=None, **kwargs):
        context= super().get_context_data(**kwargs)
        context['search_product'] = self.request.GET.get('search_product')
        context['count'] =[len(context['object_list'])]

        return context


class Register(View):
        template_name ='registration/register.html'
        def get(self,request):
            context={'form':RegisterForm}
            return render(request,self.template_name,context)
        def post(self,request):
            form = RegisterForm(request.POST)

            if form.is_valid():
                username = form.clean_username()
                password2 =form.cleaned_data.get('password2')
                email=form.cleaned_data.get('email')
                user= User.objects.create_user(username=username,password=password2,email=email)
                user.save()
                login(request,user)
                return redirect('/')
            context={'form':RegisterForm}
            return render(request, self.template_name,context)


def logout_view(request):
    logout(request)
    return redirect('/')


def to_cart(request, pk):
    if request.method=='POST':
        product =Product.objects.get(id=pk)
        if product.pr_count >=  int(request.POST.get('pr_quantity')):
            Cart.objects.create(user_id=request.user.id,
                                user_product=product,
                                user_product_quantity=int(request.POST.get('pr_quantity'))).save()

        return redirect('/')



def cart(request):
    user_cart = Cart.objects.filter(user_id=request.user.id)
    pr_id = [i.user_product.id for i in user_cart]
    pr_prices = [e.user_product.pr_price for e in user_cart]
    user_pr_amount = [c.user_product.pr_count for c in user_cart]
    pr_amount = [a.user_product.pr_count for a in user_cart]
    total=0
    text = (f'noviy zakaz \n\n' f'klient: {User.objects.get(id=request.user.id).username}\n')

    for p in range(len(pr_prices)):
        total += user_pr_amount[p] * pr_prices[p]

    if  request.method == 'POST':
        for i in user_cart:
            text += (f'Товар:{i.user_product}\n'
                     f'Количество: {i.user_product_quantity}')
            text += f'Итог: UZS{round(total,2)}'
            bot.send_message(admin_id,text )
            for u in range(len(pr_prices)):
                product = Product.objects.get(id=pr_id[u])
                product.pr_count = pr_amount[u] - user_pr_amount[u]
                product.save(update_fields=['pr_count'])
            user_cart.delete()
            return redirect('/')
    context ={'cart':user_cart , 'total' :round(total,2)}
    return render(request,'cart.html', context)

def    del_from_cart(request , pk):
    product_to_delete= Product.objects.get(id=pk)
    Cart.objects.filter(user_product=product_to_delete,user_id=request.user.id).delete()


    return redirect('/')