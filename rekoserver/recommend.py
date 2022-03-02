import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from rekoserver.models import Movies, People


def db_to_df(user=None):
    print('loading df...')
    global movies_df
    pd.set_option('display.max_columns', None)

    if not user:
        df = pd.DataFrame.from_records(Movies.objects.all().values(
            'id', 'original_title', 'genres', 'keywords', 'credits'))
    else:
        df = pd.DataFrame.from_records(Movies.objects.filter(watched__user=user).values(
            'id', 'original_title', 'genres', 'keywords', 'credits'))
        if df.empty:
            return pd.DataFrame()

    df = df[df['keywords'].map(lambda d: len(d)) > 0]

    df['cast'] = [pd.DataFrame.from_records(People.objects.filter(id__in=row, role='Acting').
                                            values('name')).to_dict('records')
                  for row in df['credits']]
    df['director'] = [pd.DataFrame.from_records(People.objects.filter(id__in=row, role='Directing').
                                                values('name')).to_dict('records')
                      for row in df['credits']]
    df = df[df['director'].map(lambda d: len(d)) > 0]

    features = ['cast', 'keywords', 'genres', 'director']
    for feature in features:
        df[feature] = df[feature].apply(get_list)

    for feature in features:
        df[feature] = df[feature].apply(clean_data)

    df['soup'] = df.apply(create_soup, axis=1)

    if not user:
        save_feather(df)
        movies_df = df

    return df


def save_feather(df):
    print('saving df to file...')
    df.reset_index(drop=True, inplace=True)
    df.to_feather('df.ftr')


def load_feather():
    print('loading df from file...')
    df = pd.read_feather('df.ftr')
    df.reset_index(inplace=True)

    return df


def get_list(x):
    if isinstance(x, list):
        if x and isinstance(x[0], dict):
            names = [i["name"] for i in x]
        else:
            names = x
        if len(names) > 3:
            names = names[:3]
        return names
    return []


def clean_data(row):
    if isinstance(row, list):
        return [str.lower(i.replace(' ', '').replace(',', '')) for i in row]
    else:
        if isinstance(row, str):
            return [str.lower(row.replace(' ', '').replace(',', ''))]
        else:
            return ""


def create_soup(features):
    return ' '.join(features['keywords']) + ' ' + ' '.join(features['cast']) \
           + ' ' + ' '.join(features['director']) + ' ' + ' '.join(features['genres'])


def get_similarity():
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['soup'])

    indices = pd.Series(movies_df.index, index=movies_df['id']).drop_duplicates()
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    return indices, cosine_sim


def get_recommendations(title, indices, cosine_sim):
    index = indices[title]
    similarity_scores = pd.DataFrame(cosine_sim[index], columns=['score'])
    similarity_scores = similarity_scores.sort_values('score', ascending=False)[1:11]
    movies_indices = similarity_scores.index

    movies = pd.DataFrame(movies_df['id'][movies_indices], columns=['id'])
    movies = pd.concat([movies, similarity_scores], axis=1, join='inner')
    print(movies)

    return movies


def calculate_score(x):
    if len(x) > 1:
        return x + 0.1*sum(x)
    else:
        return x


def user_recommendations(user):
    user_df = db_to_df(user)
    if user_df.empty:
        return pd.DataFrame()

    indices, sim = get_similarity()
    result = [get_recommendations(x, indices, sim) for x in user_df['id']]
    result = pd.concat(result).sort_values('score', ascending=False)
    dup = result['id'].isin(user_df['id'])
    result.drop(result[dup].index, inplace=True)
    result['calculated_score'] = result.groupby(['id'])['score'].transform(calculate_score)
    result.drop_duplicates(subset=['id'], inplace=True)
    result.sort_values('calculated_score', ascending=False, inplace=True)

    return result[:10]


movies_df = load_feather()
pd.set_option('display.max_colwidth', None)
