from django.shortcuts import render,redirect
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm
from .models import UpcomingMovie
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import requests
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q


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
    
def select_rooms(predicted_entries):
    """Sélectionnez les salles appropriées en fonction des entrées prévues."""
    salles = {
        "Salle 1": 140,
        "Salle 2": 100,
        "Salle 3": 80,
        "Salle 4": 80
    }

    if predicted_entries < 0.2 * min(salles.values()):
        return ["Pas rentable"]

    recommended_salles = []
    while predicted_entries > 0:
        # Trouver la salle avec la capacité la plus proche de la capacité prévue qui est aussi supérieure ou égale à ces entrées
        best_fit_salle = min(salles.keys(), key=lambda k: (salles[k] - predicted_entries) if (salles[k] >= predicted_entries and k not in recommended_salles) else float('inf'))

        if salles[best_fit_salle] < 0.2 * predicted_entries:
            break

        recommended_salles.append(best_fit_salle)
        predicted_entries -= salles[best_fit_salle]

        if predicted_entries > 0 and predicted_entries < 0.2 * min([s for name, s in salles.items() if name not in recommended_salles]):
            break

    return recommended_salles if recommended_salles else ["Pas rentable"]


@login_required  
def films_avec_predictions(request):
    API_KEY = "a6275c028adf4e9bc5ae5f67edfb4c5f"
    URL = f"https://api.themoviedb.org/3/movie/upcoming?api_key={API_KEY}&region=FR&language=fr-FR"

    response = requests.get(URL)
    movies = response.json()['results']

    today = date.today()
    week_end = today + timedelta(days=7)
    movies_this_week = [movie for movie in movies if today <= date.fromisoformat(movie['release_date']) <= week_end]

    movies_to_display = []
    for movie in movies_this_week:
        details_url = f"https://api.themoviedb.org/3/movie/{movie['id']}?api_key={API_KEY}"
        credits_url = f"https://api.themoviedb.org/3/movie/{movie['id']}/credits?api_key={API_KEY}"

        movie_details = requests.get(details_url).json()
        credits = requests.get(credits_url).json()

        if movie_details['budget'] >= 0:
            existing_movie = UpcomingMovie.objects.filter(titre_non_modifie=movie['original_title']).first()

            if not existing_movie:
                upcoming_movie = UpcomingMovie.from_tmdb_data(movie, movie_details, credits)
                upcoming_movie.predict_entries()
                upcoming_movie.save()
            else:
                upcoming_movie = existing_movie
            
            predicted_local_entries = upcoming_movie.get_predicted_local_entries()
            room_to_open = select_rooms(predicted_local_entries)

            upcoming_movie.predicted_local_entries = predicted_local_entries
            upcoming_movie.room_to_open = room_to_open
            movies_to_display.append(upcoming_movie)

    return render(request, "prediction.html", {"movies": movies_to_display})


@login_required
def historique(request, year=None, month=None, day=None):
    search_query = request.GET.get('search')

    if request.GET.get('selected_date'):
        selected_date = request.GET.get('selected_date').split('-')
        year, month, day = map(int, selected_date)

    movies_for_week = UpcomingMovie.objects.all()

    if search_query:
        movies_for_week = movies_for_week.filter(
            Q(titre_fr__icontains=search_query) |
            Q(acteurs__icontains=search_query) |
            Q(genres__icontains=search_query) |
            Q(realisateur__icontains=search_query) 
            )

    if year and month and day:
        movies_for_week = movies_for_week.filter(date_sortie__year=year, date_sortie__month=month, date_sortie__day=day)

    context = {
        'movies': movies_for_week,
        'now': datetime.now(),
    }

    return render(request, 'historique.html', context)

