from django.shortcuts import render,redirect
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login



def home(request):
    return render(request, 'home.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'


class CustomLogoutView(LogoutView):
    template_name = 'logout.html'


def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'inscription.html', {'form': form})
    

def prediction(request):
    return render(request, 'prediction.html')

def historique(request):
    return render(request, 'historique.html')



from django.shortcuts import render
import csv
from datetime import datetime

def films_par_mois_annee(request):
    if request.method == 'POST':
        selected_month = int(request.POST.get('mois'))
        selected_year = int(request.POST.get('annee'))

        selected_month_year = datetime(selected_year, selected_month, 1)

        csv_file_path = "/home/apprenant/Documents/DEV_IA/Predictif_des_Entrees_de_Films/data/films_entree.csv"

        filtered_films = []

        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                film_date = datetime.strptime(row['date'], "%Y-%m-%d")
                if film_date.month == selected_month_year.month and film_date.year == selected_month_year.year:
                    filtered_films.append({
                        'titre_fr': row['title'],
                        'entries': row['entries'],
                        'date_sortie': film_date.strftime("%Y-%m-%d")
                    })

        context = {
            'films': filtered_films,
            'selected_month': selected_month,
            'selected_year': selected_year,
        }
        return render(request, 'films_par_mois_annee.html', context)

    return render(request, 'films_par_mois_annee.html')
