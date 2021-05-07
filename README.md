README
======

re: https://code.djangoproject.com/ticket/32718

This repo is a carveout of my main work django project, to demonstrate how i use django ImageFields in production.
I take images from the default storage, from user input, and from /tmp/, and save them all to the default storage using upload_to functions to put them in the right place.

To get running, clone the project, set up a venv (i'm using python 3.6.12), and get runserver running with one of these:

```bash
$ pip install pillow django==2.2.19; rm -rf db.sqlite3 storage/ento/report-maps/*; ./manage.py migrate; ./manage.py runserver
$ pip install pillow django==2.2.20; rm -rf db.sqlite3 storage/ento/report-maps/*; ./manage.py migrate; ./manage.py runserver
$ pip install pillow django==2.2.21; rm -rf db.sqlite3 storage/ento/report-maps/*; ./manage.py migrate; ./manage.py runserver
$ pip install pillow django==2.2.22; rm -rf db.sqlite3 storage/ento/report-maps/*; ./manage.py migrate; ./manage.py runserver
```

Then visit localhost:8000 in your browser to run the view in app/views.py. the view should create 6 pngs in `storage/ento/report-maps/`.

the main change I am trying to demonstrate is that staring with django 2.2.21,
`SuspiciousFileOperation("File name '/home/phillip/upload_repro/storage/ento/field-maps/field_a.png' includes path elements")` is raised,
unless you uncomment lines `:60` and `:91` in app/models.py.

I am not opposed to changing my code when security updates come out, but the [CVE](https://www.djangoproject.com/weblog/2021/may/04/security-releases/)
only mentioned 'empty file names and paths with dot segments',
not anything about slashes.

Honestly this just seems like a bug: applying [kukosk's patch](https://github.com/django/django/pull/14354/files) to my django install also brought things back to normal, _without having to add lines 60 and 91_.
However, I don't use upload_to strings in my project, just upload_to functions, so i don't know how to account for those users.

here's the stack trace copied from the web ui:

```
Environment:


Request Method: GET
Request URL: http://127.0.0.1:8000/

Django Version: 2.2.21
Python Version: 3.6.12
Installed Applications:
['django.contrib.admin',
 'django.contrib.auth',
 'django.contrib.contenttypes',
 'django.contrib.sessions',
 'django.contrib.messages',
 'django.contrib.staticfiles',
 'app']
Installed Middleware:
['django.middleware.security.SecurityMiddleware',
 'django.contrib.sessions.middleware.SessionMiddleware',
 'django.middleware.common.CommonMiddleware',
 'django.middleware.csrf.CsrfViewMiddleware',
 'django.contrib.auth.middleware.AuthenticationMiddleware',
 'django.contrib.messages.middleware.MessageMiddleware',
 'django.middleware.clickjacking.XFrameOptionsMiddleware']



Traceback:

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/core/handlers/exception.py" in inner
  34.             response = get_response(request)

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/core/handlers/base.py" in _get_response
  115.                 response = self.process_exception_by_middleware(e, request)

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/core/handlers/base.py" in _get_response
  113.                 response = wrapped_callback(request, *callback_args, **callback_kwargs)

File "/home/phillip/upload_repro/app/views.py" in view
  18.     fieldmap_a.save()

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/db/models/base.py" in save
  744.                        force_update=force_update, update_fields=update_fields)

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/db/models/base.py" in save_base
  782.                 force_update, using, update_fields,

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/db/models/base.py" in _save_table
  851.                       for f in non_pks]

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/db/models/base.py" in <listcomp>
  851.                       for f in non_pks]

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/db/models/fields/files.py" in pre_save
  289.             file.save(file.name, file.file, save=False)

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/db/models/fields/files.py" in save
  87.         name = self.field.generate_filename(self.instance, name)

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/db/models/fields/files.py" in generate_filename
  303.         filename = validate_file_name(filename)

File "/home/phillip/.pyenv/versions/3.6.12/envs/upload_repro/lib/python3.6/site-packages/django/core/files/utils.py" in validate_file_name
  8.         raise SuspiciousFileOperation("File name '%s' includes path elements" % name)

Exception Type: SuspiciousFileOperation at /
Exception Value: File name '/home/phillip/upload_repro/storage/ento/field-maps/field_a.png' includes path elements
```
