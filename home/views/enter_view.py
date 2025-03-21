from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import View, DetailView
from home.forms import LoginForm, EditProfileForm, RegisterForm
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from home.models import UserProfile, User
from django.contrib.auth.models import Group

free_group = Group.objects.get(name='Free')

@login_required(login_url='home:login')
def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home:login')

class Login(View):
    template_name = 'autentication/login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')

        form = self.form_class()
        return render(request, self.template_name, context={'form': form, 'site_title': 'Login - '})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = authenticate(
                request=request,
                username=form.cleaned_data['user'],
                password=form.cleaned_data['password'],
            )

            if user is not None:
                login(request, user)
                messages.success(request, 'Logado com sucesso!')
                return redirect('home:home')
            
        messages.error(request, 'O login falhou. [601]')
        return render(request, self.template_name, context={'form': form})
    
class Register(View):
    template_name = 'autentication/cadastro.html'
    form_class = RegisterForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, context={'form': form, 'site_title': 'Cadastro - '})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=User())

        if form.is_valid():
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']

            form_register = form.save(commit=False)
            form_register.username = user
            form_register.set_password(password)

            form_register.save()

            form_register.groups.add(free_group) # this need stay here, because the user is created before this line

            messages.success(request, 'Cadastro realizado com sucesso.')
            user = authenticate(
                request=request,
                username=form.cleaned_data['user'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
            return redirect('home:home')
            
        messages.error(request, 'O login falhou. [601]')
        return render(request, self.template_name, context={'form': form})

@login_required(login_url='home:login')
def view_profile(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'Você não está autenticado. [605]')
        return redirect('home:home')
    
    if not UserProfile.objects.filter(user=pk).exists():
        profile = User.objects.get(pk=pk)

        if profile.pk != request.user.pk:
            return redirect('home:view_profile', request.user.pk)
        
        return render(request, 'autentication/view_profile_free.html', context={'site_title': 'Ver Perfil - ', 'profile': profile, 'plann': profile.groups.first()})
    
    profile = get_object_or_404(UserProfile, user=pk)
    if profile.user.pk != request.user.pk:
        return redirect('home:view_profile', request.user.pk)

    return render(request, 'autentication/view_profile.html', context={'site_title': 'Ver Perfil - ', 'profile': profile, 'plann': profile.user.groups.first()})

class EditProfile(DetailView):
    template_name = 'autentication/edit.html'
    form_class = EditProfileForm
    model = User

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Você não está autenticado. [605]')
            return redirect('home:home')
        
        profile = get_object_or_404(User, pk=self.kwargs['pk'])
        if profile.pk != request.user.pk:
            return redirect('home:edit_profile', request.user.pk)
        
        form = self.form_class(instance=profile)

        return render(request, self.template_name, context={'form': form, 'site_title': 'Editar Perfil - ', 'profile': profile})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            profile = User.objects.get(pk=self.kwargs['pk'])
            profile.first_name=form.cleaned_data['first_name']
            profile.last_name=form.cleaned_data['last_name']
            profile.email=form.cleaned_data['email']
            profile.save()

            messages.success(request, 'Dados editados com sucesso.')
            return redirect('home:view_profile', request.user.pk)
            
        messages.error(request, 'Dados inválidos. [606]')
        return render(request, self.template_name, context={'form': form})