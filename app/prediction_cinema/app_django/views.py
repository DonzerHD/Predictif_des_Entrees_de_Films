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
    """
    Gère l'inscription d'un nouvel utilisateur.

    Si la méthode de la requête est POST, cette fonction traitera le formulaire d'inscription.
    Si le formulaire est valide, il enregistrera le nouvel utilisateur, l'authentifiera
    et le redirigera vers la page d'accueil. Si le formulaire n'est pas valide, il affichera
    à nouveau le formulaire avec les erreurs.

    Si la méthode de la requête n'est pas POST (par exemple, GET), elle affichera simplement
    le formulaire d'inscription.

    Args:
        request (HttpRequest): Requête HTTP envoyée au serveur.

    Returns:
        HttpResponse: Réponse HTTP contenant le formulaire d'inscription ou une redirection vers la page d'accueil.
    """
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
    """
    Sélectionne les salles optimales en fonction du nombre d'entrées prévues.

    Détermine quelles salles ouvrir en fonction du nombre prévu.
    Si l'ouverture d'une salle ne permet pas d'atteindre une capacité minimale
    de 20%, elle n'est pas considérée comme rentable et n'est donc pas recommandée.

    Args:
        predicted_entries (int): Nombre d'entrées prévu.

    Returns:
        str: Noms des salles recommandées séparés par "et" si elles sont rentables, 
        sinon retourne un message indiquant que ce n'est pas rentable.
    """
    salles = {
        "Salle 1": 140,
        "Salle 2": 100,
        "Salle 3": 80,
        "Salle 4": 80
    }

    if predicted_entries < 0.2 * min(salles.values()):
        return "Aucune, pas assez rentable"

    recommended_salles = []
    while predicted_entries > 0:
        best_fit_salle = min(salles.keys(), key=lambda k: (salles[k] - predicted_entries) if (salles[k] >= predicted_entries and k not in recommended_salles) else float('inf'))

        if salles[best_fit_salle] < 0.2 * predicted_entries:
            break

        recommended_salles.append(best_fit_salle)
        predicted_entries -= salles[best_fit_salle]

        if predicted_entries > 0 and predicted_entries < 0.2 * min([s for name, s in salles.items() if name not in recommended_salles]):
            break

    if recommended_salles:
        return ' et '.join(recommended_salles)
    else:
        return "Aucune, pas assez rentable"



@login_required  
def films_avec_predictions(request):
    """
    Récupère la liste des films à venir pour la semaine et prédit les entrées locales.
    
    Utilise l'API TMDB pour obtenir des détails sur les films à venir. 
    Les films sont ensuite filtrés pour ne conserver que ceux qui sortent dans la semaine actuelle. 
    Si un film n'est pas encore dans la base de données, 
    il est ajouté et une prédiction est réalisée pour estimer les entrées en première semaine. 
    Une salle est également recommandée en fonction de cette prédiction.

    Args:
        request (HttpRequest): L'objet de requête HTTP.

    Returns:
        HttpResponse: La réponse HTML pour la page de prédiction, avec les films et leurs détails.
    """
    
    today = date.today()
    week_end = today + timedelta(days=14)
    
    # Récupération des films de la base de données
    movies_from_db = UpcomingMovie.objects.filter(date_sortie__range=[today, week_end])
    movies_to_display = []

    for movie in movies_from_db:
        predicted_local_entries = movie.get_predicted_local_entries()
        room_to_open = select_rooms(predicted_local_entries)
        movie.predicted_local_entries = predicted_local_entries
        movie.room_to_open = room_to_open
        movies_to_display.append(movie)
    
    # Si aucun film n'est trouvé dans la base de données pour la semaine à venir, requêtez l'API TMDB
    if not movies_to_display:
        API_KEY = "a6275c028adf4e9bc5ae5f67edfb4c5f"
        URL = f"https://api.themoviedb.org/3/movie/upcoming?api_key={API_KEY}&region=FR&language=fr-FR"
        response = requests.get(URL)
        movies = response.json()['results']
        movies_this_week = [movie for movie in movies if today <= date.fromisoformat(movie['release_date']) <= week_end]

        for movie in movies_this_week:
            details_url = f"https://api.themoviedb.org/3/movie/{movie['id']}?api_key={API_KEY}"
            credits_url = f"https://api.themoviedb.org/3/movie/{movie['id']}/credits?api_key={API_KEY}"

            movie_details = requests.get(details_url).json()
            credits = requests.get(credits_url).json()

            upcoming_movie = UpcomingMovie.from_tmdb_data(movie, movie_details, credits)
            upcoming_movie.predict_entries()

            if not UpcomingMovie.objects.filter(titre_non_modifie=movie['original_title']).exists():
                upcoming_movie.save()

            predicted_local_entries = upcoming_movie.get_predicted_local_entries()
            room_to_open = select_rooms(predicted_local_entries)

            upcoming_movie.predicted_local_entries = predicted_local_entries
            upcoming_movie.room_to_open = room_to_open
            movies_to_display.append(upcoming_movie)

    return render(request, "prediction.html", {"movies": movies_to_display})


@login_required
def historique(request, year=None, month=None, day=None):
    """
    Affiche une liste de films basée sur des critères de recherche et une date spécifique.
    
    Les utilisateurs peuvent rechercher des films par titre, acteurs, genres ou réalisateur. 
    De plus, ils peuvent filtrer les films selon une date de sortie spécifique.
    Si aucune date n'est spécifiée, tous les films de la base de données sont affichés.
    
    Args:
        request (HttpRequest): L'objet de requête HTTP.
        year (int, optional): L'année de sortie du film à filtrer. Par défaut à None.
        month (int, optional): Le mois de sortie du film à filtrer. Par défaut à None.
        day (int, optional): Le jour de sortie du film à filtrer. Par défaut à None.

    Returns:
        HttpResponse: La réponse HTML pour la page historique, contenant les films correspondants aux critères.
    """
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

