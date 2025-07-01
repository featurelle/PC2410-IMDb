from django.test import TestCase
from faker import Faker

from .. import models
from .. import search


class SearchTestCase(TestCase):
    def setUp(self):
        fake = Faker()

        self.search_query_both = 'ooooooooo'
        self.search_query_none = '00001111'

        # Create mock directors with random first and last names
        names = [{'first': fake.unique.first_name(), 'last': fake.unique.last_name()} for _ in range(5)]
        self.mock_directors = [
            models.Director.objects.create(
                first=name['first'],
                last=name['last'],
                slug=name['first'] + name['last']
            )
            for name in names
        ]
        self.mock_directors.append(
            models.Director.objects.create(
                first=self.search_query_both,
                last=self.search_query_both,
                slug=self.search_query_both
            )
        )

        # Create mock movies with random titles
        titles = [fake.unique.catch_phrase() for _ in range(5)]
        self.mock_movies = [
            models.Movie.objects.create(
                title=title,
                year=2015,
                slug=title + str(2015)
            )
            for title in titles
        ]
        self.mock_movies.append(
            models.Movie.objects.create(
                title=self.search_query_both,
                year=2015,
                slug=self.search_query_both + str(2015)
            )
        )

    def test_search_movies(self):
        query = self.search_query_none
        results = search.search_movies(query)['movies']
        self.assertIsNone(results)

        query = self.mock_movies[0].title
        results = search.search_movies(query)['movies']
        self.assertEqual(list(results), [self.mock_movies[0]])

    def test_search_directors(self):
        query = self.search_query_none
        results = search.search_directors(query)['directors']
        self.assertIsNone(results)

        query = self.mock_directors[0].fullname
        results = search.search_directors(query)['directors']
        self.assertEqual(list(results), [self.mock_directors[0]])

    def test_search_all(self):
        query = self.search_query_none
        results = search.search_all(query)
        self.assertIsNone(results['directors'])
        self.assertIsNone(results['movies'])

        query = self.mock_movies[0].title
        results = search.search_all(query)
        self.assertEqual(list(results['movies']), [self.mock_movies[0]])
        self.assertIsNone(results['directors'])

        query = str(self.mock_movies[0].year)
        results = search.search_all(query)
        self.assertEqual(list(results['movies']), self.mock_movies)
        self.assertIsNone(results['directors'])

        query = self.mock_directors[0].fullname
        results = search.search_all(query)
        self.assertEqual(list(results['directors']), [self.mock_directors[0]])
        self.assertIsNone(results['movies'])

        query = self.search_query_both
        results = search.search_all(query)
        self.assertEqual(list(results['directors']), [self.mock_directors[-1]])
        self.assertEqual(list(results['movies']), [self.mock_movies[-1]])

    def test_dispatch(self):
        with self.assertRaises(KeyError):
            search.dispatch("", "invalid_search_type")

        result = search.dispatch(self.search_query_both, "all")
        self.assertEqual(result['search_type'], 'all')
        self.assertIsNotNone(result['movies'])
        self.assertIsNotNone(result['directors'])

        result = search.dispatch(self.mock_movies[0].title, "movies")
        self.assertEqual(result['search_type'], 'movies')
        self.assertIsNotNone(result['movies'])
        self.assertIsNone(result['directors'])

        result = search.dispatch(self.mock_directors[0].last, "directors")
        self.assertEqual(result['search_type'], 'directors')
        self.assertIsNotNone(result['directors'])
        self.assertIsNone(result['movies'])

        result = search.dispatch("", "movies")
        self.assertEqual(result['search_type'], 'movies')
        self.assertIsNone(result['movies'])
        self.assertIsNone(result['directors'])
