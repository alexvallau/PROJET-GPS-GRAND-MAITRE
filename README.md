# Application de Cartographie de Routes et de Bornes de Recharge

Ce projet est une application web développée avec Flask et Folium permettant de visualiser des itinéraires de conduite et de localiser des bornes de recharge pour véhicules électriques. L’application intègre des services de géolocalisation, de cartographie et l’API OpenRouteService pour fournir un itinéraire optimisé avec des détours vers des bornes de recharge en fonction de l'autonomie du véhicule.

## Fonctionnalités Principales

1. **Calcul d'Itinéraire** :
   - Les utilisateurs peuvent saisir deux villes pour générer un itinéraire de conduite.
   - L'itinéraire est calculé à l'aide de l'API OpenRouteService, affichant la distance totale entre le point de départ et d'arrivée.

2. **Bornes de Recharge à Proximité** :
   - L'application identifie les bornes de recharge situées à proximité de l'itinéraire.
   - Elle prend en compte l’autonomie maximale du véhicule et insère des détours pour des arrêts de recharge lorsque nécessaire.

3. **Visualisation Intuitive avec Folium** :
   - L'itinéraire est affiché sur une carte interactive générée avec Folium.
   - Des marqueurs indiquent les villes de départ et d'arrivée ainsi que les bornes de recharge identifiées le long du parcours.

4. **Gestion des Erreurs de Géolocalisation** :
   - Si le service de géolocalisation est indisponible, l'utilisateur est invité à réessayer ultérieurement.

## Technologies Utilisées

- **Flask** : Pour la gestion des routes et du serveur web.
- **Folium** : Pour la création de cartes interactives.
- **OpenRouteService** : Pour le calcul des itinéraires.
- **Geopy** : Pour la géolocalisation des villes.

## Lancer l'Application

Pour lancer l'application, exécutez la commande suivante :

```bash
python app.py
```

