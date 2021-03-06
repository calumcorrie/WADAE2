import os
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE','treebay_django_project.settings')

import django
django.setup()

from treebay.models import Category, Plant, UserProfile
from django.contrib.auth.models import User
from django.core.files import File


def populate():
    # all plants
    plants = pd.read_excel("treebay_testing_data/plants.xlsx", index_col=0)
    plants['categories'] = plants.categories.apply(lambda x: x.split(', '))
    # all users
    users = pd.read_excel("treebay_testing_data/users.xlsx", index_col=0).to_dict("index")

    # add plants to users
    for username in plants.index.unique():
        users[username]['plants'] = plants.loc[plants.index == username].to_dict(orient='records')

    # all categories
    categories = pd.read_excel("treebay_testing_data/categories.xlsx", index_col=0).to_dict("index")

    for user in users:
        if type(users[user]["starred"]) is str:
            users[user]["starred"] = users[user]["starred"].split(", ")
        else:
            users[user]["starred"] = []

    # clear all users except for staff
    delete_users()
    # clear categories and plants
    delete_categories()
    delete_plants()

    # Add categories to DB
    for cat, cat_data in categories.items():
        add_cat(cat, cat_data['description'])

    # Add users to DB
    for username, user_data in users.items():
        user = add_user(username, user_data['email'], user_data['password'])

        user_profile = add_user_profile(user)
        user_profile.save()

        if 'plants' in user_data.keys():
            for plant_data in user_data['plants']:
                add_plant(user_profile, plant_data['name'], plant_data['description'], plant_data['location'],
                          plant_data['categories'], plant_data['views'], plant_data['price'])
                
    # add favorite plants to user
    for username, user_data in users.items():
        if 'starred' in user_data.keys():
            user = User.objects.get_or_create(username=username, email=user_data['email'])[0]
            user_profile = UserProfile.objects.get_or_create(user_id=user.id)[0]
            for starred_plant in user_data['starred']:
                user_profile.starred.add(Plant.objects.get_or_create(name=starred_plant)[0])


def add_user(username, email, password):
    user = User.objects.get_or_create(username=username, email=email)[0]
    user.set_password(password)
    user.save()
    return user


def add_user_profile(user):
    user_profile = UserProfile.objects.get_or_create(user_id=user.id)[0]
    user_profile.picture.save(user_profile.user.username + str(user_profile.id) + ".jpg",
                              File(open('./static/img/profile_pictures/' + user_profile.user.username + '.jpg', 'rb')))
    user_profile.save()
    return user_profile


def add_cat(name, description):
    c = Category.objects.get_or_create(name=name, description=description)[0]
    c.save()
    return c


def add_plant(owner, name, description, location, categories, views, price=0.0):
    p = Plant.objects.get_or_create(owner=owner, name=name, description=description, price=price, location=location, views=views)[0]
    p.categories.add(*Category.objects.filter(name__in=categories))
    p.picture.save(p.slug + str(p.id) + ".jpg",
                              File(open('./static/img/plants/' + p.slug + '.jpg', 'rb')))
    p.save()
    return p


def delete_users():
    for user_profile in UserProfile.objects.all():
        if not user_profile.user.is_staff:
            user_profile.delete()

    for user in User.objects.all():
        if not user.is_staff:
            user.delete()


def delete_categories():
    for cat in Category.objects.all():
        cat.delete()


def delete_plants():
    for plant in Plant.objects.all():
        plant.delete()


# Start execution here
if __name__ == '__main__':
    print('Starting Treebay population script...')
    populate()
    print('Done')
