from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.urls import resolve
import requests


# Create your views here.

from mendeley import Mendeley
from mendeley.session import MendeleySession

REDIRECT_URI = 'http://localhost:8000/oauth'


def index(request):
    mendeley = Mendeley(8198, 'Fi7j614Pw3e42Hjo')
    auth = mendeley.start_client_credentials_flow().authenticate()
    request.session['token'] = auth.token
    return redirect('listDocuments/')

def auth_return(request):
    auth = mendeley.start_authorization_code_flow(state=request.GET['state'])
    current_url = request.build_absolute_uri()
    mendeley_session = auth.authenticate(current_url)

    request.session['token'] = mendeley_session.token

    return redirect('/listDocuments')

def list_documents(request):
    if 'token' not in request.session:
        return redirect('/')

    headers = {"Authorization": "Bearer " + request.session['token']['access_token']}

    # Fetch the user profile to display the library owner's name.
    profile_res = requests.get("https://api.mendeley.com/profiles/me", headers=headers)
    if profile_res.ok:
        profile = profile_res.json()
        name = profile.get("display_name") or f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
    else:
        name = ""

    # Retrieve the list of documents in the user's library.
    docs_res = requests.get("https://api.mendeley.com/documents", headers=headers)
    docs = docs_res.json() if docs_res.ok else []

    return render(request, 'api/library.html', {"name": name, "docs": docs})


def get_document(request):
    if 'token' not in request.session:
        return redirect('/')

    mendeley_session = MendeleySession(mendeley, request.session['token'])

    document_id = request.GET['document_id']
    doc = mendeley_session.documents.get(document_id)

    return render(request,'metadata.html', doc=doc)
