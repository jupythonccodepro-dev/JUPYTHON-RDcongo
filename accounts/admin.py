from django.contrib import admin
from .models import User

# Enregistrer le modèle utilisateur personnalisé pour l’afficher dans l’administration Django.
admin.site.register(User)
