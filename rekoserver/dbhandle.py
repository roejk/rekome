from pandas import read_csv
from tmdbv3api.exceptions import TMDbException
from tqdm import tqdm

from .models import Movies, People, Watched
from .movieapi import m_api
from .recommend import db_to_df


def add_to_list(request):
    m_id = request.POST.get('m_id')
    if not Movies.objects.filter(id=m_id):
        credits_ids = add_people_to_db(m_id)
        add_movie_to_db(m_id, credits_ids)
        db_to_df()
    context = add_watched_to_db(m_id, request)

    return context


def add_people_to_db(m_id):
    try:
        new_credits = m_api.movie.credits(m_id)
    except TMDbException:
        return -1
    credits_list = list(new_credits['cast'][:5])
    for person in new_credits['crew']:
        if person['job'] == 'Director':
            credits_list.append(person)
            break

    credits_ids = []
    for person in credits_list:
        if not People.objects.filter(id=person['id']):
            if not hasattr(person, 'job'):
                role = 'Acting'
            else:
                role = 'Directing'
            people_entry = People(id=person['id'], name=person['name'], role=role)
            people_entry.save()
        credits_ids.append(person['id'])

    return credits_ids


def add_movie_to_db(m_id, credits_ids):
    new_movie = m_api.movie.details(m_id)
    if new_movie['release_date'] != '':
        genres = [g for g in [new_movie['genres'][it]['name'] for it in range(len(new_movie['genres']))]]
        new_keywords = m_api.movie.keywords(m_id)
        keywords = [k for k in [new_keywords['keywords'][it]['name'] for it in range(len(new_keywords['keywords']))]]
        movies_entry = Movies(id=m_id, imdb_id=new_movie['imdb_id'],
                              title=new_movie['title'], original_title=new_movie['original_title'],
                              poster_path=new_movie['poster_path'], backdrop_path=new_movie['backdrop_path'],
                              release_date=new_movie['release_date'][:4], genres=genres,
                              keywords=keywords, credits=credits_ids)
        movies_entry.save()


def add_watched_to_db(m_id, request):
    rating = request.POST.get('rating')
    watched_movie = Movies.objects.filter(id=m_id)[0]
    if not Watched.objects.filter(user=request.user, m_id=watched_movie):
        watched_entry = Watched(user=request.user, m_id=watched_movie, rating=rating)
        watched_entry.save()
        msg = "Dodano \"" + watched_movie.title + "\" do listy obejrzanych filmów z oceną " + rating
    else:
        msg = "Ten film już znajduje się na liście"
    context = {'msg': msg}

    return context


# def csv_import():
#     movies = read_csv('update.txt', sep='\n', header=None, names=['id'])
#     movie_ids = movies['id'].tolist()
#     for movie in tqdm(movie_ids):
#         if not Movies.objects.filter(id=movie):
#             credits_ids = add_people_to_db(movie)
#             if credits_ids != -1:
#                 add_movie_to_db(movie, credits_ids)
