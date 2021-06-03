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
    print(current_url)
    mendeley_session = auth.authenticate(current_url)

    request.session['token'] = mendeley_session.token

    return redirect('/listDocuments')

def list_documents(request):
    if 'token' not in request.session:
        return redirect('/')

    # print(dict(request.session))
    # utils.get_data(request.session["token"]['access_token'])
    #
    headers = {"Authorization": "Bearer "+request.session["token"]['access_token']}
    print(requests.get('https://api.mendeley.com/search/catalog?query=aerobiology&limit=25&view=all&open_access=True', headers=headers).json()[-1])

    return render(request,'api/library.html', {"name":name, "docs":docs})


def get_document(request):
    if 'token' not in request.session:
        return redirect('/')

    mendeley_session = MendeleySession(mendeley, request.session['token'])

    document_id = request.GET['document_id']
    doc = mendeley_session.documents.get(document_id)

    return render(request,'metadata.html', doc=doc)
